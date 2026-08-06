from app.repositories.base_repository import BaseRepository


class OportunidadeRepository(BaseRepository):

    TABLE = "crm_oportunidades"

    @classmethod
    def total(cls, pesquisa=None, status=None, ativo=None):
        sql = f"""
            SELECT COUNT(*)
            FROM {cls.TABLE} o
            LEFT JOIN crm_leads l
                ON l.id = o.lead_id
            LEFT JOIN crm_contatos c
                ON c.id = o.contato_id
            LEFT JOIN clientes cli
                ON cli.id = o.cliente_id
            LEFT JOIN parceiros p
                ON p.id = o.parceiro_id
            LEFT JOIN parceiros_executivos pe
                ON pe.id = o.executivo_responsavel_id
            WHERE 1 = 1
        """
        params = []

        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                o.titulo LIKE %s
                OR COALESCE(o.empresa, '') LIKE %s
                OR COALESCE(o.erp, '') LIKE %s
                OR COALESCE(l.empresa, '') LIKE %s
                OR COALESCE(c.nome, '') LIKE %s
                OR COALESCE(cli.nome_fantasia, cli.razao_social, '') LIKE %s
                OR COALESCE(p.nome, '') LIKE %s
                OR COALESCE(pe.nome, '') LIKE %s
            )
            """
            params.extend([termo, termo, termo, termo, termo, termo, termo, termo])

        if status:
            sql += """
  AND o.status = %s"""
            params.append(status)

        if ativo in (0, 1):
            sql += """
  AND o.ativo = %s"""
            params.append(ativo)

        return cls.scalar(sql, tuple(params)) or 0

    @classmethod
    def listar(cls, pesquisa=None, status=None, ativo=None, limit=50, offset=0):
        sql = f"""
            SELECT
                o.id,
                o.uuid,
                o.lead_id,
                o.contato_id,
                o.cliente_id,
                o.parceiro_id,
                o.executivo_responsavel_id,
                o.titulo,
                o.empresa,
                o.erp,
                o.quantidade_usuarios,
                o.valor_estimado,
                o.probabilidade,
                o.status,
                o.ativo,
                o.created_at,
                o.updated_at,
                l.empresa AS lead_empresa,
                c.nome AS contato_nome,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_exibicao,
                COALESCE(p.nome_fantasia, p.nome, p.razao_social) AS parceiro_exibicao,
                pe.nome AS executivo_responsavel_nome
            FROM {cls.TABLE} o
            LEFT JOIN crm_leads l
                ON l.id = o.lead_id
            LEFT JOIN crm_contatos c
                ON c.id = o.contato_id
            LEFT JOIN clientes cli
                ON cli.id = o.cliente_id
            LEFT JOIN parceiros p
                ON p.id = o.parceiro_id
            LEFT JOIN parceiros_executivos pe
                ON pe.id = o.executivo_responsavel_id
            WHERE 1 = 1
        """
        params = []

        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                o.titulo LIKE %s
                OR COALESCE(o.empresa, '') LIKE %s
                OR COALESCE(o.erp, '') LIKE %s
                OR COALESCE(l.empresa, '') LIKE %s
                OR COALESCE(c.nome, '') LIKE %s
                OR COALESCE(cli.nome_fantasia, cli.razao_social, '') LIKE %s
                OR COALESCE(p.nome, '') LIKE %s
                OR COALESCE(pe.nome, '') LIKE %s
            )
            """
            params.extend([termo, termo, termo, termo, termo, termo, termo, termo])

        if status:
            sql += """
  AND o.status = %s"""
            params.append(status)

        if ativo in (0, 1):
            sql += """
  AND o.ativo = %s"""
            params.append(ativo)

        sql += """
            ORDER BY o.updated_at DESC, o.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def listar_todos_ativos(cls):
        sql = f"""
            SELECT
                id,
                cliente_id,
                contato_id,
                parceiro_id,
                executivo_responsavel_id,
                titulo,
                empresa,
                status,
                valor_estimado,
                quantidade_usuarios
            FROM {cls.TABLE}
            WHERE ativo = 1
            ORDER BY titulo
        """
        return cls.fetch_all(sql)

    @classmethod
    def listar_pipeline(cls, pesquisa=None):
        sql = f"""
            SELECT
                o.id,
                o.titulo,
                o.empresa,
                o.erp,
                o.quantidade_usuarios,
                o.valor_estimado,
                o.probabilidade,
                o.status,
                o.ativo,
                l.empresa AS lead_empresa,
                c.nome AS contato_nome,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_exibicao,
                COALESCE(p.nome_fantasia, p.nome, p.razao_social) AS parceiro_exibicao,
                pe.nome AS executivo_responsavel_nome
            FROM {cls.TABLE} o
            LEFT JOIN crm_leads l
                ON l.id = o.lead_id
            LEFT JOIN crm_contatos c
                ON c.id = o.contato_id
            LEFT JOIN clientes cli
                ON cli.id = o.cliente_id
            LEFT JOIN parceiros p
                ON p.id = o.parceiro_id
            LEFT JOIN parceiros_executivos pe
                ON pe.id = o.executivo_responsavel_id
            WHERE o.ativo = 1
        """
        params = []

        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                o.titulo LIKE %s
                OR COALESCE(o.empresa, '') LIKE %s
                OR COALESCE(o.erp, '') LIKE %s
                OR COALESCE(l.empresa, '') LIKE %s
                OR COALESCE(c.nome, '') LIKE %s
                OR COALESCE(cli.nome_fantasia, cli.razao_social, '') LIKE %s
                OR COALESCE(p.nome, '') LIKE %s
                OR COALESCE(pe.nome, '') LIKE %s
            )
            """
            params.extend([termo, termo, termo, termo, termo, termo, termo, termo])

        sql += """
            ORDER BY FIELD(o.status, 'NOVA', 'QUALIFICACAO', 'LEVANTAMENTO', 'DIMENSIONAMENTO', 'PRECIFICACAO', 'PROPOSTA', 'NEGOCIACAO', 'GANHA', 'PERDIDA'),
                     o.updated_at DESC,
                     o.id DESC
        """

        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def buscar_por_id(cls, oportunidade_id):
        sql = f"""
            SELECT
                o.id,
                o.uuid,
                o.lead_id,
                o.contato_id,
                o.cliente_id,
                o.parceiro_id,
                o.executivo_responsavel_id,
                o.titulo,
                o.empresa,
                o.erp,
                o.quantidade_usuarios,
                o.valor_estimado,
                o.probabilidade,
                o.status,
                o.observacoes,
                o.ativo,
                o.created_at,
                o.updated_at,
                l.empresa AS lead_empresa,
                c.nome AS contato_nome,
                COALESCE(cli.nome_fantasia, cli.razao_social) AS cliente_exibicao,
                COALESCE(p.nome_fantasia, p.nome, p.razao_social) AS parceiro_exibicao,
                pe.nome AS executivo_responsavel_nome
            FROM {cls.TABLE} o
            LEFT JOIN crm_leads l
                ON l.id = o.lead_id
            LEFT JOIN crm_contatos c
                ON c.id = o.contato_id
            LEFT JOIN clientes cli
                ON cli.id = o.cliente_id
            LEFT JOIN parceiros p
                ON p.id = o.parceiro_id
            LEFT JOIN parceiros_executivos pe
                ON pe.id = o.executivo_responsavel_id
            WHERE o.id = %s
        """
        return cls.fetch_one(sql, (oportunidade_id,))

    @classmethod
    def inserir(cls, dados):
        sql = f"""
            INSERT INTO {cls.TABLE}
            (
                uuid,
                lead_id,
                contato_id,
                cliente_id,
                parceiro_id,
                executivo_responsavel_id,
                titulo,
                empresa,
                erp,
                quantidade_usuarios,
                valor_estimado,
                probabilidade,
                status,
                observacoes,
                ativo
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        return cls.execute_insert(sql, (
            cls.generate_uuid(),
            dados.get('lead_id'),
            dados.get('contato_id'),
            dados.get('cliente_id'),
            dados.get('parceiro_id'),
            dados.get('executivo_responsavel_id'),
            dados['titulo'],
            dados.get('empresa'),
            dados.get('erp'),
            dados.get('quantidade_usuarios'),
            dados.get('valor_estimado'),
            dados.get('probabilidade'),
            dados['status'],
            dados.get('observacoes'),
            cls.bool_to_int(dados.get('ativo', True)),
        ))

    @classmethod
    def atualizar(cls, oportunidade_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET lead_id = %s,
                contato_id = %s,
                cliente_id = %s,
                parceiro_id = %s,
                executivo_responsavel_id = %s,
                titulo = %s,
                empresa = %s,
                erp = %s,
                quantidade_usuarios = %s,
                valor_estimado = %s,
                probabilidade = %s,
                status = %s,
                observacoes = %s,
                ativo = %s
            WHERE id = %s
        """
        return cls.execute(sql, (
            dados.get('lead_id'),
            dados.get('contato_id'),
            dados.get('cliente_id'),
            dados.get('parceiro_id'),
            dados.get('executivo_responsavel_id'),
            dados['titulo'],
            dados.get('empresa'),
            dados.get('erp'),
            dados.get('quantidade_usuarios'),
            dados.get('valor_estimado'),
            dados.get('probabilidade'),
            dados['status'],
            dados.get('observacoes'),
            cls.bool_to_int(dados.get('ativo', True)),
            oportunidade_id,
        ))

    @classmethod
    def excluir(cls, oportunidade_id):
        sql = f"DELETE FROM {cls.TABLE} WHERE id = %s"
        return cls.execute(sql, (oportunidade_id,))

    @classmethod
    def excluir_em_massa(cls, oportunidade_ids):
        ids = [int(item) for item in oportunidade_ids if str(item).isdigit()]
        if not ids:
            return 0
        marks = ",".join(["%s"] * len(ids))
        return cls.execute(f"DELETE FROM {cls.TABLE} WHERE id IN ({marks})", tuple(ids))
