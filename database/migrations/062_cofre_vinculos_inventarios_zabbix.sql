CREATE TABLE IF NOT EXISTS zabbix_host_inventory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    hostid VARCHAR(120) NOT NULL,
    host VARCHAR(180) NULL,
    nome VARCHAR(255) NULL,
    status VARCHAR(40) NULL,
    interfaces TEXT NULL,
    cliente_id BIGINT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    ultimo_sync_em DATETIME NULL,
    raw_payload LONGTEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_zabbix_host_integracao (integracao_id, hostid),
    KEY idx_zabbix_host_ativo (ativo),
    KEY idx_zabbix_host_cliente (cliente_id),
    CONSTRAINT fk_zabbix_host_integracao FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_zabbix_host_cliente FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE implantacao_cofre_senhas
    ADD COLUMN IF NOT EXISTS proxmox_node_inventory_id BIGINT NULL AFTER zabbix_host_id,
    ADD COLUMN IF NOT EXISTS proxmox_inventory_id BIGINT NULL AFTER proxmox_node_inventory_id,
    ADD COLUMN IF NOT EXISTS pbs_backup_snapshot_id BIGINT NULL AFTER proxmox_inventory_id,
    ADD COLUMN IF NOT EXISTS zabbix_host_inventory_id BIGINT NULL AFTER pbs_backup_snapshot_id;

ALTER TABLE implantacao_cofre_senhas
    ADD KEY idx_cofre_proxmox_node_inventory (proxmox_node_inventory_id),
    ADD KEY idx_cofre_proxmox_inventory (proxmox_inventory_id),
    ADD KEY idx_cofre_pbs_snapshot (pbs_backup_snapshot_id),
    ADD KEY idx_cofre_zabbix_host_inventory (zabbix_host_inventory_id);

ALTER TABLE implantacao_cofre_senhas
    ADD CONSTRAINT fk_cofre_proxmox_node_inventory
        FOREIGN KEY (proxmox_node_inventory_id) REFERENCES proxmox_node_inventory(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    ADD CONSTRAINT fk_cofre_proxmox_inventory
        FOREIGN KEY (proxmox_inventory_id) REFERENCES proxmox_vm_inventory(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    ADD CONSTRAINT fk_cofre_pbs_snapshot
        FOREIGN KEY (pbs_backup_snapshot_id) REFERENCES pbs_backup_snapshots(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    ADD CONSTRAINT fk_cofre_zabbix_host_inventory
        FOREIGN KEY (zabbix_host_inventory_id) REFERENCES zabbix_host_inventory(id)
        ON DELETE SET NULL ON UPDATE CASCADE;
