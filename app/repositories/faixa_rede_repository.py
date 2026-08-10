from app.repositories.base_repository import BaseRepository


class FaixaRedeRepository(BaseRepository):
    @classmethod
    def listar(cls, pesquisa=None, ativo=1, limit=50, offset=0):
        sql = """
            SELECT *
            FROM implantacao_faixas_rede
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, ativo)
        sql += where
        sql += """
            ORDER BY INET_ATON(SUBSTRING_INDEX(rede, '/', 1)) ASC, id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def total(cls, pesquisa=None, ativo=1):
        sql = "SELECT COUNT(*) FROM implantacao_faixas_rede WHERE 1 = 1"
        where, params = cls._filtros(pesquisa, ativo)
        return cls.scalar(sql + where, tuple(params)) or 0

    @classmethod
    def dashboard(cls):
        return cls.fetch_one(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN ativo = 1 THEN 1 ELSE 0 END) AS ativas,
                SUM(CASE WHEN ativo = 1 AND mascara = 29 THEN 1 ELSE 0 END) AS redes_29,
                SUM(CASE WHEN ativo = 1 AND mascara = 28 THEN 1 ELSE 0 END) AS redes_28,
                SUM(CASE WHEN ativo = 1 AND mascara = 27 THEN 1 ELSE 0 END) AS redes_27,
                SUM(CASE WHEN ativo = 1 THEN COALESCE(quantidade_servidores, 0) ELSE 0 END) AS servidores_total
            FROM implantacao_faixas_rede
            """
        )

    @classmethod
    def listar_ativas(cls):
        return cls.fetch_all(
            """
            SELECT rede
            FROM implantacao_faixas_rede
            WHERE ativo = 1
            ORDER BY id ASC
            """
        )

    @classmethod
    def buscar_por_id(cls, faixa_id):
        return cls.fetch_one("SELECT * FROM implantacao_faixas_rede WHERE id = %s", (faixa_id,))

    @classmethod
    def buscar_por_rede(cls, rede):
        return cls.fetch_one("SELECT * FROM implantacao_faixas_rede WHERE rede = %s LIMIT 1", (rede,))

    @classmethod
    def buscar_conflito_portas(cls, fw_wan, porta_inicio, porta_fim, ignorar_id=None):
        if not fw_wan or not porta_inicio or not porta_fim:
            return None
        sql = """
            SELECT *
            FROM implantacao_faixas_rede
            WHERE ativo = 1
              AND fw_wan = %s
              AND porta_inicio IS NOT NULL
              AND porta_fim IS NOT NULL
              AND porta_inicio <= %s
              AND porta_fim >= %s
        """
        params = [fw_wan, porta_fim, porta_inicio]
        if ignorar_id:
            sql += " AND id <> %s"
            params.append(ignorar_id)
        sql += " ORDER BY id ASC LIMIT 1"
        return cls.fetch_one(sql, tuple(params))

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO implantacao_faixas_rede (
                uuid, rede, mascara, quantidade_servidores, fw_wan, fw_lan,
                cliente_id, cliente_nome, cliente_cnpj, vpn, porta_inicio, porta_fim, portas, pve, observacoes, ativo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (cls.generate_uuid(),) + cls._params(dados),
        )

    @classmethod
    def atualizar(cls, faixa_id, dados):
        return cls.execute(
            """
            UPDATE implantacao_faixas_rede
            SET rede=%s,
                mascara=%s,
                quantidade_servidores=%s,
                fw_wan=%s,
                fw_lan=%s,
                cliente_id=%s,
                cliente_nome=%s,
                cliente_cnpj=%s,
                vpn=%s,
                porta_inicio=%s,
                porta_fim=%s,
                portas=%s,
                pve=%s,
                observacoes=%s,
                ativo=%s
            WHERE id=%s
            """,
            cls._params(dados) + (faixa_id,),
        )

    @classmethod
    def excluir(cls, faixa_id):
        return cls.execute("UPDATE implantacao_faixas_rede SET ativo = 0 WHERE id = %s", (faixa_id,))

    @classmethod
    def _params(cls, dados):
        return (
            dados.get("rede"),
            dados.get("mascara"),
            dados.get("quantidade_servidores"),
            dados.get("fw_wan"),
            dados.get("fw_lan"),
            dados.get("cliente_id"),
            dados.get("cliente_nome"),
            dados.get("cliente_cnpj"),
            dados.get("vpn"),
            dados.get("porta_inicio"),
            dados.get("porta_fim"),
            dados.get("portas"),
            dados.get("pve"),
            dados.get("observacoes"),
            dados.get("ativo", 1),
        )

    @classmethod
    def _filtros(cls, pesquisa=None, ativo=1):
        where = []
        params = []
        if pesquisa:
            termo = f"%{pesquisa}%"
            termo_cnpj = f"%{''.join(ch for ch in str(pesquisa) if ch.isalnum()).upper()}%"
            where.append(
                """
                (
                    rede LIKE %s
                    OR cliente_nome LIKE %s
                    OR COALESCE(cliente_cnpj, '') LIKE %s
                    OR REGEXP_REPLACE(COALESCE(cliente_cnpj, ''), '[^0-9A-Za-z]', '') LIKE %s
                    OR COALESCE(fw_wan, '') LIKE %s
                    OR COALESCE(fw_lan, '') LIKE %s
                    OR COALESCE(vpn, '') LIKE %s
                    OR COALESCE(portas, '') LIKE %s
                    OR COALESCE(pve, '') LIKE %s
                    OR COALESCE(observacoes, '') LIKE %s
                )
                """
            )
            params.extend([termo, termo, termo, termo_cnpj, termo, termo, termo, termo, termo, termo])
        if ativo in (0, 1):
            where.append("ativo = %s")
            params.append(ativo)
        return (" AND " + " AND ".join(where) if where else ""), params
