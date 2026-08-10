from app.repositories.base_repository import BaseRepository


class O3WebLicencaRepository(BaseRepository):
    @classmethod
    def listar(cls, pesquisa=None, tipo=None, ativo=1, validade=None, limit=50, offset=0):
        sql = """
            SELECT *
            FROM o3web_licencas
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, tipo, ativo, validade)
        sql += where
        sql += """
            ORDER BY cliente_nome ASC, COALESCE(data_expiracao, '2999-12-31') ASC, id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def total(cls, pesquisa=None, tipo=None, ativo=1, validade=None):
        sql = "SELECT COUNT(*) FROM o3web_licencas WHERE 1 = 1"
        where, params = cls._filtros(pesquisa, tipo, ativo, validade)
        return cls.scalar(sql + where, tuple(params)) or 0

    @classmethod
    def dashboard(cls):
        return cls.fetch_one(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN ativo = 1 THEN 1 ELSE 0 END) AS ativas,
                SUM(CASE WHEN tipo = 'trial' AND ativo = 1 THEN 1 ELSE 0 END) AS trials,
                SUM(CASE WHEN tipo = 'permanent' AND ativo = 1 THEN 1 ELSE 0 END) AS permanentes,
                SUM(CASE WHEN ativo = 1 THEN COALESCE(usuarios, 0) ELSE 0 END) AS usuarios_total,
                SUM(CASE WHEN ativo = 1 AND data_expiracao IS NOT NULL AND data_expiracao < CURDATE() THEN 1 ELSE 0 END) AS expiradas
            FROM o3web_licencas
            """
        )

    @classmethod
    def buscar_por_id(cls, licenca_id):
        return cls.fetch_one("SELECT * FROM o3web_licencas WHERE id = %s", (licenca_id,))

    @classmethod
    def buscar_por_id_licenca(cls, id_licenca):
        if not id_licenca:
            return None
        return cls.fetch_one("SELECT * FROM o3web_licencas WHERE id_licenca = %s LIMIT 1", (id_licenca,))

    @classmethod
    def buscar_por_chave_cliente_url(cls, chave_ativacao, cliente_nome, url_principal):
        if not chave_ativacao or not cliente_nome:
            return None
        return cls.fetch_one(
            """
            SELECT *
            FROM o3web_licencas
            WHERE COALESCE(chave_ativacao, '') = %s
              AND cliente_nome = %s
              AND COALESCE(url_principal, '') = %s
            LIMIT 1
            """,
            (chave_ativacao or "", cliente_nome, url_principal or ""),
        )

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO o3web_licencas (
                uuid, cliente_id, cliente_nome, cliente_cnpj, chave_ativacao, id_licenca, tipo, bkp, dias, usuarios, edicao,
                data_ativacao, data_ativacao_raw, data_expiracao, data_expiracao_raw,
                url_principal, url_secundaria, comments, observacao, origem, ativo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            cls._params(dados, incluir_uuid=True),
        )

    @classmethod
    def atualizar(cls, licenca_id, dados):
        return cls.execute(
            """
            UPDATE o3web_licencas
            SET cliente_id=%s,
                cliente_nome=%s,
                cliente_cnpj=%s,
                chave_ativacao=%s,
                id_licenca=%s,
                tipo=%s,
                bkp=%s,
                dias=%s,
                usuarios=%s,
                edicao=%s,
                data_ativacao=%s,
                data_ativacao_raw=%s,
                data_expiracao=%s,
                data_expiracao_raw=%s,
                url_principal=%s,
                url_secundaria=%s,
                comments=%s,
                observacao=%s,
                origem=%s,
                ativo=%s
            WHERE id=%s
            """,
            cls._params(dados) + (licenca_id,),
        )

    @classmethod
    def excluir(cls, licenca_id):
        return cls.execute("UPDATE o3web_licencas SET ativo = 0 WHERE id = %s", (licenca_id,))

    @classmethod
    def _params(cls, dados, incluir_uuid=False):
        params = (
            dados.get("cliente_id"),
            dados.get("cliente_nome"),
            dados.get("cliente_cnpj"),
            dados.get("chave_ativacao"),
            dados.get("id_licenca"),
            dados.get("tipo"),
            cls.bool_to_int(dados.get("bkp")),
            dados.get("dias"),
            dados.get("usuarios"),
            dados.get("edicao"),
            dados.get("data_ativacao"),
            dados.get("data_ativacao_raw"),
            dados.get("data_expiracao"),
            dados.get("data_expiracao_raw"),
            dados.get("url_principal"),
            dados.get("url_secundaria"),
            dados.get("comments"),
            dados.get("observacao"),
            dados.get("origem") or "MANUAL",
            dados.get("ativo", 1),
        )
        if incluir_uuid:
            return (cls.generate_uuid(),) + params
        return params

    @classmethod
    def _filtros(cls, pesquisa=None, tipo=None, ativo=1, validade=None):
        where = []
        params = []
        if pesquisa:
            termo = f"%{pesquisa}%"
            termo_cnpj = f"%{''.join(ch for ch in str(pesquisa) if ch.isalnum()).upper()}%"
            where.append("""
                (
                    cliente_nome LIKE %s
                    OR COALESCE(chave_ativacao, '') LIKE %s
                    OR COALESCE(id_licenca, '') LIKE %s
                    OR COALESCE(cliente_cnpj, '') LIKE %s
                    OR REGEXP_REPLACE(COALESCE(cliente_cnpj, ''), '[^0-9A-Za-z]', '') LIKE %s
                    OR COALESCE(url_principal, '') LIKE %s
                    OR COALESCE(comments, '') LIKE %s
                    OR COALESCE(observacao, '') LIKE %s
                )
            """)
            params.extend([termo, termo, termo, termo, termo_cnpj, termo, termo, termo])
        if tipo:
            where.append("tipo = %s")
            params.append(tipo)
        if validade == "expiradas":
            where.append("data_expiracao IS NOT NULL AND data_expiracao < CURDATE()")
        elif validade == "vigentes":
            where.append("(data_expiracao IS NULL OR data_expiracao >= CURDATE())")
        if ativo in (0, 1):
            where.append("ativo = %s")
            params.append(ativo)
        return (" AND " + " AND ".join(where) if where else ""), params
