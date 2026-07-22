CREATE TABLE IF NOT EXISTS implantacao_cofre_pastas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    nome VARCHAR(160) NOT NULL,
    tipo VARCHAR(30) NOT NULL DEFAULT 'usuario',
    parceiro_id BIGINT NULL,
    parceiro_nome VARCHAR(180) NULL,
    cliente_id BIGINT NULL,
    cliente_nome VARCHAR(180) NULL,
    owner_email VARCHAR(180) NOT NULL DEFAULT 'sistema',
    compartilhada TINYINT(1) NOT NULL DEFAULT 0,
    compartilhada_com TEXT NULL,
    observacoes TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_implantacao_cofre_pastas_tipo (tipo),
    KEY idx_implantacao_cofre_pastas_parceiro_id (parceiro_id),
    KEY idx_implantacao_cofre_pastas_cliente_id (cliente_id),
    KEY idx_implantacao_cofre_pastas_owner_email (owner_email),
    KEY idx_implantacao_cofre_pastas_ativo (ativo),
    CONSTRAINT fk_implantacao_cofre_pastas_parceiro
        FOREIGN KEY (parceiro_id)
        REFERENCES parceiros (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_implantacao_cofre_pastas_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE implantacao_cofre_senhas
    ADD COLUMN pasta_id BIGINT NULL AFTER uuid,
    ADD INDEX idx_implantacao_cofre_pasta_id (pasta_id),
    ADD CONSTRAINT fk_implantacao_cofre_senha_pasta
        FOREIGN KEY (pasta_id)
        REFERENCES implantacao_cofre_pastas (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
