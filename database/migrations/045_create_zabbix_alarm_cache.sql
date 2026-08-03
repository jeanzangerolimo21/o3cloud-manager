CREATE TABLE IF NOT EXISTS zabbix_alarm_cache (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    eventid VARCHAR(80) NOT NULL,
    clock BIGINT NULL,
    data_evento DATETIME NULL,
    aberto TINYINT(1) NOT NULL DEFAULT 0,
    status_label VARCHAR(40) NOT NULL,
    severidade INT NOT NULL DEFAULT 0,
    severidade_label VARCHAR(80) NOT NULL,
    host VARCHAR(255) NULL,
    nome VARCHAR(500) NOT NULL,
    acknowledged TINYINT(1) NOT NULL DEFAULT 0,
    raw_payload LONGTEXT NULL,
    sincronizado_em DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_zabbix_alarm_cache_integracao_evento (integracao_id, eventid),
    KEY idx_zabbix_alarm_cache_prioridade (aberto, severidade, clock),
    KEY idx_zabbix_alarm_cache_sync (sincronizado_em),
    CONSTRAINT fk_zabbix_alarm_cache_integracao
        FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
