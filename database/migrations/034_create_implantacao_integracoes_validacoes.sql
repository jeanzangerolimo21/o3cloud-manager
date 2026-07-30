CREATE TABLE IF NOT EXISTS implantacao_integracoes_validacoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    status VARCHAR(40) NOT NULL,
    mensagem TEXT NULL,
    validado_por VARCHAR(150) NULL,
    validado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_integracoes_validacoes_config
        FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config(id)
        ON DELETE CASCADE,
    KEY idx_integracoes_validacoes_integracao (integracao_id, validado_em),
    KEY idx_integracoes_validacoes_status (status, validado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
