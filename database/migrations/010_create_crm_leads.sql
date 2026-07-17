CREATE TABLE IF NOT EXISTS crm_leads (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    parceiro_id BIGINT NULL,
    executivo_responsavel_id BIGINT NULL,
    empresa VARCHAR(150) NOT NULL,
    nome_contato VARCHAR(150) NOT NULL,
    cargo VARCHAR(120) NULL,
    email VARCHAR(150) NULL,
    telefone VARCHAR(30) NULL,
    origem VARCHAR(40) NOT NULL DEFAULT 'OUTRO',
    interesse VARCHAR(200) NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'NOVO',
    cidade VARCHAR(120) NULL,
    uf CHAR(2) NULL,
    observacoes TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_crm_leads_parceiro
        FOREIGN KEY (parceiro_id)
        REFERENCES parceiros (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_crm_leads_executivo
        FOREIGN KEY (executivo_responsavel_id)
        REFERENCES parceiros_executivos (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    KEY idx_crm_leads_empresa (empresa),
    KEY idx_crm_leads_status (status),
    KEY idx_crm_leads_origem (origem),
    KEY idx_crm_leads_ativo (ativo),
    KEY idx_crm_leads_parceiro_id (parceiro_id),
    KEY idx_crm_leads_executivo_id (executivo_responsavel_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
