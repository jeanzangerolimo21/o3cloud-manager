CREATE TABLE IF NOT EXISTS financeiro_premiacoes_pagamento (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    contrato_id BIGINT NOT NULL,
    campanha_id BIGINT NOT NULL,
    status_manual ENUM('ABERTO', 'LANCADO', 'PAGO') NOT NULL DEFAULT 'ABERTO',
    observacoes TEXT NULL,
    created_by VARCHAR(180) NULL,
    updated_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_financeiro_premiacoes_pagamento (contrato_id, campanha_id),
    KEY idx_financeiro_premiacoes_pagamento_status (status_manual),
    CONSTRAINT fk_financeiro_premiacoes_pagamento_contrato
        FOREIGN KEY (contrato_id)
        REFERENCES contratos (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_financeiro_premiacoes_pagamento_campanha
        FOREIGN KEY (campanha_id)
        REFERENCES regras_campanhas_comissao (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
