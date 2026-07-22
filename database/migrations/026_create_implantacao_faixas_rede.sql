CREATE TABLE IF NOT EXISTS implantacao_faixas_rede (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    rede VARCHAR(43) NOT NULL,
    mascara TINYINT UNSIGNED NOT NULL,
    quantidade_servidores INT NOT NULL DEFAULT 0,
    fw_wan VARCHAR(45) NULL,
    fw_lan VARCHAR(45) NULL,
    cliente_id BIGINT NULL,
    cliente_nome VARCHAR(180) NOT NULL,
    cliente_cnpj VARCHAR(20) NULL,
    vpn VARCHAR(120) NULL,
    porta_inicio INT NULL,
    porta_fim INT NULL,
    portas VARCHAR(255) NULL,
    pve VARCHAR(255) NULL,
    observacoes TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_implantacao_faixas_rede_rede (rede),
    KEY idx_implantacao_faixas_rede_cliente_id (cliente_id),
    KEY idx_implantacao_faixas_rede_cliente_nome (cliente_nome),
    KEY idx_implantacao_faixas_rede_mascara (mascara),
    KEY idx_implantacao_faixas_rede_fw_portas (fw_wan, porta_inicio, porta_fim),
    KEY idx_implantacao_faixas_rede_ativo (ativo),
    CONSTRAINT fk_implantacao_faixas_rede_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
