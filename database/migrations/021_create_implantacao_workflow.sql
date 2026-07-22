CREATE TABLE IF NOT EXISTS implantacoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    contrato_id BIGINT NOT NULL,
    cliente_id BIGINT NOT NULL,
    proposta_id BIGINT NULL,
    executivo_id BIGINT NULL,
    parceiro_id BIGINT NULL,
    ambiente_id BIGINT NULL,
    titulo VARCHAR(180) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'AGUARDANDO_INICIO',
    prioridade VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
    responsavel VARCHAR(150) NULL,
    data_prevista_inicio DATE NULL,
    data_prevista_entrega DATE NULL,
    data_inicio DATE NULL,
    data_entrega DATE NULL,
    percentual_conclusao DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    observacoes TEXT NULL,
    provisionamento_status VARCHAR(40) NOT NULL DEFAULT 'NAO_PLANEJADO',
    provisionamento_notas TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_implantacoes_contrato
        FOREIGN KEY (contrato_id)
        REFERENCES contratos (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_implantacoes_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    KEY idx_implantacoes_contrato_id (contrato_id),
    KEY idx_implantacoes_cliente_id (cliente_id),
    KEY idx_implantacoes_status (status),
    KEY idx_implantacoes_responsavel (responsavel),
    KEY idx_implantacoes_prazo (data_prevista_entrega),
    UNIQUE KEY uk_implantacoes_contrato_ativo (contrato_id, ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS implantacao_checklist (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    implantacao_id BIGINT NOT NULL,
    ordem INT NOT NULL DEFAULT 1,
    grupo VARCHAR(80) NOT NULL,
    titulo VARCHAR(180) NOT NULL,
    descricao TEXT NULL,
    obrigatorio TINYINT(1) NOT NULL DEFAULT 1,
    status VARCHAR(40) NOT NULL DEFAULT 'PENDENTE',
    responsavel VARCHAR(150) NULL,
    evidencia TEXT NULL,
    concluido_em DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_implantacao_checklist_implantacao
        FOREIGN KEY (implantacao_id)
        REFERENCES implantacoes (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    KEY idx_implantacao_checklist_implantacao_id (implantacao_id),
    KEY idx_implantacao_checklist_status (status),
    KEY idx_implantacao_checklist_ordem (ordem)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
