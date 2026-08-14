ALTER TABLE auth_usuarios
    ADD COLUMN IF NOT EXISTS exigir_2fa TINYINT(1) NOT NULL DEFAULT 0 AFTER possui_agenda,
    ADD COLUMN IF NOT EXISTS two_factor_metodo VARCHAR(30) NOT NULL DEFAULT 'EMAIL' AFTER exigir_2fa,
    ADD COLUMN IF NOT EXISTS two_factor_secret TEXT NULL AFTER two_factor_metodo,
    ADD COLUMN IF NOT EXISTS two_factor_configurado_em DATETIME NULL AFTER two_factor_secret;

CREATE TABLE IF NOT EXISTS auth_2fa_codigos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    usuario_id BIGINT NOT NULL,
    codigo_hash CHAR(64) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDENTE',
    expira_em DATETIME NOT NULL,
    usado_em DATETIME NULL,
    tentativas INT NOT NULL DEFAULT 0,
    ip_origem VARCHAR(80) NULL,
    user_agent VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_auth_2fa_usuario_status (usuario_id, status, expira_em),
    CONSTRAINT fk_auth_2fa_codigos_usuario FOREIGN KEY (usuario_id) REFERENCES auth_usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_dispositivos_confiaveis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    usuario_id BIGINT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    descricao VARCHAR(180) NULL,
    ip_origem VARCHAR(80) NULL,
    user_agent VARCHAR(255) NULL,
    expira_em DATETIME NOT NULL,
    ultimo_uso_em DATETIME NULL,
    revogado_em DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_auth_disp_usuario (usuario_id, expira_em, revogado_em),
    CONSTRAINT fk_auth_dispositivos_usuario FOREIGN KEY (usuario_id) REFERENCES auth_usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
