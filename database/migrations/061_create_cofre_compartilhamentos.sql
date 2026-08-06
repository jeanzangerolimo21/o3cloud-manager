CREATE TABLE IF NOT EXISTS implantacao_cofre_compartilhamentos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    cofre_senha_id BIGINT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    accessed_at DATETIME NULL,
    revoked_at DATETIME NULL,
    created_by VARCHAR(180) NULL,
    created_ip VARCHAR(45) NULL,
    accessed_ip VARCHAR(45) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_cofre_compartilhamento_expira (expires_at),
    KEY idx_cofre_compartilhamento_senha (cofre_senha_id),
    CONSTRAINT fk_cofre_compartilhamento_senha
        FOREIGN KEY (cofre_senha_id) REFERENCES implantacao_cofre_senhas (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
