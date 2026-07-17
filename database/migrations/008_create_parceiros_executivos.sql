CREATE TABLE IF NOT EXISTS parceiros_executivos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    parceiro_id BIGINT NULL,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NULL,
    telefone VARCHAR(30) NULL,
    chave_pix VARCHAR(120) NULL,
    informacoes_pagamento TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_parceiros_executivos_parceiro
        FOREIGN KEY (parceiro_id)
        REFERENCES parceiros (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    KEY idx_parceiros_executivos_nome (nome),
    KEY idx_parceiros_executivos_parceiro_id (parceiro_id),
    KEY idx_parceiros_executivos_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
