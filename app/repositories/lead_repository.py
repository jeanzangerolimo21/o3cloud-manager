from app.repositories.base_repository import BaseRepository


class LeadRepository(BaseRepository):

    TABLE = "crm_leads"

    @classmethod
    def total(cls, pesquisa=None, status=None, origem=None, ativo=None):
        sql = f"""
            SELECT COUNT(*)
            FROM {cls.TABLE} l
            LEFT JOIN parceiros p
                ON p.id = l.parceiro_id
            LEFT JOIN parceiros_executivos pe
                ON pe.id = l.executivo_responsavel_id
            WHERE 1 = 1
        """

        params = []

        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                l.empresa LIKE %s
                OR l.nome_contato LIKE %s
                OR l.email LIKE %s
                OR l.telefone LIKE %s
                OR COALESCE(l.interesse, '') LIKE %s
                OR COALESCE(p.nome, '') LIKE %s
                OR COALESCE(pe.nome, '') LIKE %s
            )
            """
            params.extend([termo, termo, termo, termo, termo, termo, termo])

        if status:
            sql += """
  AND l.status = %s"""
            params.append(status)

        if origem:
            sql += """
  AND l.origem = %s"""
            params.append(origem)

        if ativo in (0, 1):
            sql += """
  AND l.ativo = %s"""
            params.append(ativo)

        return cls.scalar(sql, tuple(params)) or 0

    @classmethod
    def listar(cls, pesquisa=None, status=None, origem=None, ativo=None, limit=50, offset=0):
        sql = f"""
            SELECT
                l.id,
                l.uuid,
                l.parceiro_id,
                l.executivo_responsavel_id,
                l.empresa,
                l.nome_contato,
                l.cargo,
                l.email,
                l.telefone,
                l.origem,
                l.interesse,
                l.status,
                l.cidade,
                l.uf,
                l.ativo,
                l.created_at,
                l.updated_at,
                p.nome AS parceiro_nome,
                COALESCE(p.nome_fantasia, p.nome, p.razao_social) AS parceiro_exibicao,
                pe.nome AS executivo_responsavel_nome
            FROM {cls.TABLE} l
            LEFT JOIN parceiros p
                ON p.id = l.parceiro_id
            LEFT JOIN parceiros_executivos pe
                ON pe.id = l.executivo_responsavel_id
            WHERE 1 = 1
        """

        params = []

        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                l.empresa LIKE %s
                OR l.nome_contato LIKE %s
                OR l.email LIKE %s
                OR l.telefone LIKE %s
                OR COALESCE(l.interesse, '') LIKE %s
                OR COALESCE(p.nome, '') LIKE %s
                OR COALESCE(pe.nome, '') LIKE %s
            )
            """
            params.extend([termo, termo, termo, termo, termo, termo, termo])

        if status:
            sql += """
  AND l.status = %s"""
            params.append(status)

        if origem:
            sql += """
  AND l.origem = %s"""
            params.append(origem)

        if ativo in (0, 1):
            sql += """
  AND l.ativo = %s"""
            params.append(ativo)

        sql += """
            ORDER BY l.created_at DESC, l.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def listar_todos_ativos(cls):
        sql = f"""
            SELECT
                id,
                empresa,
                nome_contato,
                status
            FROM {cls.TABLE}
            WHERE ativo = 1
            ORDER BY empresa, nome_contato
        """

        return cls.fetch_all(sql)

    @classmethod
    def buscar_por_id(cls, lead_id):
        sql = f"""
            SELECT
                l.id,
                l.uuid,
                l.parceiro_id,
                l.executivo_responsavel_id,
                l.empresa,
                l.nome_contato,
                l.cargo,
                l.email,
                l.telefone,
                l.origem,
                l.interesse,
                l.status,
                l.cidade,
                l.uf,
                l.observacoes,
                l.ativo,
                l.created_at,
                l.updated_at,
                p.nome AS parceiro_nome,
                COALESCE(p.nome_fantasia, p.nome, p.razao_social) AS parceiro_exibicao,
                pe.nome AS executivo_responsavel_nome
            FROM {cls.TABLE} l
            LEFT JOIN parceiros p
                ON p.id = l.parceiro_id
            LEFT JOIN parceiros_executivos pe
                ON pe.id = l.executivo_responsavel_id
            WHERE l.id = %s
        """

        return cls.fetch_one(sql, (lead_id,))

    @classmethod
    def inserir(cls, dados):
        sql = f"""
            INSERT INTO {cls.TABLE}
            (
                uuid,
                parceiro_id,
                executivo_responsavel_id,
                empresa,
                nome_contato,
                cargo,
                email,
                telefone,
                origem,
                interesse,
                status,
                cidade,
                uf,
                observacoes,
                ativo
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        return cls.execute_insert(
            sql,
            (
                cls.generate_uuid(),
                dados.get("parceiro_id"),
                dados.get("executivo_responsavel_id"),
                dados["empresa"],
                dados["nome_contato"],
                dados.get("cargo"),
                dados.get("email"),
                dados.get("telefone"),
                dados["origem"],
                dados.get("interesse"),
                dados["status"],
                dados.get("cidade"),
                dados.get("uf"),
                dados.get("observacoes"),
                cls.bool_to_int(dados.get("ativo", True)),
            ),
        )

    @classmethod
    def atualizar(cls, lead_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET parceiro_id = %s,
                executivo_responsavel_id = %s,
                empresa = %s,
                nome_contato = %s,
                cargo = %s,
                email = %s,
                telefone = %s,
                origem = %s,
                interesse = %s,
                status = %s,
                cidade = %s,
                uf = %s,
                observacoes = %s,
                ativo = %s
            WHERE id = %s
        """

        return cls.execute(
            sql,
            (
                dados.get("parceiro_id"),
                dados.get("executivo_responsavel_id"),
                dados["empresa"],
                dados["nome_contato"],
                dados.get("cargo"),
                dados.get("email"),
                dados.get("telefone"),
                dados["origem"],
                dados.get("interesse"),
                dados["status"],
                dados.get("cidade"),
                dados.get("uf"),
                dados.get("observacoes"),
                cls.bool_to_int(dados.get("ativo", True)),
                lead_id,
            ),
        )

    @classmethod
    def excluir(cls, lead_id):
        sql = f"DELETE FROM {cls.TABLE} WHERE id = %s"
        return cls.execute(sql, (lead_id,))

    @classmethod
    def excluir_em_massa(cls, lead_ids):
        ids = [int(item) for item in lead_ids if str(item).isdigit()]
        if not ids:
            return 0
        marks = ",".join(["%s"] * len(ids))
        return cls.execute(f"DELETE FROM {cls.TABLE} WHERE id IN ({marks})", tuple(ids))
