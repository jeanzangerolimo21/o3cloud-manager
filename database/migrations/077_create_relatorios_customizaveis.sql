CREATE TABLE IF NOT EXISTS relatorios_modelos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    nome VARCHAR(160) NOT NULL,
    descricao TEXT NULL,
    fonte VARCHAR(80) NOT NULL,
    configuracao_json JSON NOT NULL,
    visibilidade ENUM('PRIVADO','PERFIL','GLOBAL') NOT NULL DEFAULT 'PRIVADO',
    perfis_json JSON NULL,
    criado_por_id BIGINT NULL,
    criado_por_email VARCHAR(180) NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_by VARCHAR(180) NULL,
    updated_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_relatorios_modelos_fonte (fonte),
    KEY idx_relatorios_modelos_visibilidade (visibilidade, ativo),
    KEY idx_relatorios_modelos_criador (criado_por_id, ativo),
    CONSTRAINT fk_relatorios_modelos_usuario
        FOREIGN KEY (criado_por_id) REFERENCES auth_usuarios(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS relatorios_execucoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    modelo_id BIGINT NULL,
    fonte VARCHAR(80) NOT NULL,
    formato VARCHAR(20) NOT NULL DEFAULT 'HTML',
    total_linhas INT NOT NULL DEFAULT 0,
    usuario_id BIGINT NULL,
    usuario_email VARCHAR(180) NULL,
    filtros_json JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_relatorios_execucoes_modelo (modelo_id),
    KEY idx_relatorios_execucoes_usuario (usuario_id, created_at),
    KEY idx_relatorios_execucoes_fonte (fonte, created_at),
    CONSTRAINT fk_relatorios_execucoes_modelo
        FOREIGN KEY (modelo_id) REFERENCES relatorios_modelos(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_relatorios_execucoes_usuario
        FOREIGN KEY (usuario_id) REFERENCES auth_usuarios(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT p.id, 'relatorios', 1, 'EDICAO'
FROM auth_perfis p
WHERE p.codigo IN ('ADMIN', 'DIRETORIA', 'ADMINISTRATIVO_GESTOR')
ON DUPLICATE KEY UPDATE permitido=1, nivel_acesso='EDICAO';
