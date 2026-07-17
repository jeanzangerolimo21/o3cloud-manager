CREATE TABLE IF NOT EXISTS crm_oportunidades (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    lead_id BIGINT NULL,
    contato_id BIGINT NULL,
    cliente_id BIGINT NULL,
    parceiro_id BIGINT NULL,
    executivo_responsavel_id BIGINT NULL,
    titulo VARCHAR(180) NOT NULL,
    empresa VARCHAR(150) NULL,
    erp VARCHAR(120) NULL,
    quantidade_usuarios INT NULL,
    valor_estimado DECIMAL(12,2) NULL,
    probabilidade INT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'NOVA',
    observacoes TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_crm_oportunidades_lead
        FOREIGN KEY (lead_id)
        REFERENCES crm_leads (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_crm_oportunidades_contato
        FOREIGN KEY (contato_id)
        REFERENCES crm_contatos (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_crm_oportunidades_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_crm_oportunidades_parceiro
        FOREIGN KEY (parceiro_id)
        REFERENCES parceiros (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_crm_oportunidades_executivo
        FOREIGN KEY (executivo_responsavel_id)
        REFERENCES parceiros_executivos (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    KEY idx_crm_oportunidades_titulo (titulo),
    KEY idx_crm_oportunidades_status (status),
    KEY idx_crm_oportunidades_ativo (ativo),
    KEY idx_crm_oportunidades_lead_id (lead_id),
    KEY idx_crm_oportunidades_contato_id (contato_id),
    KEY idx_crm_oportunidades_cliente_id (cliente_id),
    KEY idx_crm_oportunidades_parceiro_id (parceiro_id),
    KEY idx_crm_oportunidades_executivo_id (executivo_responsavel_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
