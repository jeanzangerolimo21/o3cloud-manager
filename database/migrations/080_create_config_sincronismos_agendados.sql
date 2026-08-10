CREATE TABLE IF NOT EXISTS config_sincronismos_agendados (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    tipo VARCHAR(40) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 0,
    frequencia_minutos INT NOT NULL DEFAULT 1440,
    proxima_execucao_em DATETIME NULL,
    ultima_execucao_em DATETIME NULL,
    ultimo_status VARCHAR(30) NULL,
    ultimo_mensagem VARCHAR(500) NULL,
    updated_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_config_sincronismos_agendados_due (ativo, proxima_execucao_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS config_sincronismos_execucoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    agendamento_id BIGINT NOT NULL,
    tipo VARCHAR(40) NOT NULL,
    status VARCHAR(30) NOT NULL,
    iniciada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finalizada_em DATETIME NULL,
    mensagem VARCHAR(500) NULL,
    executado_por VARCHAR(180) NULL,
    manual TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_config_sincronismos_execucoes_agendamento (agendamento_id, created_at),
    KEY idx_config_sincronismos_execucoes_tipo (tipo, created_at),
    CONSTRAINT fk_config_sincronismos_execucoes_agendamento
        FOREIGN KEY (agendamento_id) REFERENCES config_sincronismos_agendados(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO config_sincronismos_agendados (uuid, tipo, nome, ativo, frequencia_minutos)
VALUES
    (UUID(), 'OMIE', 'Omie', 0, 1440),
    (UUID(), 'ZABBIX', 'Zabbix', 0, 60),
    (UUID(), 'PROXMOX', 'Proxmox', 0, 60),
    (UUID(), 'CLICKSIGN', 'ClickSign', 0, 60),
    (UUID(), 'PBS', 'PBS', 0, 360),
    (UUID(), 'TRUENAS', 'TrueNAS', 0, 360)
ON DUPLICATE KEY UPDATE nome=VALUES(nome);

INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT p.id, 'sincronismos_agendados', 1, 'EDICAO'
FROM auth_perfis p
WHERE p.codigo = 'ADMIN'
ON DUPLICATE KEY UPDATE permitido=1, nivel_acesso='EDICAO';
