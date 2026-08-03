CREATE TABLE IF NOT EXISTS truenas_backup_cache (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    ambiente_id BIGINT NULL,
    prefixo_proxmox VARCHAR(120) NOT NULL,
    cliente_nome VARCHAR(180) NULL,
    mountpoint VARCHAR(40) NOT NULL,
    pasta_path VARCHAR(500) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'ALERTA',
    arquivos_recentes INT NOT NULL DEFAULT 0,
    arquivos_total INT NOT NULL DEFAULT 0,
    ultimo_arquivo VARCHAR(255) NULL,
    ultimo_mtime DATETIME NULL,
    detalhes LONGTEXT NULL,
    sincronizado_em DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_truenas_backup_cache_pasta (integracao_id, pasta_path),
    KEY idx_truenas_backup_cache_status (status, ultimo_mtime),
    KEY idx_truenas_backup_cache_prefixo (prefixo_proxmox),
    CONSTRAINT fk_truenas_backup_cache_integracao
        FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_truenas_backup_cache_ambiente
        FOREIGN KEY (ambiente_id)
        REFERENCES ambientes (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
