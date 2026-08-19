import json

from app.repositories.base_repository import BaseRepository


class PBSBackupRepository(BaseRepository):
    @classmethod
    def listar_integracoes_pbs(cls):
        return cls.fetch_all(
            """
            SELECT id, nome, base_url, ativo
            FROM implantacao_integracoes_config
            WHERE tipo = 'pbs' AND ativo = 1
            ORDER BY nome ASC, id ASC
            """
        )

    @classmethod
    def listar_escopos(cls, ativo=True):
        sql = """
            SELECT e.*, i.nome AS integracao_nome, i.base_url AS integracao_base_url
            FROM pbs_backup_escopos e
            JOIN implantacao_integracoes_config i ON i.id = e.integracao_id
            WHERE i.tipo = 'pbs'
        """
        params = []
        if ativo is not None:
            sql += " AND e.ativo = %s"
            params.append(1 if ativo else 0)
        sql += " ORDER BY e.ativo DESC, e.nome ASC, e.id ASC"
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def buscar_escopo(cls, escopo_id):
        return cls.fetch_one(
            """
            SELECT e.*, i.nome AS integracao_nome, i.base_url AS integracao_base_url
            FROM pbs_backup_escopos e
            JOIN implantacao_integracoes_config i ON i.id = e.integracao_id
            WHERE e.id = %s AND i.tipo = 'pbs'
            """,
            (escopo_id,),
        )

    @classmethod
    def inserir_escopo(cls, dados):
        return cls.execute_insert(
            """
            INSERT INTO pbs_backup_escopos (uuid, integracao_id, nome, datastore, namespaces, ativo, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                cls.generate_uuid(), dados.get("integracao_id"), dados.get("nome"),
                dados.get("datastore"), dados.get("namespaces"),
                cls.bool_to_int(dados.get("ativo", 1)), dados.get("observacoes"),
            ),
        )

    @classmethod
    def atualizar_escopo(cls, escopo_id, dados):
        return cls.execute(
            """
            UPDATE pbs_backup_escopos
            SET integracao_id=%s, nome=%s, datastore=%s, namespaces=%s, ativo=%s, observacoes=%s
            WHERE id=%s
            """,
            (
                dados.get("integracao_id"), dados.get("nome"), dados.get("datastore"),
                dados.get("namespaces"), cls.bool_to_int(dados.get("ativo", 1)),
                dados.get("observacoes"), escopo_id,
            ),
        )

    @classmethod
    def inativar_escopo(cls, escopo_id):
        return cls.execute(
            "UPDATE pbs_backup_escopos SET ativo = 0 WHERE id = %s",
            (escopo_id,),
        )

    @classmethod
    def listar_recursos(cls, pesquisa=None, status=None, tipo=None, node=None):
        sql = """
            SELECT
                p.id, p.node, p.vmid, p.tipo, p.nome, p.status AS vm_status, p.ultimo_sync_em,
                COALESCE(pol.frequencia_horas, 24) AS frequencia_horas,
                ult.ultimo_backup_em, COALESCE(ult.backups_total, 0) AS backups_total,
                ult.datastore, ult.namespace,
                (
                    SELECT GROUP_CONCAT(DISTINCT a.nome ORDER BY a.nome SEPARATOR ', ')
                    FROM ambiente_proxmox_recursos apr
                    JOIN ambientes a ON a.id = apr.ambiente_id AND a.ativo = 1
                    WHERE apr.proxmox_inventory_id = p.id
                ) AS ambiente_nomes,
                (
                    SELECT GROUP_CONCAT(DISTINCT cli.nome_fantasia ORDER BY cli.nome_fantasia SEPARATOR ', ')
                    FROM ambiente_proxmox_recursos apr
                    JOIN ambiente_clientes ac ON ac.ambiente_id = apr.ambiente_id
                    JOIN clientes cli ON cli.id = ac.cliente_id
                    WHERE apr.proxmox_inventory_id = p.id
                ) AS cliente_nomes
            FROM proxmox_vm_inventory p
            LEFT JOIN (
                SELECT proxmox_inventory_id, MAX(frequencia_horas) AS frequencia_horas
                FROM pbs_backup_politicas
                GROUP BY proxmox_inventory_id
            ) pol ON pol.proxmox_inventory_id = p.id
            LEFT JOIN (
                SELECT s.proxmox_inventory_id, COUNT(*) AS backups_total, MAX(s.backup_time) AS ultimo_backup_em,
                       SUBSTRING_INDEX(GROUP_CONCAT(s.datastore ORDER BY s.backup_time DESC), ',', 1) AS datastore,
                       SUBSTRING_INDEX(GROUP_CONCAT(s.namespace ORDER BY s.backup_time DESC), ',', 1) AS namespace
                FROM pbs_backup_snapshots s
                WHERE s.proxmox_inventory_id IS NOT NULL
                GROUP BY s.proxmox_inventory_id
            ) ult ON ult.proxmox_inventory_id = p.id
            WHERE p.ativo = 1
        """
        params = []
        if tipo:
            sql += " AND p.tipo = %s"
            params.append(tipo)
        if node:
            sql += " AND p.node = %s"
            params.append(node)
        if pesquisa:
            termo = f"%{pesquisa}%"
            sql += " AND (p.nome LIKE %s OR CAST(p.vmid AS CHAR) LIKE %s OR p.node LIKE %s)"
            params.extend([termo, termo, termo])
        if status == "com_alerta":
            sql += " AND (ult.ultimo_backup_em IS NULL OR TIMESTAMPDIFF(HOUR, ult.ultimo_backup_em, UTC_TIMESTAMP()) > COALESCE(pol.frequencia_horas, 24))"
        elif status == "ok":
            sql += " AND ult.ultimo_backup_em IS NOT NULL AND TIMESTAMPDIFF(HOUR, ult.ultimo_backup_em, UTC_TIMESTAMP()) <= COALESCE(pol.frequencia_horas, 24)"
        elif status == "sem_backup":
            sql += " AND ult.ultimo_backup_em IS NULL"
        sql += " ORDER BY p.node ASC, p.tipo ASC, p.vmid ASC"
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def dashboard(cls):
        return cls.fetch_one(
            """
            SELECT COUNT(*) AS total_recursos,
                   SUM(CASE WHEN ult.ultimo_backup_em IS NULL THEN 1 ELSE 0 END) AS sem_backup,
                   SUM(CASE WHEN ult.ultimo_backup_em IS NOT NULL AND TIMESTAMPDIFF(HOUR, ult.ultimo_backup_em, UTC_TIMESTAMP()) <= COALESCE(pol.frequencia_horas, 24) THEN 1 ELSE 0 END) AS ok_total,
                   SUM(CASE WHEN ult.ultimo_backup_em IS NULL OR TIMESTAMPDIFF(HOUR, ult.ultimo_backup_em, UTC_TIMESTAMP()) > COALESCE(pol.frequencia_horas, 24) THEN 1 ELSE 0 END) AS alerta_total,
                   SUM(CASE WHEN COALESCE(pol.frequencia_horas, 24) >= 168 THEN 1 ELSE 0 END) AS semanais_total,
                   COALESCE(SUM(ult.backups_total), 0) AS backups_total
            FROM proxmox_vm_inventory p
            LEFT JOIN (
                SELECT proxmox_inventory_id, MAX(frequencia_horas) AS frequencia_horas
                FROM pbs_backup_politicas
                GROUP BY proxmox_inventory_id
            ) pol ON pol.proxmox_inventory_id = p.id
            LEFT JOIN (
                SELECT proxmox_inventory_id, COUNT(*) AS backups_total, MAX(backup_time) AS ultimo_backup_em
                FROM pbs_backup_snapshots
                WHERE proxmox_inventory_id IS NOT NULL
                GROUP BY proxmox_inventory_id
            ) ult ON ult.proxmox_inventory_id = p.id
            WHERE p.ativo = 1
            """
        )

    @classmethod
    def listar_nodes_proxmox(cls):
        return cls.fetch_all(
            """
            SELECT DISTINCT node
            FROM proxmox_vm_inventory
            WHERE ativo = 1 AND node IS NOT NULL AND node <> ''
            ORDER BY node
            """
        )

    @classmethod
    def mapa_recursos_por_node(cls):
        recursos = cls.fetch_all(
            """
            SELECT id, node, vmid, tipo
            FROM proxmox_vm_inventory
            WHERE ativo = 1
            """
        )
        mapa = {}
        for item in recursos:
            backup_type = "vm" if item.get("tipo") == "qemu" else "ct"
            chave = (item.get("node"), backup_type, str(item.get("vmid")))
            mapa[chave] = item.get("id")
        return mapa

    @classmethod
    def atualizar_politicas(cls, recurso_ids_semanais, recurso_ids_visiveis=None):
        recurso_ids_semanais = {int(item) for item in recurso_ids_semanais or [] if str(item).isdigit()}
        recurso_ids_visiveis = {int(item) for item in recurso_ids_visiveis or [] if str(item).isdigit()}
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            if recurso_ids_visiveis:
                todos = sorted(recurso_ids_visiveis)
            else:
                cursor.execute("SELECT id FROM proxmox_vm_inventory WHERE ativo = 1")
                todos = [row[0] for row in cursor.fetchall()]
            for recurso_id in todos:
                frequencia = 168 if recurso_id in recurso_ids_semanais else 24
                cursor.execute(
                    """
                    INSERT INTO pbs_backup_politicas (uuid, proxmox_inventory_id, frequencia_horas)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE frequencia_horas=VALUES(frequencia_horas)
                    """,
                    (cls.generate_uuid(), recurso_id, frequencia),
                )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

    @classmethod
    def criar_execucao(cls, integracao_id, datastore, executado_por=None):
        return cls.execute_insert(
            """
            INSERT INTO pbs_backup_sync_execucoes (uuid, integracao_id, datastore, status, iniciada_em, executado_por)
            VALUES (%s, %s, %s, 'EXECUTANDO', UTC_TIMESTAMP(), %s)
            """,
            (cls.generate_uuid(), integracao_id, datastore, executado_por or "sistema"),
        )

    @classmethod
    def finalizar_execucao(cls, execucao_id, status, namespaces_lidos=0, snapshots_lidos=0, snapshots_atualizados=0, mensagem=None):
        return cls.execute(
            """
            UPDATE pbs_backup_sync_execucoes
            SET status=%s, finalizada_em=UTC_TIMESTAMP(), namespaces_lidos=%s, snapshots_lidos=%s, snapshots_atualizados=%s, mensagem=%s
            WHERE id=%s
            """,
            (status, namespaces_lidos, snapshots_lidos, snapshots_atualizados, mensagem, execucao_id),
        )

    @classmethod
    def listar_execucoes(cls, limite=10):
        limite = max(1, min(int(limite or 10), 50))
        return cls.fetch_all(
            f"""
            SELECT e.*, i.nome AS integracao_nome
            FROM pbs_backup_sync_execucoes e
            JOIN implantacao_integracoes_config i ON i.id = e.integracao_id
            ORDER BY e.iniciada_em DESC, e.id DESC
            LIMIT {limite}
            """
        )

    @classmethod
    def salvar_snapshots(cls, snapshots):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            atualizados = 0
            for item in snapshots:
                cursor.execute(
                    """
                    INSERT INTO pbs_backup_snapshots (
                        uuid, integracao_id, proxmox_inventory_id, datastore, namespace, backup_type,
                        backup_id, backup_time, snapshot_name, size_bytes, protected, raw_payload, ultimo_sync_em
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP())
                    ON DUPLICATE KEY UPDATE
                        proxmox_inventory_id=VALUES(proxmox_inventory_id),
                        snapshot_name=VALUES(snapshot_name),
                        size_bytes=VALUES(size_bytes),
                        protected=VALUES(protected),
                        raw_payload=VALUES(raw_payload),
                        ultimo_sync_em=UTC_TIMESTAMP()
                    """,
                    (
                        cls.generate_uuid(), item.get("integracao_id"), item.get("proxmox_inventory_id"),
                        item.get("datastore"), item.get("namespace") or "", item.get("backup_type"),
                        item.get("backup_id"), item.get("backup_time"), item.get("snapshot_name"),
                        item.get("size_bytes"), cls.bool_to_int(item.get("protected")),
                        json.dumps(item.get("raw_payload") or {}, ensure_ascii=False),
                    ),
                )
                atualizados += 1
            conn.commit()
            return atualizados
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)
