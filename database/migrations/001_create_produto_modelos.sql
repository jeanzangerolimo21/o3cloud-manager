CREATE TABLE IF NOT EXISTS produto_modelos (
    id BIGINT NOT NULL AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL,
    produto_id BIGINT NOT NULL,
    codigo VARCHAR(30) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT NULL,
    ordem INT NOT NULL DEFAULT 0,
    padrao TINYINT(1) NOT NULL DEFAULT 0,
    versao VARCHAR(20) NULL,
    ativo TINYINT(1) NULL DEFAULT 1,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT NULL,
    updated_by BIGINT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_produto_modelo (produto_id, codigo),
    CONSTRAINT fk_modelo_produto
        FOREIGN KEY (produto_id)
        REFERENCES produtos (id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
