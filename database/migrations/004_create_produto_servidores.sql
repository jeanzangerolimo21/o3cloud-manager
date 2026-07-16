CREATE TABLE IF NOT EXISTS produto_servidores (
    id BIGINT NOT NULL AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL,
    faixa_id BIGINT NOT NULL,
    codigo VARCHAR(30) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tipo ENUM('BANCO','APLICACAO','SM','STORE','ACESSO','TERMINAL','WEB','OUTRO') NOT NULL,
    sistema_operacional VARCHAR(100) NULL,
    observacoes TEXT NULL,
    ordem INT NULL DEFAULT 0,
    ativo TINYINT(1) NULL DEFAULT 1,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT NULL,
    updated_by BIGINT NULL,
    PRIMARY KEY (id),
    KEY idx_faixa (faixa_id),
    CONSTRAINT fk_produto_servidor_faixa
        FOREIGN KEY (faixa_id)
        REFERENCES produto_faixas (id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
