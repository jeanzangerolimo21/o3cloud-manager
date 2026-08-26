CREATE TABLE IF NOT EXISTS implantacao_faixas_rede_portas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    faixa_rede_id BIGINT NOT NULL,
    porta_inicio INT NOT NULL,
    porta_fim INT NOT NULL,
    portas VARCHAR(32) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_implantacao_faixas_portas_faixa_id (faixa_rede_id),
    KEY idx_implantacao_faixas_portas_range (porta_inicio, porta_fim),
    CONSTRAINT fk_implantacao_faixas_portas_faixa
        FOREIGN KEY (faixa_rede_id)
        REFERENCES implantacao_faixas_rede (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
