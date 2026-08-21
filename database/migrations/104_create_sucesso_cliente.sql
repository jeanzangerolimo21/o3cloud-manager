CREATE TABLE IF NOT EXISTS crm_sucesso_cliente (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    contrato_id BIGINT NOT NULL,
    contato_id BIGINT NULL,
    status_relacionamento ENUM('OTIMO','BOM','REGULAR','CRITICO') NOT NULL DEFAULT 'BOM',
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    updated_by VARCHAR(120) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_cs_contrato (contrato_id),
    KEY idx_cs_status (status_relacionamento),
    KEY idx_cs_contato (contato_id),
    CONSTRAINT fk_cs_contrato FOREIGN KEY (contrato_id) REFERENCES contratos(id),
    CONSTRAINT fk_cs_contato FOREIGN KEY (contato_id) REFERENCES crm_contatos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS crm_sucesso_cliente_historico (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    contrato_id BIGINT NOT NULL,
    contato_id BIGINT NULL,
    status_relacionamento ENUM('OTIMO','BOM','REGULAR','CRITICO') NOT NULL,
    comentario TEXT NOT NULL,
    autor_email VARCHAR(120) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_cs_hist_contrato (contrato_id, created_at),
    KEY idx_cs_hist_status (status_relacionamento),
    CONSTRAINT fk_cs_hist_contrato FOREIGN KEY (contrato_id) REFERENCES contratos(id),
    CONSTRAINT fk_cs_hist_contato FOREIGN KEY (contato_id) REFERENCES crm_contatos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS crm_sucesso_cliente_historico_anexos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    historico_id BIGINT NOT NULL,
    contrato_id BIGINT NOT NULL,
    arquivo_original VARCHAR(255) NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    caminho VARCHAR(500) NOT NULL,
    url VARCHAR(500) NOT NULL,
    mime_type VARCHAR(120) NULL,
    tamanho BIGINT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_cs_anexo_historico (historico_id),
    KEY idx_cs_anexo_contrato (contrato_id),
    CONSTRAINT fk_cs_anexo_historico FOREIGN KEY (historico_id) REFERENCES crm_sucesso_cliente_historico(id),
    CONSTRAINT fk_cs_anexo_contrato FOREIGN KEY (contrato_id) REFERENCES contratos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT perfil_id,
       'sucesso_cliente',
       1,
       CASE WHEN SUM(nivel_acesso = 'EDICAO') > 0 THEN 'EDICAO' ELSE MAX(nivel_acesso) END
FROM auth_perfil_permissoes
WHERE menu_key IN ('propostas', 'dashboard_comercial')
  AND permitido = 1
GROUP BY perfil_id
ON DUPLICATE KEY UPDATE
    permitido = VALUES(permitido),
    nivel_acesso = VALUES(nivel_acesso);
