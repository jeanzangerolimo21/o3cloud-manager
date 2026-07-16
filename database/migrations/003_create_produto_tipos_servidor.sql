CREATE TABLE IF NOT EXISTS produto_tipos_servidor (
    id BIGINT NOT NULL AUTO_INCREMENT,
    uuid CHAR(36) NULL,
    codigo VARCHAR(30) NULL,
    nome VARCHAR(100) NULL,
    descricao TEXT NULL,
    ordem INT NULL DEFAULT 0,
    ativo TINYINT(1) NULL DEFAULT 1,
    PRIMARY KEY (id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
