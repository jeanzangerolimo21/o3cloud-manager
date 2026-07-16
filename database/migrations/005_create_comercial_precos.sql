CREATE TABLE IF NOT EXISTS comercial_precos (
    id BIGINT NOT NULL AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL,
    faixa_id BIGINT NOT NULL,
    valor_mensal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    valor_setup DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    tem_projeto TINYINT(1) NOT NULL DEFAULT 0,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT NULL,
    updated_by BIGINT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_comercial_preco_faixa (faixa_id),
    CONSTRAINT fk_comercial_preco_faixa
        FOREIGN KEY (faixa_id)
        REFERENCES produto_faixas (id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
