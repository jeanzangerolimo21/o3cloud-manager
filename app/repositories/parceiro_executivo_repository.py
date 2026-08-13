from app.repositories.base_repository import BaseRepository


class ParceiroExecutivoRepository(BaseRepository):

    TABLE = "parceiros_executivos"

    @classmethod
    def total(cls, pesquisa=None, ativo=None, parceiro_id=None):
        sql = f"""
            SELECT COUNT(*)
            FROM {cls.TABLE} pe
            LEFT JOIN parceiros p
                ON p.id = pe.parceiro_id
            WHERE 1 = 1
        """

        params = []

        if parceiro_id is not None:
            sql += "\n  AND pe.parceiro_id = %s"
            params.append(parceiro_id)

        if ativo in (0, 1):
            sql += "\n  AND pe.ativo = %s"
            params.append(ativo)

        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                pe.nome LIKE %s
                OR pe.email LIKE %s
                OR pe.telefone LIKE %s
                OR COALESCE(p.nome, '') LIKE %s
            )
            """
            params.extend([termo, termo, termo, termo])

        return cls.scalar(sql, tuple(params)) or 0

    @classmethod
    def listar(cls, pesquisa=None, ativo=None, parceiro_id=None, limit=50, offset=0):
        sql = f"""
            SELECT
                pe.id,
                pe.uuid,
                pe.parceiro_id,
                pe.nome,
                pe.email,
                pe.telefone,
                pe.chave_pix,
                pe.informacoes_pagamento,
                pe.premiacao_ativa,
                pe.ativo,
                pe.created_at,
                pe.updated_at,
                p.nome AS parceiro,
                p.sigla AS parceiro_sigla
            FROM {cls.TABLE} pe
            LEFT JOIN parceiros p
                ON p.id = pe.parceiro_id
            WHERE 1 = 1
        """

        params = []

        if parceiro_id is not None:
            sql += "\n  AND pe.parceiro_id = %s"
            params.append(parceiro_id)

        if ativo in (0, 1):
            sql += "\n  AND pe.ativo = %s"
            params.append(ativo)

        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += """
            AND (
                pe.nome LIKE %s
                OR pe.email LIKE %s
                OR pe.telefone LIKE %s
                OR COALESCE(p.nome, '') LIKE %s
            )
            """
            params.extend([termo, termo, termo, termo])

        sql += """
            ORDER BY pe.nome
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def listar_todos_ativos(cls):
        sql = f"""
            SELECT
                pe.id,
                pe.parceiro_id,
                pe.nome,
                pe.email,
                pe.telefone,
                p.nome AS parceiro
            FROM {cls.TABLE} pe
            LEFT JOIN parceiros p
                ON p.id = pe.parceiro_id
            WHERE pe.ativo = 1
            ORDER BY pe.nome
        """

        return cls.fetch_all(sql)

    @classmethod
    def buscar_por_id(cls, executivo_id):
        sql = f"""
            SELECT
                pe.id,
                pe.uuid,
                pe.parceiro_id,
                pe.nome,
                pe.email,
                pe.telefone,
                pe.chave_pix,
                pe.informacoes_pagamento,
                pe.premiacao_ativa,
                pe.ativo,
                pe.created_at,
                pe.updated_at,
                p.nome AS parceiro,
                p.sigla AS parceiro_sigla
            FROM {cls.TABLE} pe
            LEFT JOIN parceiros p
                ON p.id = pe.parceiro_id
            WHERE pe.id = %s
        """

        return cls.fetch_one(sql, (executivo_id,))


    @classmethod
    def buscar_duplicado(cls, nome, email=None, ignorar_id=None):
        sql = f"""
            SELECT id, nome, email
            FROM {cls.TABLE}
            WHERE (LOWER(TRIM(nome)) = LOWER(TRIM(%s))
        """
        params = [nome]

        if email:
            sql += " OR LOWER(TRIM(email)) = LOWER(TRIM(%s))"
            params.append(email)

        sql += ")"

        if ignorar_id:
            sql += " AND id <> %s"
            params.append(ignorar_id)

        sql += " LIMIT 1"
        return cls.fetch_one(sql, tuple(params))

    @classmethod
    def contar_por_parceiro(cls, parceiro_id):
        sql = f"""
            SELECT COUNT(*)
            FROM {cls.TABLE}
            WHERE parceiro_id = %s
        """

        return cls.scalar(sql, (parceiro_id,)) or 0

    @classmethod
    def inserir(cls, dados):
        sql = f"""
            INSERT INTO {cls.TABLE}
            (
                uuid,
                parceiro_id,
                nome,
                email,
                telefone,
                chave_pix,
                informacoes_pagamento,
                premiacao_ativa,
                ativo
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        return cls.execute_insert(
            sql,
            (
                cls.generate_uuid(),
                dados.get("parceiro_id"),
                dados["nome"],
                dados.get("email"),
                dados.get("telefone"),
                dados.get("chave_pix"),
                dados.get("informacoes_pagamento"),
                cls.bool_to_int(dados.get("premiacao_ativa", False)),
                cls.bool_to_int(dados.get("ativo", True)),
            ),
        )

    @classmethod
    def atualizar(cls, executivo_id, dados):
        sql = f"""
            UPDATE {cls.TABLE}
            SET parceiro_id = %s,
                nome = %s,
                email = %s,
                telefone = %s,
                chave_pix = %s,
                informacoes_pagamento = %s,
                premiacao_ativa = %s,
                ativo = %s
            WHERE id = %s
        """

        return cls.execute(
            sql,
            (
                dados.get("parceiro_id"),
                dados["nome"],
                dados.get("email"),
                dados.get("telefone"),
                dados.get("chave_pix"),
                dados.get("informacoes_pagamento"),
                cls.bool_to_int(dados.get("premiacao_ativa", False)),
                cls.bool_to_int(dados.get("ativo", True)),
                executivo_id,
            ),
        )

    @classmethod
    def atualizar_premiacao(cls, executivo_id, premiacao_ativa):
        sql = f"""
            UPDATE {cls.TABLE}
            SET premiacao_ativa = %s
            WHERE id = %s
        """

        return cls.execute(sql, (cls.bool_to_int(premiacao_ativa), executivo_id))

    @classmethod
    def excluir(cls, executivo_id):
        sql = f"""
            UPDATE {cls.TABLE}
            SET parceiro_id = NULL,
                ativo = 0
            WHERE id = %s
        """

        return cls.execute(sql, (executivo_id,))
