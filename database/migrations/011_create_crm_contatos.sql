CREATE TABLE IF NOT EXISTS crm_contatos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    lead_id BIGINT NULL,
    parceiro_id BIGINT NULL,
    executivo_responsavel_id BIGINT NULL,
    empresa VARCHAR(150) NULL,
    nome VARCHAR(150) NOT NULL,
    cargo VARCHAR(120) NULL,
    email VARCHAR(150) NULL,
    telefone VARCHAR(30) NULL,
    whatsapp VARCHAR(30) NULL,
    tipo_contato VARCHAR(40) NOT NULL DEFAULT 'COMERCIAL',
    canal_preferido VARCHAR(40) NOT NULL DEFAULT 'WHATSAPP',
    cidade VARCHAR(120) NULL,
    uf CHAR(2) NULL,
    observacoes TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_crm_contatos_lead
        FOREIGN KEY (lead_id)
        REFERENCES crm_leads (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_crm_contatos_parceiro
        FOREIGN KEY (parceiro_id)
        REFERENCES parceiros (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_crm_contatos_executivo
        FOREIGN KEY (executivo_responsavel_id)
        REFERENCES parceiros_executivos (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    KEY idx_crm_contatos_nome (nome),
    KEY idx_crm_contatos_tipo (tipo_contato),
    KEY idx_crm_contatos_ativo (ativo),
    KEY idx_crm_contatos_lead_id (lead_id),
    KEY idx_crm_contatos_parceiro_id (parceiro_id),
    KEY idx_crm_contatos_executivo_id (executivo_responsavel_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
