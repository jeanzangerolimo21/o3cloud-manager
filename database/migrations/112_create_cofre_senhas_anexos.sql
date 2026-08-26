CREATE TABLE IF NOT EXISTS implantacao_cofre_senhas_anexos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    cofre_senha_id BIGINT NOT NULL,
    arquivo_original VARCHAR(255) NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    caminho VARCHAR(500) NOT NULL,
    url VARCHAR(500) NULL,
    mime_type VARCHAR(150) NULL,
    tamanho BIGINT NULL,
    created_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_implantacao_cofre_anexos_senha_id (cofre_senha_id),
    CONSTRAINT fk_implantacao_cofre_anexos_senha
        FOREIGN KEY (cofre_senha_id)
        REFERENCES implantacao_cofre_senhas (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
