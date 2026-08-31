from app.repositories.base_repository import BaseRepository


class FaixaRedeRepository(BaseRepository):
    @classmethod
    def listar(cls, pesquisa=None, ativo=1, limit=50, offset=0):
        sql = """
            SELECT fr.*,
                   extras.portas_adicionais
            FROM implantacao_faixas_rede fr
            LEFT JOIN (
                SELECT faixa_rede_id, GROUP_CONCAT(portas ORDER BY porta_inicio, id SEPARATOR ', ') AS portas_adicionais
                FROM implantacao_faixas_rede_portas
                GROUP BY faixa_rede_id
            ) extras ON extras.faixa_rede_id = fr.id
            WHERE 1 = 1
        """
        where, params = cls._filtros(pesquisa, ativo)
        sql += where
        sql += """
            ORDER BY INET_ATON(SUBSTRING_INDEX(fr.rede, '/', 1)) ASC, fr.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def total(cls, pesquisa=None, ativo=1):
        sql = "SELECT COUNT(*) FROM implantacao_faixas_rede fr WHERE 1 = 1"
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
    def ultima_ativa_cadastrada(cls):
        return cls.fetch_one(
            """
            SELECT fr.rede,
                   fr.fw_wan,
                   GREATEST(
                       COALESCE(fr.porta_fim, 0),
                       COALESCE(extras.maior_porta_fim, 0)
                   ) AS porta_fim
            FROM implantacao_faixas_rede fr
            LEFT JOIN (
                SELECT faixa_rede_id, MAX(porta_fim) AS maior_porta_fim
                FROM implantacao_faixas_rede_portas
                GROUP BY faixa_rede_id
            ) extras ON extras.faixa_rede_id = fr.id
            WHERE fr.ativo = 1
            ORDER BY fr.id DESC
            LIMIT 1
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
            SELECT fr.*, fr.porta_inicio AS conflito_inicio, fr.porta_fim AS conflito_fim
            FROM implantacao_faixas_rede fr
            WHERE fr.ativo = 1
              AND fr.fw_wan = %s
              AND fr.porta_inicio IS NOT NULL
              AND fr.porta_fim IS NOT NULL
              AND fr.porta_inicio <= %s
              AND fr.porta_fim >= %s
        """
        params = [fw_wan, porta_fim, porta_inicio]
        if ignorar_id:
            sql += " AND fr.id <> %s"
            params.append(ignorar_id)
        sql += """
            UNION ALL
            SELECT fr.*, p.porta_inicio AS conflito_inicio, p.porta_fim AS conflito_fim
            FROM implantacao_faixas_rede_portas p
            JOIN implantacao_faixas_rede fr ON fr.id = p.faixa_rede_id
            WHERE fr.ativo = 1
              AND fr.fw_wan = %s
              AND p.porta_inicio <= %s
              AND p.porta_fim >= %s
        """
        params.extend([fw_wan, porta_fim, porta_inicio])
        if ignorar_id:
            sql += " AND fr.id <> %s"
            params.append(ignorar_id)
        sql += " ORDER BY id ASC LIMIT 1"
        return cls.fetch_one(sql, tuple(params))

    @classmethod
    def inserir(cls, dados):
        faixa_id = cls.execute_insert(
            """
            INSERT INTO implantacao_faixas_rede (
                uuid, rede, mascara, quantidade_servidores, fw_wan, fw_lan,
                cliente_id, cliente_nome, cliente_cnpj, vpn, porta_inicio, porta_fim, portas, pve, observacoes, ativo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (cls.generate_uuid(),) + cls._params(dados),
        )
        cls.substituir_portas_adicionais(faixa_id, dados.get("portas_adicionais", []))
        return faixa_id

    @classmethod
    def atualizar(cls, faixa_id, dados):
        atualizado = cls.execute(
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
        cls.substituir_portas_adicionais(faixa_id, dados.get("portas_adicionais", []))
        return atualizado

    @classmethod
    def listar_portas_adicionais(cls, faixa_id):
        return cls.fetch_all(
            """
            SELECT *
            FROM implantacao_faixas_rede_portas
            WHERE faixa_rede_id = %s
            ORDER BY porta_inicio ASC, id ASC
            """,
            (faixa_id,),
        )

    @classmethod
    def substituir_portas_adicionais(cls, faixa_id, portas_adicionais):
        cls.execute("DELETE FROM implantacao_faixas_rede_portas WHERE faixa_rede_id = %s", (faixa_id,))
        for item in portas_adicionais or []:
            cls.execute_insert(
                """
                INSERT INTO implantacao_faixas_rede_portas (
                    uuid, faixa_rede_id, porta_inicio, porta_fim, portas
                ) VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    cls.generate_uuid(),
                    faixa_id,
                    item.get("porta_inicio"),
                    item.get("porta_fim"),
                    item.get("portas"),
                ),
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
                    fr.rede LIKE %s
                    OR fr.cliente_nome LIKE %s
                    OR COALESCE(fr.cliente_cnpj, '') LIKE %s
                    OR REGEXP_REPLACE(COALESCE(fr.cliente_cnpj, ''), '[^0-9A-Za-z]', '') LIKE %s
                    OR COALESCE(fr.fw_wan, '') LIKE %s
                    OR COALESCE(fr.fw_lan, '') LIKE %s
                    OR COALESCE(fr.vpn, '') LIKE %s
                    OR COALESCE(fr.portas, '') LIKE %s
                    OR EXISTS (SELECT 1 FROM implantacao_faixas_rede_portas p WHERE p.faixa_rede_id = fr.id AND p.portas LIKE %s)
                    OR COALESCE(fr.pve, '') LIKE %s
                    OR COALESCE(fr.observacoes, '') LIKE %s
                )
                """
            )
            params.extend([termo, termo, termo, termo_cnpj, termo, termo, termo, termo, termo, termo, termo])
        if ativo in (0, 1):
            where.append("fr.ativo = %s")
            params.append(ativo)
        return (" AND " + " AND ".join(where) if where else ""), params
