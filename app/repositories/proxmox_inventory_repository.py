import json

from app.repositories.base_repository import BaseRepository


class ProxmoxInventoryRepository(BaseRepository):
    @classmethod
    def listar(cls, tipo=None, status=None, node=None, pesquisa=None):
        sql = """
            SELECT p.id, p.integracao_id, i.base_url, p.node, p.vmid, p.tipo, p.nome, p.status, p.cpu_cores,
                   p.memoria_mb, p.disco_gb, p.discos_qtd, p.interfaces_qtd, p.ips, p.tags,
                   p.template, p.uptime_seconds, p.cliente_id, c.nome_fantasia AS cliente_nome,
                   p.contrato_id, p.implantacao_id, p.ultimo_sync_em, p.ativo,
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
                   ) AS ambiente_clientes,
                   (
                       SELECT GROUP_CONCAT(DISTINCT ct.numero ORDER BY ct.numero SEPARATOR ', ')
                       FROM ambiente_proxmox_recursos apr
                       JOIN ambiente_contratos act ON act.ambiente_id = apr.ambiente_id
                       JOIN contratos ct ON ct.id = act.contrato_id
                       WHERE apr.proxmox_inventory_id = p.id
                   ) AS ambiente_contratos
            FROM proxmox_vm_inventory p
            JOIN implantacao_integracoes_config i ON i.id = p.integracao_id
            LEFT JOIN clientes c ON c.id = p.cliente_id
            WHERE p.ativo = 1
        """
        params = []
        if tipo:
            sql += " AND p.tipo = %s"
            params.append(tipo)
        if status:
            sql += " AND p.status = %s"
            params.append(status)
        if node:
            sql += " AND p.node = %s"
            params.append(node)
        if pesquisa:
            sql += " AND (p.nome LIKE %s OR CAST(p.vmid AS CHAR) LIKE %s OR p.tags LIKE %s OR c.nome_fantasia LIKE %s)"
            termo = f"%{pesquisa}%"
            params.extend([termo, termo, termo, termo])
        sql += " ORDER BY p.node ASC, p.vmid ASC"
        return cls.fetch_all(sql, tuple(params))

    @classmethod
    def dashboard(cls, tipo=None):
        where = "WHERE p.ativo = 1"
        params = []
        if tipo:
            where += " AND p.tipo = %s"
            params.append(tipo)
        return cls.fetch_one(
            f"""
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN tipo = 'qemu' THEN 1 ELSE 0 END) AS qemu,
                   SUM(CASE WHEN tipo = 'lxc' THEN 1 ELSE 0 END) AS lxc,
                   SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) AS running,
                   SUM(CASE WHEN status = 'stopped' THEN 1 ELSE 0 END) AS stopped,
                   COUNT(DISTINCT node) AS nodes,
                   COALESCE(SUM(cpu_cores), 0) AS cpu_total,
                   COALESCE(SUM(memoria_mb), 0) AS memoria_total_mb,
                   COALESCE(SUM(disco_gb), 0) AS disco_total_gb,
                   COALESCE(SUM(discos_qtd), 0) AS discos_total,
                   COALESCE(SUM(interfaces_qtd), 0) AS interfaces_total,
                   SUM(CASE WHEN NOT EXISTS (
                       SELECT 1 FROM ambiente_proxmox_recursos apr
                       WHERE apr.proxmox_inventory_id = p.id
                   ) THEN 1 ELSE 0 END) AS sem_cliente,
                   SUM(CASE WHEN EXISTS (
                       SELECT 1 FROM ambiente_proxmox_recursos apr
                       WHERE apr.proxmox_inventory_id = p.id
                   ) THEN 1 ELSE 0 END) AS com_cliente
            FROM proxmox_vm_inventory p
            {where}
            """,
            tuple(params),
        )

    @classmethod
    def listar_clusters_dashboard(cls):
        return cls.fetch_all(
            """
            SELECT
                i.id,
                i.nome,
                i.base_url,
                i.ativo,
                i.ultimo_teste_status,
                i.ultimo_teste_em,
                COALESCE(n.nodes_total, 0) AS nodes_total,
                COALESCE(n.online_total, 0) AS online_total,
                COALESCE(n.cpu_total, 0) AS cpu_total,
                COALESCE(n.cpu_consumida, 0) AS cpu_consumida,
                COALESCE(n.memoria_total_mb, 0) AS memoria_total_mb,
                COALESCE(n.memoria_usada_mb, 0) AS memoria_usada_mb,
                COALESCE(n.memoria_disponivel_mb, 0) AS memoria_disponivel_mb,
                COALESCE(n.disco_total_gb, 0) AS disco_total_gb,
                COALESCE(n.disco_usado_gb, 0) AS disco_usado_gb,
                COALESCE(n.disco_disponivel_gb, 0) AS disco_disponivel_gb,
                COALESCE(v.recursos_total, 0) AS recursos_total,
                COALESCE(v.qemu_total, 0) AS qemu_total,
                COALESCE(v.lxc_total, 0) AS lxc_total,
                COALESCE(v.running_total, 0) AS running_total,
                COALESCE(v.cpu_alocada, 0) AS cpu_alocada,
                COALESCE(v.memoria_alocada_mb, 0) AS memoria_alocada_mb,
                COALESCE(v.disco_alocado_gb, 0) AS disco_alocado_gb,
                COALESCE(v.discos_total, 0) AS discos_total,
                COALESCE(v.interfaces_total, 0) AS interfaces_total,
                COALESCE(n.ultimo_sync_em, v.ultimo_sync_em) AS ultimo_sync_em
            FROM implantacao_integracoes_config i
            LEFT JOIN (
                SELECT
                    integracao_id,
                    COUNT(*) AS nodes_total,
                    SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) AS online_total,
                    COALESCE(SUM(cpu_total), 0) AS cpu_total,
                    COALESCE(SUM(COALESCE(cpu_total, 0) * COALESCE(cpu_usado_percent, 0) / 100), 0) AS cpu_consumida,
                    COALESCE(SUM(memoria_total_mb), 0) AS memoria_total_mb,
                    COALESCE(SUM(memoria_usada_mb), 0) AS memoria_usada_mb,
                    COALESCE(SUM(memoria_disponivel_mb), 0) AS memoria_disponivel_mb,
                    COALESCE(SUM(disco_total_gb), 0) AS disco_total_gb,
                    COALESCE(SUM(disco_usado_gb), 0) AS disco_usado_gb,
                    COALESCE(SUM(disco_disponivel_gb), 0) AS disco_disponivel_gb,
                    MAX(ultimo_sync_em) AS ultimo_sync_em
                FROM proxmox_node_inventory
                WHERE ativo = 1
                GROUP BY integracao_id
            ) n ON n.integracao_id = i.id
            LEFT JOIN (
                SELECT
                    integracao_id,
                    COUNT(*) AS recursos_total,
                    SUM(CASE WHEN tipo = 'qemu' THEN 1 ELSE 0 END) AS qemu_total,
                    SUM(CASE WHEN tipo = 'lxc' THEN 1 ELSE 0 END) AS lxc_total,
                    SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) AS running_total,
                    COALESCE(SUM(cpu_cores), 0) AS cpu_alocada,
                    COALESCE(SUM(memoria_mb), 0) AS memoria_alocada_mb,
                    COALESCE(SUM(disco_gb), 0) AS disco_alocado_gb,
                    COALESCE(SUM(discos_qtd), 0) AS discos_total,
                    COALESCE(SUM(interfaces_qtd), 0) AS interfaces_total,
                    MAX(ultimo_sync_em) AS ultimo_sync_em
                FROM proxmox_vm_inventory
                WHERE ativo = 1
                GROUP BY integracao_id
            ) v ON v.integracao_id = i.id
            WHERE i.tipo = 'proxmox'
              AND i.ativo = 1
            ORDER BY i.nome ASC, i.id ASC
            """
        )

    @classmethod
    def dashboard_clusters(cls):
        return cls.fetch_one(
            """
            SELECT
                COUNT(DISTINCT i.id) AS clusters_total,
                COALESCE(SUM(n.nodes_total), 0) AS nodes_total,
                COALESCE(SUM(n.online_total), 0) AS online_total,
                COALESCE(SUM(n.cpu_total), 0) AS cpu_total,
                COALESCE(SUM(n.cpu_consumida), 0) AS cpu_consumida,
                COALESCE(SUM(n.memoria_total_mb), 0) AS memoria_total_mb,
                COALESCE(SUM(n.memoria_usada_mb), 0) AS memoria_usada_mb,
                COALESCE(SUM(n.disco_total_gb), 0) AS disco_total_gb,
                COALESCE(SUM(n.disco_usado_gb), 0) AS disco_usado_gb,
                COALESCE(SUM(v.recursos_total), 0) AS recursos_total,
                COALESCE(SUM(v.cpu_alocada), 0) AS cpu_alocada,
                COALESCE(SUM(v.memoria_alocada_mb), 0) AS memoria_alocada_mb,
                COALESCE(SUM(v.disco_alocado_gb), 0) AS disco_alocado_gb
            FROM implantacao_integracoes_config i
            LEFT JOIN (
                SELECT integracao_id, COUNT(*) AS nodes_total,
                       SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) AS online_total,
                       COALESCE(SUM(cpu_total), 0) AS cpu_total,
                       COALESCE(SUM(COALESCE(cpu_total, 0) * COALESCE(cpu_usado_percent, 0) / 100), 0) AS cpu_consumida,
                       COALESCE(SUM(memoria_total_mb), 0) AS memoria_total_mb,
                       COALESCE(SUM(memoria_usada_mb), 0) AS memoria_usada_mb,
                       COALESCE(SUM(disco_total_gb), 0) AS disco_total_gb,
                       COALESCE(SUM(disco_usado_gb), 0) AS disco_usado_gb
                FROM proxmox_node_inventory
                WHERE ativo = 1
                GROUP BY integracao_id
            ) n ON n.integracao_id = i.id
            LEFT JOIN (
                SELECT integracao_id, COUNT(*) AS recursos_total,
                       COALESCE(SUM(cpu_cores), 0) AS cpu_alocada,
                       COALESCE(SUM(memoria_mb), 0) AS memoria_alocada_mb,
                       COALESCE(SUM(disco_gb), 0) AS disco_alocado_gb
                FROM proxmox_vm_inventory
                WHERE ativo = 1
                GROUP BY integracao_id
            ) v ON v.integracao_id = i.id
            WHERE i.tipo = 'proxmox'
              AND i.ativo = 1
            """
        )

    @classmethod
    def listar_nodes_por_cluster(cls):
        return cls.fetch_all(
            """
            SELECT n.id, n.integracao_id, i.nome AS cluster_nome, i.base_url, n.node, n.status,
                   n.cpu_total, n.cpu_usado_percent, n.memoria_total_mb, n.memoria_usada_mb,
                   n.memoria_disponivel_mb, n.disco_total_gb, n.disco_usado_gb,
                   n.disco_disponivel_gb, n.storages_qtd, n.uptime_seconds, n.pve_version,
                   n.ultimo_sync_em,
                   COUNT(v.id) AS recursos_total,
                   SUM(CASE WHEN v.tipo = 'qemu' THEN 1 ELSE 0 END) AS qemu_total,
                   SUM(CASE WHEN v.tipo = 'lxc' THEN 1 ELSE 0 END) AS lxc_total,
                   SUM(CASE WHEN v.status = 'running' THEN 1 ELSE 0 END) AS running_total,
                   COALESCE(SUM(v.cpu_cores), 0) AS cpu_alocada,
                   COALESCE(SUM(v.memoria_mb), 0) AS memoria_alocada_mb,
                   COALESCE(SUM(v.disco_gb), 0) AS disco_alocado_gb
            FROM proxmox_node_inventory n
            JOIN implantacao_integracoes_config i ON i.id = n.integracao_id
            LEFT JOIN proxmox_vm_inventory v ON v.integracao_id = n.integracao_id
                AND v.node = n.node
                AND v.ativo = 1
            WHERE n.ativo = 1
              AND i.tipo = 'proxmox'
              AND i.ativo = 1
            GROUP BY n.id, n.integracao_id, i.nome, i.base_url, n.node, n.status, n.cpu_total,
                     n.cpu_usado_percent, n.memoria_total_mb, n.memoria_usada_mb,
                     n.memoria_disponivel_mb, n.disco_total_gb, n.disco_usado_gb,
                     n.disco_disponivel_gb, n.storages_qtd, n.uptime_seconds, n.pve_version,
                     n.ultimo_sync_em
            ORDER BY i.nome ASC, n.node ASC
            """
        )

    @classmethod
    def listar_nodes_dashboard(cls):
        return cls.fetch_all(
            """
            SELECT n.id, n.node, i.base_url, n.status, n.cpu_total, n.cpu_usado_percent,
                   n.memoria_total_mb, n.memoria_usada_mb, n.memoria_disponivel_mb,
                   n.disco_total_gb, n.disco_usado_gb, n.disco_disponivel_gb, n.storages_qtd,
                   n.uptime_seconds, n.pve_version, n.raw_payload,
                   n.ultimo_sync_em,
                   COUNT(v.id) AS recursos_total,
                   SUM(CASE WHEN v.tipo = 'qemu' THEN 1 ELSE 0 END) AS qemu_total,
                   SUM(CASE WHEN v.tipo = 'lxc' THEN 1 ELSE 0 END) AS lxc_total,
                   SUM(CASE WHEN v.status = 'running' THEN 1 ELSE 0 END) AS running_total,
                   COALESCE(SUM(v.cpu_cores), 0) AS cpu_alocada,
                   COALESCE(SUM(v.memoria_mb), 0) AS memoria_alocada_mb,
                   COALESCE(SUM(v.disco_gb), 0) AS disco_alocado_gb,
                   COALESCE(SUM(v.discos_qtd), 0) AS discos_total,
                   COALESCE(SUM(v.interfaces_qtd), 0) AS interfaces_total,
                   SUM(CASE WHEN NOT EXISTS (
                       SELECT 1 FROM ambiente_proxmox_recursos apr
                       WHERE apr.proxmox_inventory_id = v.id
                   ) THEN 1 ELSE 0 END) AS sem_cliente
            FROM proxmox_node_inventory n
            JOIN implantacao_integracoes_config i ON i.id = n.integracao_id
            LEFT JOIN proxmox_vm_inventory v ON v.integracao_id = n.integracao_id
                AND v.node = n.node
                AND v.ativo = 1
            WHERE n.ativo = 1
            GROUP BY n.id, n.node, i.base_url, n.status, n.cpu_total, n.cpu_usado_percent,
                     n.memoria_total_mb, n.memoria_usada_mb, n.memoria_disponivel_mb,
                     n.disco_total_gb, n.disco_usado_gb, n.disco_disponivel_gb, n.storages_qtd,
                     n.uptime_seconds, n.pve_version, n.raw_payload,
                     n.ultimo_sync_em
            ORDER BY n.node ASC
            """
        )

    @classmethod
    def dashboard_nodes(cls):
        return cls.fetch_one(
            """
            SELECT COUNT(*) AS nodes_total,
                   SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) AS online_total,
                   COALESCE(SUM(cpu_total), 0) AS cpu_total,
                   COALESCE(SUM(memoria_total_mb), 0) AS memoria_total_mb,
                   COALESCE(SUM(memoria_usada_mb), 0) AS memoria_usada_mb,
                   COALESCE(SUM(memoria_disponivel_mb), 0) AS memoria_disponivel_mb,
                   COALESCE(SUM(disco_total_gb), 0) AS disco_total_gb,
                   COALESCE(SUM(disco_usado_gb), 0) AS disco_usado_gb,
                   COALESCE(SUM(disco_disponivel_gb), 0) AS disco_disponivel_gb,
                   COALESCE(SUM(storages_qtd), 0) AS storages_qtd
            FROM proxmox_node_inventory
            WHERE ativo = 1
            """
        )

    @classmethod
    def salvar_nodes(cls, integracao_id, nodes):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE proxmox_node_inventory SET ativo = 0 WHERE integracao_id = %s",
                (integracao_id,),
            )
            atualizados = 0
            for item in nodes:
                cursor.execute(
                    """
                    INSERT INTO proxmox_node_inventory (
                        uuid, integracao_id, node, status, cpu_total, cpu_usado_percent,
                        memoria_total_mb, memoria_usada_mb, memoria_disponivel_mb,
                        disco_total_gb, disco_usado_gb, disco_disponivel_gb, storages_qtd,
                        uptime_seconds, pve_version, raw_payload, ativo, ultimo_sync_em
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW())
                    ON DUPLICATE KEY UPDATE
                        status=VALUES(status), cpu_total=VALUES(cpu_total),
                        cpu_usado_percent=VALUES(cpu_usado_percent),
                        memoria_total_mb=VALUES(memoria_total_mb),
                        memoria_usada_mb=VALUES(memoria_usada_mb),
                        memoria_disponivel_mb=VALUES(memoria_disponivel_mb),
                        disco_total_gb=VALUES(disco_total_gb),
                        disco_usado_gb=VALUES(disco_usado_gb),
                        disco_disponivel_gb=VALUES(disco_disponivel_gb),
                        storages_qtd=VALUES(storages_qtd),
                        uptime_seconds=VALUES(uptime_seconds), pve_version=VALUES(pve_version),
                        raw_payload=VALUES(raw_payload), ativo=1, ultimo_sync_em=NOW()
                    """,
                    (
                        cls.generate_uuid(), integracao_id, item.get("node"), item.get("status"),
                        item.get("cpu_total"), item.get("cpu_usado_percent"),
                        item.get("memoria_total_mb"), item.get("memoria_usada_mb"),
                        item.get("memoria_disponivel_mb"), item.get("disco_total_gb"),
                        item.get("disco_usado_gb"), item.get("disco_disponivel_gb"),
                        item.get("storages_qtd"), item.get("uptime_seconds"), item.get("pve_version"),
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

    @classmethod
    def listar_nodes(cls):
        return cls.fetch_all(
            """
            SELECT DISTINCT node
            FROM proxmox_vm_inventory
            WHERE ativo = 1
            ORDER BY node ASC
            """
        )

    @classmethod
    def listar_execucoes(cls, limite=10):
        limite = max(1, min(int(limite or 10), 50))
        return cls.fetch_all(
            f"""
            SELECT e.id, e.integracao_id, e.modo, e.status, e.iniciada_em, e.finalizada_em,
                   e.vms_lidas, e.vms_atualizadas, e.mensagem, e.executado_por, i.nome AS integracao_nome
            FROM proxmox_vm_sync_execucoes e
            JOIN implantacao_integracoes_config i ON i.id = e.integracao_id
            ORDER BY e.iniciada_em DESC, e.id DESC
            LIMIT {limite}
            """
        )

    @classmethod
    def criar_execucao(cls, integracao_id, executado_por=None):
        return cls.execute_insert(
            """
            INSERT INTO proxmox_vm_sync_execucoes (uuid, integracao_id, modo, status, iniciada_em, executado_por)
            VALUES (%s, %s, 'MANUAL', 'EXECUTANDO', NOW(), %s)
            """,
            (cls.generate_uuid(), integracao_id, executado_por or "sistema"),
        )

    @classmethod
    def finalizar_execucao(cls, execucao_id, status, lidas=0, atualizadas=0, mensagem=None):
        return cls.execute(
            """
            UPDATE proxmox_vm_sync_execucoes
            SET status=%s, finalizada_em=NOW(), vms_lidas=%s, vms_atualizadas=%s, mensagem=%s
            WHERE id=%s
            """,
            (status, int(lidas or 0), int(atualizadas or 0), mensagem, execucao_id),
        )

    @classmethod
    def salvar_inventario(cls, integracao_id, recursos):
        conn = cls.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE proxmox_vm_inventory SET ativo = 0 WHERE integracao_id = %s",
                (integracao_id,),
            )
            atualizadas = 0
            for item in recursos:
                cursor.execute(
                    """
                    INSERT INTO proxmox_vm_inventory (
                        uuid, integracao_id, node, vmid, tipo, nome, status, cpu_cores,
                        memoria_mb, disco_gb, discos_qtd, interfaces_qtd, ips, tags, template,
                        uptime_seconds, raw_payload, ativo, ultimo_sync_em
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW())
                    ON DUPLICATE KEY UPDATE
                        tipo=VALUES(tipo), nome=VALUES(nome), status=VALUES(status),
                        cpu_cores=VALUES(cpu_cores), memoria_mb=VALUES(memoria_mb),
                        disco_gb=VALUES(disco_gb),
                        discos_qtd=COALESCE(VALUES(discos_qtd), discos_qtd),
                        interfaces_qtd=COALESCE(VALUES(interfaces_qtd), interfaces_qtd),
                        ips=VALUES(ips), tags=VALUES(tags),
                        template=VALUES(template), uptime_seconds=VALUES(uptime_seconds),
                        raw_payload=VALUES(raw_payload), ativo=1, ultimo_sync_em=NOW()
                    """,
                    (
                        cls.generate_uuid(), integracao_id, item["node"], item["vmid"], item["tipo"],
                        item.get("nome"), item.get("status"), item.get("cpu_cores"),
                        item.get("memoria_mb"), item.get("disco_gb"), item.get("discos_qtd"),
                        item.get("interfaces_qtd"), item.get("ips"), item.get("tags"),
                        cls.bool_to_int(item.get("template")), item.get("uptime_seconds"),
                        json.dumps(item.get("raw_payload") or {}, ensure_ascii=False),
                    ),
                )
                atualizadas += 1
            conn.commit()
            return atualizadas
        except Exception:
            conn.rollback()
            raise
        finally:
            cls.close(conn, cursor)

    @classmethod
    def vincular_cliente(cls, inventario_id, cliente_id):
        return cls.execute(
            """
            UPDATE proxmox_vm_inventory
            SET cliente_id = %s
            WHERE id = %s AND ativo = 1
            """,
            (cliente_id or None, inventario_id),
        )
