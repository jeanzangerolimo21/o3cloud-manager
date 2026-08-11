CREATE TABLE IF NOT EXISTS config_atualizacoes_verificacoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL,
    branch_atual VARCHAR(120) NULL,
    commit_atual CHAR(40) NULL,
    tag_atual VARCHAR(120) NULL,
    remoto VARCHAR(500) NULL,
    releases_encontradas INT NOT NULL DEFAULT 0,
    release_recomendada VARCHAR(120) NULL,
    payload_json JSON NULL,
    mensagem VARCHAR(500) NULL,
    executado_por VARCHAR(180) NULL,
    iniciado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finalizado_em DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_config_atualizacoes_status (status, created_at),
    KEY idx_config_atualizacoes_release (release_recomendada)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
