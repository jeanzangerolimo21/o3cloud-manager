CREATE TABLE IF NOT EXISTS produto_faixas (
    id BIGINT NOT NULL AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL,
    modelo_id BIGINT NOT NULL,
    codigo VARCHAR(30) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    usuarios_inicio INT NOT NULL,
    usuarios_fim INT NOT NULL,
    permite_upgrade_manual TINYINT(1) NOT NULL DEFAULT 1,
    descricao TEXT NULL,
    ordem INT NOT NULL DEFAULT 0,
    ativo TINYINT(1) NULL DEFAULT 1,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT NULL,
    updated_by BIGINT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_produto_faixa (modelo_id, usuarios_inicio, usuarios_fim),
    KEY idx_modelo (modelo_id),
    CONSTRAINT fk_produto_faixa_modelo
        FOREIGN KEY (modelo_id)
        REFERENCES produto_modelos (id),
    CONSTRAINT ck_faixa_inicio
        CHECK (usuarios_inicio >= 0),
    CONSTRAINT ck_faixa_fim
        CHECK (usuarios_fim >= usuarios_inicio),
    CONSTRAINT ck_faixa_ordem
        CHECK (ordem >= 0)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
