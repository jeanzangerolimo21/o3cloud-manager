from app.repositories.base_repository import BaseRepository


class SucessoClienteRepository(BaseRepository):

    @classmethod
    def listar_contratos(cls, pesquisa=None, curva=None, status_relacionamento=None, limit=50, offset=0):
        where, params = cls._filtros(pesquisa, curva, status_relacionamento)
        sql = cls._select_base() + "\n" + where + """
            ORDER BY CASE relacionamento.status_relacionamento
                        WHEN 'CRITICO' THEN 0
                        WHEN 'REGULAR' THEN 1
                        WHEN 'BOM' THEN 2
                        WHEN 'OTIMO' THEN 3
                        ELSE 4
                     END,
                     COALESCE(c.valor_servicos_bruto, c.valor_mensal, 0) DESC,
                     cli.razao_social ASC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def total_contratos(cls, pesquisa=None, curva=None, status_relacionamento=None):
        where, params = cls._filtros(pesquisa, curva, status_relacionamento)
        row = cls.fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN crm_sucesso_cliente relacionamento ON relacionamento.contrato_id = c.id
            """ + where,
            tuple(params),
        )
        return row["total"] if row else 0

    @classmethod
    def dashboard(cls):
        return cls.fetch_one(
            """
            SELECT
                COUNT(*) AS total_contratos,
                SUM(CASE WHEN COALESCE(c.valor_servicos_bruto, c.valor_mensal, 0) >= 2999.99 THEN 1 ELSE 0 END) AS curva_a,
                SUM(CASE WHEN COALESCE(c.valor_servicos_bruto, c.valor_mensal, 0) >= 1000 AND COALESCE(c.valor_servicos_bruto, c.valor_mensal, 0) < 2999.99 THEN 1 ELSE 0 END) AS curva_b,
                SUM(CASE WHEN COALESCE(c.valor_servicos_bruto, c.valor_mensal, 0) < 1000 THEN 1 ELSE 0 END) AS curva_c,
                SUM(CASE WHEN relacionamento.status_relacionamento = 'CRITICO' THEN 1 ELSE 0 END) AS criticos
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN crm_sucesso_cliente relacionamento ON relacionamento.contrato_id = c.id
            WHERE c.ativo = 1 AND c.status = 'ATIVO'
            """
        )

    @classmethod
    def buscar_contrato(cls, contrato_id):
        return cls.fetch_one(cls._select_base() + "\nWHERE c.id = %s AND c.ativo = 1", (contrato_id,))

    @classmethod
    def buscar_relacionamento(cls, contrato_id):
        return cls.fetch_one(
            """
            SELECT r.*, ct.nome AS contato_nome, ct.email AS contato_email, ct.telefone AS contato_telefone, ct.whatsapp AS contato_whatsapp
            FROM crm_sucesso_cliente r
            LEFT JOIN crm_contatos ct ON ct.id = r.contato_id
            WHERE r.contrato_id = %s
            """,
            (contrato_id,),
        )

    @classmethod
    def salvar_relacionamento(cls, contrato_id, contato_id, status_relacionamento, usuario_email=None):
        return cls.execute_insert(
            """
            INSERT INTO crm_sucesso_cliente (uuid, contrato_id, contato_id, status_relacionamento, updated_by)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE contato_id=VALUES(contato_id), status_relacionamento=VALUES(status_relacionamento), updated_by=VALUES(updated_by)
            """,
            (cls.generate_uuid(), contrato_id, contato_id, status_relacionamento, usuario_email),
        )

    @classmethod
    def inserir_historico(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO crm_sucesso_cliente_historico (uuid, contrato_id, contato_id, status_relacionamento, comentario, autor_email)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(),
                dados.get("contrato_id"),
                dados.get("contato_id"),
                dados.get("status_relacionamento"),
                dados.get("comentario"),
                dados.get("autor_email"),
            ),
        )

    @classmethod
    def listar_historico(cls, contrato_id):
        return cls.fetch_all(
            """
            SELECT h.*, ct.nome AS contato_nome
            FROM crm_sucesso_cliente_historico h
            LEFT JOIN crm_contatos ct ON ct.id = h.contato_id
            WHERE h.contrato_id = %s
            ORDER BY h.created_at DESC, h.id DESC
            """,
            (contrato_id,),
        )

    @classmethod
    def inserir_anexo(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO crm_sucesso_cliente_historico_anexos (
                uuid, historico_id, contrato_id, arquivo_original, nome_arquivo, caminho, url, mime_type, tamanho
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(),
                dados.get("historico_id"),
                dados.get("contrato_id"),
                dados.get("arquivo_original"),
                dados.get("nome_arquivo"),
                dados.get("caminho"),
                dados.get("url"),
                dados.get("mime_type"),
                dados.get("tamanho"),
            ),
        )

    @classmethod
    def listar_anexos(cls, contrato_id):
        return cls.fetch_all(
            """
            SELECT *
            FROM crm_sucesso_cliente_historico_anexos
            WHERE contrato_id = %s
            ORDER BY id ASC
            """,
            (contrato_id,),
        )

    @classmethod
    def listar_contatos_cliente(cls, nomes_cliente=None):
        nomes = [nome for nome in (nomes_cliente or []) if nome]
        params = []
        where = "WHERE ativo = 1"
        if nomes:
            placeholders = ", ".join(["%s"] * len(nomes))
            where += f" AND empresa IN ({placeholders})"
            params.extend(nomes)
        return cls.fetch_all(
            f"""
            SELECT id, nome, empresa, cargo, email, telefone, whatsapp, tipo_contato
            FROM crm_contatos
            {where}
            ORDER BY nome ASC
            """,
            tuple(params),
        )

    @staticmethod
    def _select_base():
        return """
            SELECT
                c.id,
                c.numero,
                c.status,
                c.quantidade_usuarios,
                c.vendedor_nome,
                c.projeto_nome,
                c.valor_servicos_bruto,
                c.valor_mensal,
                c.observacao_contrato,
                c.observacoes,
                cli.id AS cliente_id,
                cli.razao_social AS cliente_razao_social,
                cli.nome_fantasia AS cliente_nome_fantasia,
                cli.cnpj AS cliente_cnpj,
                relacionamento.contato_id,
                relacionamento.status_relacionamento,
                contato.nome AS contato_nome,
                contato.email AS contato_email,
                contato.telefone AS contato_telefone,
                contato.whatsapp AS contato_whatsapp,
                ultimo.created_at AS ultimo_relacionamento_em
            FROM contratos c
            INNER JOIN clientes cli ON cli.id = c.cliente_id
            LEFT JOIN crm_sucesso_cliente relacionamento ON relacionamento.contrato_id = c.id
            LEFT JOIN crm_contatos contato ON contato.id = relacionamento.contato_id
            LEFT JOIN (
                SELECT contrato_id, MAX(created_at) AS created_at
                FROM crm_sucesso_cliente_historico
                GROUP BY contrato_id
            ) ultimo ON ultimo.contrato_id = c.id
        """

    @staticmethod
    def _filtros(pesquisa=None, curva=None, status_relacionamento=None):
        where = ["c.ativo = 1", "c.status = 'ATIVO'"]
        params = []
        if pesquisa:
            like = f"%{pesquisa}%"
            where.append("(cli.razao_social LIKE %s OR cli.nome_fantasia LIKE %s OR cli.cnpj LIKE %s OR c.numero LIKE %s OR c.vendedor_nome LIKE %s OR c.projeto_nome LIKE %s)")
            params.extend([like, like, like, like, like, like])
        if status_relacionamento:
            where.append("relacionamento.status_relacionamento = %s")
            params.append(status_relacionamento)
        valor = "COALESCE(c.valor_servicos_bruto, c.valor_mensal, 0)"
        if curva == "A":
            where.append(f"{valor} >= 2999.99")
        elif curva == "B":
            where.append(f"{valor} >= 1000 AND {valor} < 2999.99")
        elif curva == "C":
            where.append(f"{valor} < 1000")
        return "WHERE " + " AND ".join(where), params
