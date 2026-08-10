CREATE TABLE IF NOT EXISTS relatorios_jobs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    modelo_id BIGINT NULL,
    fonte VARCHAR(80) NOT NULL,
    formato VARCHAR(20) NOT NULL DEFAULT 'XLSX',
    configuracao_json JSON NOT NULL,
    status ENUM('PENDENTE','PROCESSANDO','CONCLUIDO','ERRO') NOT NULL DEFAULT 'PENDENTE',
    total_linhas INT NULL,
    arquivo_nome VARCHAR(255) NULL,
    arquivo_url VARCHAR(500) NULL,
    erro TEXT NULL,
    solicitado_por_id BIGINT NULL,
    solicitado_por_email VARCHAR(180) NOT NULL,
    processado_em DATETIME NULL,
    email_enviado TINYINT(1) NOT NULL DEFAULT 0,
    email_erro TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_relatorios_jobs_status (status, created_at),
    KEY idx_relatorios_jobs_usuario (solicitado_por_id, created_at),
    KEY idx_relatorios_jobs_modelo (modelo_id),
    CONSTRAINT fk_relatorios_jobs_modelo
        FOREIGN KEY (modelo_id) REFERENCES relatorios_modelos(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_relatorios_jobs_usuario
        FOREIGN KEY (solicitado_por_id) REFERENCES auth_usuarios(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
