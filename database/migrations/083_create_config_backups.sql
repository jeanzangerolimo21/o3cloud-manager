CREATE TABLE IF NOT EXISTS config_backups_agendamentos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 0,
    tipo_backup VARCHAR(30) NOT NULL DEFAULT 'COMPLETO',
    frequencia_horas INT NOT NULL DEFAULT 24,
    destino_tipo VARCHAR(30) NOT NULL DEFAULT 'LOCAL',
    destino_path VARCHAR(500) NULL,
    retencao_dias INT NOT NULL DEFAULT 7,
    proxima_execucao_em DATETIME NULL,
    ultima_execucao_em DATETIME NULL,
    ultimo_status VARCHAR(30) NULL,
    ultimo_mensagem VARCHAR(500) NULL,
    updated_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_config_backups_agendamentos_nome (nome),
    KEY idx_config_backups_agendamentos_due (ativo, proxima_execucao_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS config_backups_execucoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    agendamento_id BIGINT NULL,
    tipo_backup VARCHAR(30) NOT NULL,
    destino_tipo VARCHAR(30) NOT NULL,
    destino_path VARCHAR(500) NULL,
    status VARCHAR(30) NOT NULL,
    arquivo_nome VARCHAR(255) NULL,
    arquivo_path VARCHAR(700) NULL,
    tamanho_bytes BIGINT NULL,
    checksum_sha256 CHAR(64) NULL,
    iniciado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finalizado_em DATETIME NULL,
    mensagem VARCHAR(500) NULL,
    executado_por VARCHAR(180) NULL,
    manual TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_config_backups_execucoes_agendamento (agendamento_id, created_at),
    KEY idx_config_backups_execucoes_status (status, created_at),
    CONSTRAINT fk_config_backups_execucoes_agendamento
        FOREIGN KEY (agendamento_id) REFERENCES config_backups_agendamentos(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO config_backups_agendamentos (uuid, nome, ativo, tipo_backup, frequencia_horas, destino_tipo, destino_path, retencao_dias)
VALUES (UUID(), 'Backup principal', 0, 'COMPLETO', 24, 'LOCAL', NULL, 7)
ON DUPLICATE KEY UPDATE nome=VALUES(nome);

INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT p.id, 'backups_sistema', 1, 'EDICAO'
FROM auth_perfis p
WHERE p.codigo = 'ADMIN'
ON DUPLICATE KEY UPDATE permitido=1, nivel_acesso='EDICAO';
