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
    def listar_parceiros_navegacao(cls):
        return cls.fetch_all(
            """
            SELECT
                p.id,
                COALESCE(p.nome_fantasia, p.nome, p.razao_social) AS nome,
                p.sigla,
                COUNT(DISTINCT cp.id) AS total_pastas,
                COUNT(DISTINCT cs.id) AS total_credenciais
            FROM parceiros p
            LEFT JOIN implantacao_cofre_pastas cp
                ON cp.parceiro_id = p.id
                AND cp.tipo = 'cliente'
                AND cp.ativo = 1
            LEFT JOIN implantacao_cofre_senhas cs
                ON cs.pasta_id = cp.id
                AND cs.ativo = 1
            WHERE p.ativo = 1
            GROUP BY p.id, p.nome_fantasia, p.nome, p.razao_social, p.sigla
            ORDER BY COALESCE(p.nome_fantasia, p.nome, p.razao_social), p.nome
            """
        )

    @classmethod
    def buscar_parceiro_navegacao(cls, parceiro_id):
        return cls.fetch_one(
            """
            SELECT
                p.id,
                COALESCE(p.nome_fantasia, p.nome, p.razao_social) AS nome,
                p.sigla,
                COUNT(DISTINCT cp.id) AS total_pastas,
                COUNT(DISTINCT cs.id) AS total_credenciais
            FROM parceiros p
            LEFT JOIN implantacao_cofre_pastas cp
                ON cp.parceiro_id = p.id
                AND cp.tipo = 'cliente'
                AND cp.ativo = 1
            LEFT JOIN implantacao_cofre_senhas cs
                ON cs.pasta_id = cp.id
                AND cs.ativo = 1
            WHERE p.id = %s
                AND p.ativo = 1
            GROUP BY p.id, p.nome_fantasia, p.nome, p.razao_social, p.sigla
            """,
            (parceiro_id,),
        )

    @classmethod
    def listar_pastas_cliente_por_parceiro(cls, parceiro_id):
        return cls.fetch_all(
            """
            SELECT
                cp.*,
                COUNT(DISTINCT cs.id) AS total_credenciais,
                SUM(CASE WHEN cs.ativo = 1 THEN 1 ELSE 0 END) AS credenciais_ativas
            FROM implantacao_cofre_pastas cp
            LEFT JOIN implantacao_cofre_senhas cs
                ON cs.pasta_id = cp.id
            WHERE cp.ativo = 1
                AND cp.tipo = 'cliente'
                AND cp.parceiro_id = %s
            GROUP BY cp.id
            ORDER BY COALESCE(cp.cliente_nome, cp.nome), cp.nome
            """,
            (parceiro_id,),
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
