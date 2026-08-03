CREATE TABLE IF NOT EXISTS pbs_backup_politicas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    proxmox_inventory_id BIGINT NOT NULL,
    frequencia_horas INT NOT NULL DEFAULT 24,
    observacoes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_pbs_backup_politicas_recurso (proxmox_inventory_id),
    KEY idx_pbs_backup_politicas_freq (frequencia_horas),
    CONSTRAINT fk_pbs_backup_politicas_recurso
        FOREIGN KEY (proxmox_inventory_id)
        REFERENCES proxmox_vm_inventory (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pbs_backup_snapshots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    proxmox_inventory_id BIGINT NULL,
    datastore VARCHAR(120) NOT NULL,
    namespace VARCHAR(180) NOT NULL DEFAULT '',
    backup_type VARCHAR(20) NOT NULL,
    backup_id VARCHAR(120) NOT NULL,
    backup_time DATETIME NOT NULL,
    snapshot_name VARCHAR(255) NOT NULL,
    size_bytes BIGINT NULL,
    protected TINYINT(1) NOT NULL DEFAULT 0,
    raw_payload LONGTEXT NULL,
    ultimo_sync_em DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_pbs_backup_snapshot (integracao_id, datastore, namespace, backup_type, backup_id, backup_time),
    KEY idx_pbs_backup_recurso_time (proxmox_inventory_id, backup_time),
    KEY idx_pbs_backup_datastore_ns (datastore, namespace),
    CONSTRAINT fk_pbs_backup_snapshots_integracao
        FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_pbs_backup_snapshots_recurso
        FOREIGN KEY (proxmox_inventory_id)
        REFERENCES proxmox_vm_inventory (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pbs_backup_sync_execucoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    datastore VARCHAR(120) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'PENDENTE',
    iniciada_em DATETIME NULL,
    finalizada_em DATETIME NULL,
    namespaces_lidos INT NOT NULL DEFAULT 0,
    snapshots_lidos INT NOT NULL DEFAULT 0,
    snapshots_atualizados INT NOT NULL DEFAULT 0,
    mensagem TEXT NULL,
    executado_por VARCHAR(150) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_pbs_backup_sync_integracao_status (integracao_id, status),
    KEY idx_pbs_backup_sync_iniciada (iniciada_em),
    CONSTRAINT fk_pbs_backup_sync_integracao
        FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
