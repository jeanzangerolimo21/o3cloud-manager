from app.repositories.base_repository import BaseRepository


class IntegracaoConfigRepository(BaseRepository):
    TABLE = "implantacao_integracoes_config"

    @classmethod
    def listar(cls, tipo=None, ativo=1, tipos=None):
        sql = """
            SELECT id, uuid, tipo, nome, base_url, usuario, token_nome,
                   CASE WHEN segredo_encrypted IS NULL OR segredo_encrypted = '' THEN 0 ELSE 1 END AS possui_segredo,
                   verify_ssl, timeout_seconds, ativo, observacoes,
                   ultimo_teste_status, ultimo_teste_mensagem, ultimo_teste_em,
                   created_by, updated_by, created_at, updated_at
            FROM implantacao_integracoes_config
            WHERE 1 = 1
        """
        params = []
        if tipo:
            sql += " AND tipo = %s"
            params.append(tipo)
        elif tipos:
            placeholders = ", ".join(["%s"] * len(tipos))
            sql += f" AND tipo IN ({placeholders})"
            params.extend(tipos)
        if ativo in (0, 1):
            sql += " AND ativo = %s"
            params.append(ativo)
        sql += " ORDER BY FIELD(tipo, 'omie', 'clicksign', 'proxmox', 'pbs', 'zabbix', 'freeipa', 'truenas'), nome ASC, id ASC"
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def dashboard(cls, tipos=None):
        where = ""
        params = []
        if tipos:
            placeholders = ", ".join(["%s"] * len(tipos))
            where = f"WHERE tipo IN ({placeholders})"
            params.extend(tipos)
        return cls.fetch_one(
            f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN ativo = 1 THEN 1 ELSE 0 END) AS ativas,
                SUM(CASE WHEN tipo = 'omie' AND ativo = 1 THEN 1 ELSE 0 END) AS omie,
                SUM(CASE WHEN tipo = 'clicksign' AND ativo = 1 THEN 1 ELSE 0 END) AS clicksign,
                SUM(CASE WHEN tipo = 'proxmox' AND ativo = 1 THEN 1 ELSE 0 END) AS proxmox,
                SUM(CASE WHEN tipo = 'pbs' AND ativo = 1 THEN 1 ELSE 0 END) AS pbs,
                SUM(CASE WHEN tipo = 'zabbix' AND ativo = 1 THEN 1 ELSE 0 END) AS zabbix,
                SUM(CASE WHEN tipo = 'freeipa' AND ativo = 1 THEN 1 ELSE 0 END) AS freeipa,
                SUM(CASE WHEN tipo = 'truenas' AND ativo = 1 THEN 1 ELSE 0 END) AS truenas,
                SUM(CASE WHEN ultimo_teste_status = 'OK' THEN 1 ELSE 0 END) AS testes_ok,
                SUM(CASE WHEN ativo = 1 AND (segredo_encrypted IS NULL OR segredo_encrypted = '') THEN 1 ELSE 0 END) AS pendentes_credencial,
                SUM(CASE WHEN ativo = 1 AND segredo_encrypted IS NOT NULL AND segredo_encrypted <> '' AND ultimo_teste_status IS NULL THEN 1 ELSE 0 END) AS pendentes_teste,
                SUM(CASE WHEN ativo = 1 AND ultimo_teste_status = 'ERRO' THEN 1 ELSE 0 END) AS erros_cadastro
            FROM implantacao_integracoes_config
            {where}
            """,
            tuple(params),
        )

    @classmethod
    def dashboard_diagnosticos(cls, tipos=None):
        where = "WHERE ativo = 1"
        params = []
        if tipos:
            placeholders = ", ".join(["%s"] * len(tipos))
            where += f" AND tipo IN ({placeholders})"
            params.extend(tipos)
        return cls.fetch_one(
            f"""
            SELECT
                SUM(CASE WHEN ultimo_teste_status = 'OK' THEN 1 ELSE 0 END) AS diagnostico_configurado,
                SUM(CASE WHEN segredo_encrypted IS NULL OR segredo_encrypted = '' THEN 1 ELSE 0 END) AS diagnostico_pendente_credencial,
                SUM(CASE WHEN segredo_encrypted IS NOT NULL AND segredo_encrypted <> '' AND ultimo_teste_status IS NULL THEN 1 ELSE 0 END) AS diagnostico_pendente_teste,
                SUM(CASE WHEN ultimo_teste_status = 'ERRO' THEN 1 ELSE 0 END) AS diagnostico_erro_cadastro
            FROM implantacao_integracoes_config
            {where}
            """,
            tuple(params),
        )

    @classmethod
    def buscar_por_id(cls, integracao_id):
        return cls.fetch_one(
            """
            SELECT *
            FROM implantacao_integracoes_config
            WHERE id = %s
            """,
            (integracao_id,),
        )

    @classmethod
    def buscar_por_tipo_nome(cls, tipo, nome):
        return cls.fetch_one(
            """
            SELECT *
            FROM implantacao_integracoes_config
            WHERE tipo = %s AND nome = %s
            LIMIT 1
            """,
            (tipo, nome),
        )

    @classmethod
    def buscar_ativa_por_tipo(cls, tipo):
        return cls.fetch_one(
            """
            SELECT *
            FROM implantacao_integracoes_config
            WHERE tipo = %s AND ativo = 1
            ORDER BY
                CASE WHEN ultimo_teste_status = 'OK' THEN 0 ELSE 1 END,
                updated_at DESC,
                id DESC
            LIMIT 1
            """,
            (tipo,),
        )

    @classmethod
    def inserir(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO implantacao_integracoes_config (
                uuid, tipo, nome, base_url, usuario, token_nome, segredo_encrypted,
                verify_ssl, timeout_seconds, ativo, observacoes, created_by, updated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("tipo"), dados.get("nome"), dados.get("base_url"),
                dados.get("usuario"), dados.get("token_nome"), dados.get("segredo_encrypted"),
                cls.bool_to_int(dados.get("verify_ssl", True)), dados.get("timeout_seconds"),
                cls.bool_to_int(dados.get("ativo", True)), dados.get("observacoes"),
                dados.get("created_by"), dados.get("updated_by"),
            ),
        )

    @classmethod
    def atualizar(cls, integracao_id, dados):
        return cls.execute(
            """
            UPDATE implantacao_integracoes_config
            SET tipo=%s, nome=%s, base_url=%s, usuario=%s, token_nome=%s,
                segredo_encrypted=COALESCE(%s, segredo_encrypted), verify_ssl=%s,
                timeout_seconds=%s, ativo=%s, observacoes=%s, updated_by=%s
            WHERE id=%s
            """,
            (
                dados.get("tipo"), dados.get("nome"), dados.get("base_url"),
                dados.get("usuario"), dados.get("token_nome"), dados.get("segredo_encrypted"),
                cls.bool_to_int(dados.get("verify_ssl", True)), dados.get("timeout_seconds"),
                cls.bool_to_int(dados.get("ativo", True)), dados.get("observacoes"),
                dados.get("updated_by"), integracao_id,
            ),
        )

    @classmethod
    def registrar_teste(cls, integracao_id, status, mensagem, usuario_email=None):
        conn = cls.connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE implantacao_integracoes_config
                SET ultimo_teste_status=%s,
                    ultimo_teste_mensagem=%s,
                    ultimo_teste_em=NOW()
                WHERE id=%s
                """,
                (status, mensagem, integracao_id),
            )
            cursor.execute(
                """
                INSERT INTO implantacao_integracoes_validacoes (
                    uuid, integracao_id, status, mensagem, validado_por
                ) VALUES (%s, %s, %s, %s, %s)
                """,
                (cls.generate_uuid(), integracao_id, status, mensagem, usuario_email or "sistema"),
            )
            conn.commit()
            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            cls.close(conn, cursor)

    @classmethod
    def listar_validacoes_recentes(cls, tipos=None, limite=10):
        sql = """
            SELECT v.id, v.integracao_id, v.status, v.mensagem, v.validado_por, v.validado_em,
                   i.tipo, i.nome
            FROM implantacao_integracoes_validacoes v
            JOIN implantacao_integracoes_config i ON i.id = v.integracao_id
            WHERE 1 = 1
        """
        params = []
        if tipos:
            placeholders = ", ".join(["%s"] * len(tipos))
            sql += f" AND i.tipo IN ({placeholders})"
            params.extend(tipos)
        sql += " ORDER BY v.validado_em DESC, v.id DESC LIMIT %s"
        params.append(int(limite or 10))
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def listar_historico(cls, integracao_id, limite=10):
        limite = max(1, min(int(limite or 10), 50))
        return cls.fetch_all(
            f"""
            SELECT id, status, mensagem, validado_por, validado_em
            FROM implantacao_integracoes_validacoes
            WHERE integracao_id = %s
            ORDER BY validado_em DESC, id DESC
            LIMIT {limite}
            """,
            (integracao_id,),
        )

    @classmethod
    def inativar(cls, integracao_id, usuario_email=None):
        return cls.execute(
            """
            UPDATE implantacao_integracoes_config
            SET ativo = 0, updated_by = %s
            WHERE id = %s
            """,
            (usuario_email, integracao_id),
        )
