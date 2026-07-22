ALTER TABLE implantacoes
    ADD COLUMN emails_adicionais TEXT NULL AFTER implantador_email;

CREATE TABLE IF NOT EXISTS implantacao_historico (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    implantacao_id BIGINT NOT NULL,
    tipo VARCHAR(40) NOT NULL DEFAULT 'COMENTARIO',
    etapa_anterior VARCHAR(60) NULL,
    etapa_nova VARCHAR(60) NULL,
    autor VARCHAR(150) NULL,
    comentario TEXT NOT NULL,
    email_enviado TINYINT(1) NOT NULL DEFAULT 0,
    email_resultado TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_implantacao_historico_implantacao
        FOREIGN KEY (implantacao_id)
        REFERENCES implantacoes (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    KEY idx_implantacao_historico_implantacao_id (implantacao_id),
    KEY idx_implantacao_historico_created_at (created_at),
    KEY idx_implantacao_historico_tipo (tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
