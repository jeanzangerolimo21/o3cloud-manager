from app.repositories.base_repository import BaseRepository


class ContatoRepository(BaseRepository):

    TABLE = "crm_contatos"

    @classmethod
    def total(cls, pesquisa=None, tipo_contato=None, ativo=None):
        sql = f"""
            SELECT COUNT(*)
            FROM {cls.TABLE} c
            LEFT JOIN crm_leads l
                ON l.id = c.lead_id
            LEFT JOIN parceiros p
                ON p.id = c.parceiro_id
            LEFT JOIN parceiros_executivos pe
                ON pe.id = c.executivo_responsavel_id
            WHERE 1 = 1
        """

        params = []

        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                c.nome LIKE %s
                OR COALESCE(c.empresa, '') LIKE %s
                OR COALESCE(c.email, '') LIKE %s
                OR COALESCE(c.telefone, '') LIKE %s
                OR COALESCE(c.whatsapp, '') LIKE %s
                OR COALESCE(l.empresa, '') LIKE %s
                OR COALESCE(p.nome, '') LIKE %s
                OR COALESCE(pe.nome, '') LIKE %s
            )
            """
            params.extend([termo, termo, termo, termo, termo, termo, termo, termo])

        if tipo_contato:
            sql += """
  AND c.tipo_contato = %s"""
            params.append(tipo_contato)

        if ativo in (0, 1):
            sql += """
  AND c.ativo = %s"""
            params.append(ativo)

        return cls.scalar(sql, tuple(params)) or 0

    @classmethod
    def listar(cls, pesquisa=None, tipo_contato=None, ativo=None, limit=50, offset=0):
        sql = f"""
            SELECT
                c.id,
                c.uuid,
                c.lead_id,
                c.parceiro_id,
                c.executivo_responsavel_id,
                c.empresa,
                c.nome,
                c.cargo,
                c.cpf,
                c.email,
                c.telefone,
                c.whatsapp,
                c.tipo_contato,
                c.canal_preferido,
                c.cidade,
                c.uf,
                c.ativo,
                c.created_at,
                c.updated_at,
                l.empresa AS lead_empresa,
                COALESCE(p.nome_fantasia, p.nome, p.razao_social) AS parceiro_exibicao,
                pe.nome AS executivo_responsavel_nome
            FROM {cls.TABLE} c
            LEFT JOIN crm_leads l
                ON l.id = c.lead_id
            LEFT JOIN parceiros p
                ON p.id = c.parceiro_id
            LEFT JOIN parceiros_executivos pe
                ON pe.id = c.executivo_responsavel_id
            WHERE 1 = 1
        """

        params = []

        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                c.nome LIKE %s
                OR COALESCE(c.empresa, '') LIKE %s
                OR COALESCE(c.email, '') LIKE %s
                OR COALESCE(c.telefone, '') LIKE %s
                OR COALESCE(c.whatsapp, '') LIKE %s
                OR COALESCE(l.empresa, '') LIKE %s
                OR COALESCE(p.nome, '') LIKE %s
                OR COALESCE(pe.nome, '') LIKE %s
            )
            """
            params.extend([termo, termo, termo, termo, termo, termo, termo, termo])

        if tipo_contato:
            sql += """
  AND c.tipo_contato = %s"""
            params.append(tipo_contato)

        if ativo in (0, 1):
            sql += """
  AND c.ativo = %s"""
            params.append(ativo)

        sql += """
            ORDER BY c.nome, c.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def listar_todos_ativos(cls):
        sql = f"""
            SELECT
                id,
                nome,
                empresa,
                cpf,
                email,
                telefone,
                whatsapp
            FROM {cls.TABLE}
            WHERE ativo = 1
            ORDER BY nome
        """
        return cls.fetch_all(sql)

    @classmethod
    def buscar_por_id(cls, contato_id):
        sql = f"""
            SELECT
                c.id,
                c.uuid,
                c.lead_id,
                c.parceiro_id,
                c.executivo_responsavel_id,
                c.empresa,
                c.nome,
                c.cargo,
                c.cpf,
                c.email,
                c.telefone,
                c.whatsapp,
                c.tipo_contato,
                c.canal_preferido,
                c.cidade,
                c.uf,
                c.observacoes,
                c.ativo,
                c.created_at,
                c.updated_at,
                l.empresa AS lead_empresa,
                COALESCE(p.nome_fantasia, p.nome, p.razao_social) AS parceiro_exibicao,
                pe.nome AS executivo_responsavel_nome
            FROM {cls.TABLE} c
            LEFT JOIN crm_leads l
                ON l.id = c.lead_id
            LEFT JOIN parceiros p
                ON p.id = c.parceiro_id
            LEFT JOIN parceiros_executivos pe
                ON pe.id = c.executivo_responsavel_id
            WHERE c.id = %s
        """

        return cls.fetch_one(sql, (contato_id,))

    @classmethod
    def inserir(cls, dados):
        sql = f"""
            INSERT INTO {cls.TABLE}
            (
                uuid,
                lead_id,
                parceiro_id,
                executivo_responsavel_id,
                empresa,
                nome,
                cargo,
                cpf,
                email,
                telefone,
                whatsapp,
                tipo_contato,
                canal_preferido,
                cidade,
                uf,
                observacoes,
                ativo
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        return cls.execute_insert(
            sql,
            (
                cls.generate_uuid(),
                dados.get("lead_id"),
                dados.get("parceiro_id"),
                dados.get("executivo_responsavel_id"),
                dados.get("empresa"),
                dados["nome"],
                dados.get("cargo"),
                dados.get("cpf"),
                dados.get("email"),
                dados.get("telefone"),
                dados.get("whatsapp"),
                dados["tipo_contato"],
                dados["canal_preferido"],
                dados.get("cidade"),
                dados.get("uf"),
                dados.get("observacoes"),
                cls.bool_to_int(dados.get("ativo", True)),
            ),
        )

    @classmethod
    def atualizar(cls, contato_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET lead_id = %s,
                parceiro_id = %s,
                executivo_responsavel_id = %s,
                empresa = %s,
                nome = %s,
                cargo = %s,
                cpf = %s,
                email = %s,
                telefone = %s,
                whatsapp = %s,
                tipo_contato = %s,
                canal_preferido = %s,
                cidade = %s,
                uf = %s,
                observacoes = %s,
                ativo = %s
            WHERE id = %s
        """

        return cls.execute(
            sql,
            (
                dados.get("lead_id"),
                dados.get("parceiro_id"),
                dados.get("executivo_responsavel_id"),
                dados.get("empresa"),
                dados["nome"],
                dados.get("cargo"),
                dados.get("cpf"),
                dados.get("email"),
                dados.get("telefone"),
                dados.get("whatsapp"),
                dados["tipo_contato"],
                dados["canal_preferido"],
                dados.get("cidade"),
                dados.get("uf"),
                dados.get("observacoes"),
                cls.bool_to_int(dados.get("ativo", True)),
                contato_id,
            ),
        )

    @classmethod
    def excluir(cls, contato_id):
        sql = f"DELETE FROM {cls.TABLE} WHERE id = %s"
        return cls.execute(sql, (contato_id,))
