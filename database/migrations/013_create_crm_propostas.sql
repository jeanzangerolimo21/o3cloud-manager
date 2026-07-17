CREATE TABLE IF NOT EXISTS crm_propostas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    oportunidade_id BIGINT NOT NULL,
    titulo VARCHAR(180) NOT NULL,
    versao INT NOT NULL DEFAULT 1,
    status VARCHAR(40) NOT NULL DEFAULT 'RASCUNHO',
    validade DATE NULL,
    valor_total DECIMAL(12,2) NULL,
    condicoes_comerciais TEXT NULL,
    observacoes TEXT NULL,
    itens_snapshot MEDIUMTEXT NULL,
    arquivo VARCHAR(255) NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_crm_propostas_oportunidade
        FOREIGN KEY (oportunidade_id)
        REFERENCES crm_oportunidades (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    KEY idx_crm_propostas_oportunidade_id (oportunidade_id),
    KEY idx_crm_propostas_status (status),
    KEY idx_crm_propostas_ativo (ativo),
    KEY idx_crm_propostas_versao (versao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
