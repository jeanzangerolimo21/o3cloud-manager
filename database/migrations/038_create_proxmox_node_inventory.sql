CREATE TABLE IF NOT EXISTS proxmox_node_inventory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    node VARCHAR(120) NOT NULL,
    status VARCHAR(40) NULL,
    cpu_total DECIMAL(10,2) NULL,
    cpu_usado_percent DECIMAL(10,2) NULL,
    memoria_total_mb BIGINT NULL,
    memoria_usada_mb BIGINT NULL,
    memoria_disponivel_mb BIGINT NULL,
    disco_total_gb DECIMAL(15,2) NULL,
    disco_usado_gb DECIMAL(15,2) NULL,
    uptime_seconds BIGINT NULL,
    pve_version VARCHAR(120) NULL,
    raw_payload LONGTEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    ultimo_sync_em DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_proxmox_node_inventory_integracao_node (integracao_id, node),
    KEY idx_proxmox_node_inventory_status (status, ativo),
    CONSTRAINT fk_proxmox_node_inventory_integracao
        FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
