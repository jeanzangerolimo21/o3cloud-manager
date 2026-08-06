CREATE TABLE IF NOT EXISTS crm_evento_disparos_email (
 id BIGINT AUTO_INCREMENT PRIMARY KEY, uuid CHAR(36) NOT NULL UNIQUE, evento_id BIGINT NOT NULL, config_email_id BIGINT NOT NULL,
 assunto VARCHAR(255) NOT NULL, total_destinatarios INT NOT NULL DEFAULT 0, total_enviados INT NOT NULL DEFAULT 0,
 status VARCHAR(30) NOT NULL DEFAULT 'PROCESSANDO', erro TEXT NULL, anexo_nome VARCHAR(255) NULL,
 created_by VARCHAR(120) NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, finished_at DATETIME NULL,
 KEY idx_evento_disparo_evento (evento_id), KEY idx_evento_disparo_config_data (config_email_id,created_at),
 CONSTRAINT fk_evento_disparo_evento FOREIGN KEY (evento_id) REFERENCES crm_eventos(id) ON DELETE CASCADE,
 CONSTRAINT fk_evento_disparo_config FOREIGN KEY (config_email_id) REFERENCES config_email_servicos(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;