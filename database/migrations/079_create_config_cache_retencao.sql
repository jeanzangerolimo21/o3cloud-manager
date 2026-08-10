CREATE TABLE IF NOT EXISTS config_cache_retencao (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    cache_key VARCHAR(80) NOT NULL UNIQUE,
    retencao_dias INT NOT NULL DEFAULT 90,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    updated_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS config_cache_limpezas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    cache_key VARCHAR(80) NOT NULL,
    modo VARCHAR(30) NOT NULL,
    retencao_dias INT NULL,
    registros_removidos INT NOT NULL DEFAULT 0,
    executado_por VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_config_cache_limpezas_cache (cache_key, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT p.id, 'cache_sistema', 1, 'EDICAO'
FROM auth_perfis p
WHERE p.codigo = 'ADMIN'
ON DUPLICATE KEY UPDATE permitido=1, nivel_acesso='EDICAO';
