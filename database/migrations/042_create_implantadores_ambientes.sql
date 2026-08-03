CREATE TABLE IF NOT EXISTS implantadores (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NULL,
    telefone VARCHAR(40) NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    observacoes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_implantadores_email (email),
    KEY idx_implantadores_ativo_nome (ativo, nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE ambientes
    ADD COLUMN IF NOT EXISTS implantador_id BIGINT NULL AFTER responsavel_implantacao,
    ADD CONSTRAINT fk_ambientes_implantador
        FOREIGN KEY IF NOT EXISTS (implantador_id)
        REFERENCES implantadores(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
