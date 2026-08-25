CREATE TABLE IF NOT EXISTS auth_password_resets (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    usuario_id BIGINT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDENTE',
    expira_em DATETIME NOT NULL,
    usado_em DATETIME NULL,
    ip_origem VARCHAR(80) NULL,
    user_agent VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_auth_password_resets_usuario_status (usuario_id, status, expira_em),
    CONSTRAINT fk_auth_password_resets_usuario
        FOREIGN KEY (usuario_id) REFERENCES auth_usuarios(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
