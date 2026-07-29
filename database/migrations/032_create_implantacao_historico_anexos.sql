CREATE TABLE IF NOT EXISTS implantacao_historico_anexos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    historico_id BIGINT NOT NULL,
    implantacao_id BIGINT NOT NULL,
    arquivo_original VARCHAR(255) NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    caminho VARCHAR(500) NOT NULL,
    url VARCHAR(500) NOT NULL,
    mime_type VARCHAR(150) NULL,
    tamanho BIGINT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_implantacao_historico_anexo_historico
        FOREIGN KEY (historico_id)
        REFERENCES implantacao_historico (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_implantacao_historico_anexo_implantacao
        FOREIGN KEY (implantacao_id)
        REFERENCES implantacoes (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    KEY idx_implantacao_historico_anexos_historico_id (historico_id),
    KEY idx_implantacao_historico_anexos_implantacao_id (implantacao_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
