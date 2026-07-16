CREATE TABLE IF NOT EXISTS catalogo_recursos_servidor (
    id BIGINT NOT NULL AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL,
    codigo VARCHAR(30) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT NULL,
    tipo_recurso VARCHAR(20) NOT NULL DEFAULT 'SERVICO',
    valor_mensal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    valor_instalacao DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    ordem INT NOT NULL DEFAULT 0,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT NULL,
    updated_by BIGINT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_catalogo_recurso_codigo (codigo),
    KEY idx_catalogo_recurso_categoria (categoria),
    CONSTRAINT ck_catalogo_recurso_ordem
        CHECK (ordem >= 0)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
