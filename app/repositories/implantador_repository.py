from app.repositories.base_repository import BaseRepository


class ImplantadorRepository(BaseRepository):
    @classmethod
    def listar(cls, pesquisa=None, ativo=1, limit=1000, offset=0):
        sql = """
            SELECT id, uuid, nome, email, telefone, ativo, observacoes, created_at, updated_at
            FROM implantadores
            WHERE 1 = 1
        """
        params = []
        if ativo in (0, 1):
            sql += " AND ativo = %s"
            params.append(ativo)
        if pesquisa:
            sql += " AND (nome LIKE %s OR email LIKE %s OR telefone LIKE %s)"
            termo = f"%{pesquisa}%"
            params.extend([termo, termo, termo])
        sql += " ORDER BY nome ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def total(cls, pesquisa=None, ativo=1):
        sql = "SELECT COUNT(*) AS total FROM implantadores WHERE 1 = 1"
        params = []
        if ativo in (0, 1):
            sql += " AND ativo = %s"
            params.append(ativo)
        if pesquisa:
            sql += " AND (nome LIKE %s OR email LIKE %s OR telefone LIKE %s)"
            termo = f"%{pesquisa}%"
            params.extend([termo, termo, termo])
        row = cls.fetch_one(sql, tuple(params))
        return row["total"] if row else 0

    @classmethod
    def buscar_por_id(cls, implantador_id):
        return cls.fetch_one(
            """
            SELECT id, uuid, nome, email, telefone, ativo, observacoes, created_at, updated_at
            FROM implantadores
            WHERE id = %s
            """,
            (implantador_id,),
        )

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO implantadores (uuid, nome, email, telefone, ativo, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("nome"), dados.get("email"),
                dados.get("telefone"), cls.bool_to_int(dados.get("ativo", True)),
                dados.get("observacoes"),
            ),
        )

    @classmethod
    def atualizar(cls, implantador_id, dados):
        return cls.execute(
            """
            UPDATE implantadores
            SET nome=%s, email=%s, telefone=%s, ativo=%s, observacoes=%s
            WHERE id=%s
            """,
            (
                dados.get("nome"), dados.get("email"), dados.get("telefone"),
                cls.bool_to_int(dados.get("ativo", True)), dados.get("observacoes"),
                implantador_id,
            ),
        )

    @classmethod
    def inativar(cls, implantador_id):
        return cls.execute(
            "UPDATE implantadores SET ativo = 0 WHERE id = %s",
            (implantador_id,),
        )
