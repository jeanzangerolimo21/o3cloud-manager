from app.repositories.base_repository import BaseRepository


class TrueNASBackupRepository(BaseRepository):
    @classmethod
    def listar_prefixos_ambientes(cls):
        return cls.fetch_all(
            """
            SELECT a.id AS ambiente_id, a.nome AS ambiente_nome, a.prefixo_proxmox,
                   COALESCE(c.nome_fantasia, c.razao_social) AS cliente_nome
            FROM ambientes a
            JOIN clientes c ON c.id = a.cliente_id
            WHERE a.ativo = 1
              AND a.prefixo_proxmox IS NOT NULL
              AND a.prefixo_proxmox <> ''
            ORDER BY a.prefixo_proxmox ASC, a.id ASC
            """
        )

    @classmethod
    def listar_cache(cls, integracao_id=None):
        sql = """
            SELECT b.*, i.nome AS integracao_nome
            FROM truenas_backup_cache b
            JOIN implantacao_integracoes_config i ON i.id = b.integracao_id
            WHERE 1 = 1
        """
        params = []
        if integracao_id:
            sql += " AND b.integracao_id = %s"
            params.append(integracao_id)
        sql += """
            ORDER BY CASE WHEN b.status = 'ALERTA' THEN 0 ELSE 1 END,
                     b.prefixo_proxmox ASC, b.mountpoint ASC
        """
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def dashboard(cls, integracao_id=None):
        sql = """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN status = 'OK' THEN 1 ELSE 0 END) AS ok_total,
                   SUM(CASE WHEN status = 'ALERTA' THEN 1 ELSE 0 END) AS alerta_total,
                   COALESCE(SUM(arquivos_recentes), 0) AS arquivos_recentes,
                   COALESCE(SUM(arquivos_total), 0) AS arquivos_total,
                   MAX(sincronizado_em) AS ultimo_sync
            FROM truenas_backup_cache
            WHERE 1 = 1
        """
        params = []
        if integracao_id:
            sql += " AND integracao_id = %s"
            params.append(integracao_id)
        return cls.fetch_one(sql, tuple(params))

    @classmethod
    def salvar_cache(cls, integracao_id, registros):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM truenas_backup_cache WHERE integracao_id = %s", (integracao_id,))
            for item in registros:
                cursor.execute(
                    """
                    INSERT INTO truenas_backup_cache (
                        uuid, integracao_id, ambiente_id, prefixo_proxmox, cliente_nome, mountpoint,
                        pasta_path, status, arquivos_recentes, arquivos_total, ultimo_arquivo,
                        ultimo_mtime, detalhes, sincronizado_em
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP())
                    ON DUPLICATE KEY UPDATE
                        ambiente_id=VALUES(ambiente_id), prefixo_proxmox=VALUES(prefixo_proxmox),
                        cliente_nome=VALUES(cliente_nome), mountpoint=VALUES(mountpoint), status=VALUES(status),
                        arquivos_recentes=VALUES(arquivos_recentes), arquivos_total=VALUES(arquivos_total),
                        ultimo_arquivo=VALUES(ultimo_arquivo), ultimo_mtime=VALUES(ultimo_mtime),
                        detalhes=VALUES(detalhes), sincronizado_em=UTC_TIMESTAMP()
                    """,
                    (
                        cls.generate_uuid(), integracao_id, item.get("ambiente_id"), item.get("prefixo_proxmox"),
                        item.get("cliente_nome"), item.get("mountpoint"), item.get("pasta_path"), item.get("status"),
                        item.get("arquivos_recentes"), item.get("arquivos_total"), item.get("ultimo_arquivo"),
                        item.get("ultimo_mtime"), item.get("detalhes"),
                    ),
                )
            conn.commit()
            return len(registros)
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)
