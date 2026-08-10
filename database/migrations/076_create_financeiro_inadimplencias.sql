CREATE TABLE IF NOT EXISTS financeiro_inadimplencias (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    contrato_id BIGINT NOT NULL,
    status ENUM('PENDENTE','LIBERADO') NOT NULL DEFAULT 'PENDENTE',
    motivo VARCHAR(255) NULL,
    observacoes TEXT NULL,
    bloqueado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    bloqueado_por BIGINT NULL,
    bloqueado_por_email VARCHAR(180) NULL,
    tipo_liberacao ENUM('QUITACAO','ACORDO') NULL,
    observacao_liberacao TEXT NULL,
    liberado_em DATETIME NULL,
    liberado_por BIGINT NULL,
    liberado_por_email VARCHAR(180) NULL,
    email_suporte_enviado TINYINT(1) NOT NULL DEFAULT 0,
    email_cliente_enviado TINYINT(1) NOT NULL DEFAULT 0,
    email_liberacao_suporte_enviado TINYINT(1) NOT NULL DEFAULT 0,
    email_liberacao_cliente_enviado TINYINT(1) NOT NULL DEFAULT 0,
    erro_email_suporte TEXT NULL,
    erro_email_cliente TEXT NULL,
    erro_email_liberacao_suporte TEXT NULL,
    erro_email_liberacao_cliente TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_inadimplencia_contrato (contrato_id),
    KEY idx_inadimplencia_status (status),
    KEY idx_inadimplencia_ativo_status (ativo, status),
    KEY idx_inadimplencia_contrato_status_ativo (contrato_id, status, ativo),
    KEY idx_inadimplencia_bloqueado_em (bloqueado_em),
    CONSTRAINT fk_financeiro_inadimplencias_contrato
        FOREIGN KEY (contrato_id) REFERENCES contratos(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT p.id, 'inadimplentes', 1, 'EDICAO'
FROM auth_perfis p
WHERE p.codigo IN ('DIRETORIA', 'FINANCEIRO')
ON DUPLICATE KEY UPDATE permitido=1, nivel_acesso='EDICAO';
