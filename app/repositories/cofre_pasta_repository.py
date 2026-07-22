from app.repositories.base_repository import BaseRepository


class CofrePastaRepository(BaseRepository):
    @classmethod
    def listar(cls, pesquisa=None, tipo=None, ativo=1, limit=200, offset=0):
        sql = """
            SELECT *
            FROM implantacao_cofre_pastas
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, tipo, ativo)
        sql += where
        sql += """
            ORDER BY tipo ASC, nome ASC, id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def listar_ativas(cls):
        return cls.fetch_all(
            """
            SELECT *
            FROM implantacao_cofre_pastas
            WHERE ativo = 1
            ORDER BY tipo ASC, nome ASC
            """
        )

    @classmethod
    def buscar_por_id(cls, pasta_id):
        return cls.fetch_one("SELECT * FROM implantacao_cofre_pastas WHERE id = %s", (pasta_id,))

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO implantacao_cofre_pastas (
                uuid, nome, tipo, parceiro_id, parceiro_nome, cliente_id, cliente_nome,
                owner_email, compartilhada, compartilhada_com, observacoes, ativo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (cls.generate_uuid(),) + cls._params(dados),
        )

    @classmethod
    def atualizar(cls, pasta_id, dados):
        return cls.execute(
            """
            UPDATE implantacao_cofre_pastas
            SET nome=%s,
                tipo=%s,
                parceiro_id=%s,
                parceiro_nome=%s,
                cliente_id=%s,
                cliente_nome=%s,
                owner_email=%s,
                compartilhada=%s,
                compartilhada_com=%s,
                observacoes=%s,
                ativo=%s
            WHERE id=%s
            """,
            cls._params(dados) + (pasta_id,),
        )

    @classmethod
    def excluir(cls, pasta_id):
        return cls.execute("UPDATE implantacao_cofre_pastas SET ativo = 0 WHERE id = %s", (pasta_id,))

    @classmethod
    def _params(cls, dados):
        return (
            dados.get("nome"),
            dados.get("tipo"),
            dados.get("parceiro_id"),
            dados.get("parceiro_nome"),
            dados.get("cliente_id"),
            dados.get("cliente_nome"),
            dados.get("owner_email") or "sistema",
            dados.get("compartilhada", 0),
            dados.get("compartilhada_com"),
            dados.get("observacoes"),
            dados.get("ativo", 1),
        )

    @classmethod
    def _filtros(cls, pesquisa=None, tipo=None, ativo=1):
        where = []
        params = []
        if pesquisa:
            termo = f"%{pesquisa}%"
            where.append(
                """
                (
                    nome LIKE %s
                    OR COALESCE(parceiro_nome, '') LIKE %s
                    OR COALESCE(cliente_nome, '') LIKE %s
                    OR owner_email LIKE %s
                    OR COALESCE(compartilhada_com, '') LIKE %s
                    OR COALESCE(observacoes, '') LIKE %s
                )
                """
            )
            params.extend([termo] * 6)
        if tipo:
            where.append("tipo = %s")
            params.append(tipo)
        if ativo in (0, 1):
            where.append("ativo = %s")
            params.append(ativo)
        return (" AND " + " AND ".join(where) if where else ""), params
