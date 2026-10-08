CREATE TABLE IF NOT EXISTS financeiro_cancelamentos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    cliente_id BIGINT NOT NULL,
    status ENUM('SOLICITADO') NOT NULL DEFAULT 'SOLICITADO',
    motivo VARCHAR(255) NOT NULL,
    data_desligamento DATETIME NOT NULL,
    detalhes_monitoramento TEXT NULL,
    detalhes_backup TEXT NULL,
    detalhes_ambiente TEXT NULL,
    observacoes TEXT NULL,
    solicitado_por BIGINT NULL,
    solicitado_por_email VARCHAR(180) NULL,
    destinatario_email VARCHAR(180) NOT NULL DEFAULT 'sac@o3cloud.com.br',
    email_enviado TINYINT(1) NOT NULL DEFAULT 0,
    email_enviado_em DATETIME NULL,
    email_tentativas INT NOT NULL DEFAULT 0,
    erro_email TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_cancelamentos_cliente (cliente_id),
    KEY idx_cancelamentos_data_desligamento (data_desligamento),
    KEY idx_cancelamentos_ativo_status (ativo, status),
    CONSTRAINT fk_financeiro_cancelamentos_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS financeiro_cancelamento_contratos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cancelamento_id BIGINT NOT NULL,
    contrato_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_cancelamento_contrato (cancelamento_id, contrato_id),
    KEY idx_cancelamento_contratos_contrato (contrato_id),
    CONSTRAINT fk_cancelamento_contratos_cancelamento
        FOREIGN KEY (cancelamento_id) REFERENCES financeiro_cancelamentos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cancelamento_contratos_contrato
        FOREIGN KEY (contrato_id) REFERENCES contratos(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT p.id, 'cancelamentos', 1, 'EDICAO'
FROM auth_perfis p
WHERE p.codigo IN ('DIRETORIA', 'FINANCEIRO')
ON DUPLICATE KEY UPDATE permitido=1, nivel_acesso='EDICAO';
