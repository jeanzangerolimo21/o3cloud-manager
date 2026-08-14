CREATE TABLE IF NOT EXISTS contratos_valores_historico (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    contrato_id BIGINT NOT NULL,
    valor_mensal DECIMAL(15,2) NULL,
    valor_servicos_bruto DECIMAL(15,2) NULL,
    valor_descontos DECIMAL(15,2) NULL,
    valor_servicos_liquido DECIMAL(15,2) NULL,
    vigencia_referencia DATE NULL,
    detectado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    origem VARCHAR(30) NOT NULL DEFAULT 'SISTEMA',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_contratos_valores_contrato_detectado (contrato_id, detectado_em),
    CONSTRAINT fk_contratos_valores_contrato
        FOREIGN KEY (contrato_id) REFERENCES contratos(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contratos_reajustes_alertas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    contrato_id BIGINT NOT NULL,
    aniversario_referencia DATE NOT NULL,
    antecedencia_dias INT NOT NULL,
    status VARCHAR(40) NOT NULL,
    exibido_em DATETIME NULL,
    email_enviado_em DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_reajuste_alerta_contrato_aniversario (contrato_id, aniversario_referencia, antecedencia_dias),
    KEY idx_reajuste_alerta_status (status, created_at),
    CONSTRAINT fk_reajuste_alerta_contrato
        FOREIGN KEY (contrato_id) REFERENCES contratos(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reajustes_configuracoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    chave VARCHAR(80) NOT NULL UNIQUE,
    alerta_30_dias TINYINT(1) NOT NULL DEFAULT 1,
    alerta_15_dias TINYINT(1) NOT NULL DEFAULT 1,
    alerta_7_dias TINYINT(1) NOT NULL DEFAULT 1,
    enviar_email TINYINT(1) NOT NULL DEFAULT 0,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    updated_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reajustes_configuracoes_usuarios (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    configuracao_id BIGINT NOT NULL,
    usuario_id BIGINT NOT NULL,
    receber_notificacao TINYINT(1) NOT NULL DEFAULT 1,
    receber_email TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_reajuste_config_usuario (configuracao_id, usuario_id),
    CONSTRAINT fk_reajuste_config_usuario_config
        FOREIGN KEY (configuracao_id) REFERENCES reajustes_configuracoes(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_reajuste_config_usuario_usuario
        FOREIGN KEY (usuario_id) REFERENCES auth_usuarios(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO reajustes_configuracoes (uuid, chave, alerta_30_dias, alerta_15_dias, alerta_7_dias, enviar_email, ativo)
VALUES (UUID(), 'PADRAO', 1, 1, 1, 0, 1)
ON DUPLICATE KEY UPDATE chave=VALUES(chave);

INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT perfil_id, 'reajustes_contratuais', 1, nivel_acesso
FROM auth_perfil_permissoes
WHERE menu_key IN ('contratos', 'faturamento')
  AND permitido = 1
ON DUPLICATE KEY UPDATE permitido=1, nivel_acesso=VALUES(nivel_acesso);
