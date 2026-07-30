CREATE TABLE IF NOT EXISTS implantacao_cofre_senhas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    cliente_id BIGINT NOT NULL,
    cliente_nome VARCHAR(180) NOT NULL,
    cliente_cnpj VARCHAR(32) NULL,
    faixa_rede_id BIGINT NOT NULL,
    licenca_o3web_id BIGINT NULL,
    categoria VARCHAR(40) NOT NULL,
    titulo VARCHAR(160) NOT NULL,
    host VARCHAR(180) NULL,
    porta INT NULL,
    url VARCHAR(255) NULL,
    usuario VARCHAR(160) NOT NULL,
    senha_encrypted TEXT NOT NULL,
    observacoes TEXT NULL,
    proxmox_node_id VARCHAR(120) NULL,
    proxmox_vm_id VARCHAR(120) NULL,
    pbs_server_id VARCHAR(120) NULL,
    zabbix_host_id VARCHAR(120) NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_by VARCHAR(180) NULL,
    updated_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_implantacao_cofre_cliente_id (cliente_id),
    KEY idx_implantacao_cofre_faixa_rede_id (faixa_rede_id),
    KEY idx_implantacao_cofre_licenca_o3web_id (licenca_o3web_id),
    KEY idx_implantacao_cofre_categoria (categoria),
    KEY idx_implantacao_cofre_ativo (ativo),
    CONSTRAINT fk_implantacao_cofre_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_implantacao_cofre_faixa_rede
        FOREIGN KEY (faixa_rede_id)
        REFERENCES implantacao_faixas_rede (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_implantacao_cofre_licenca_o3web
        FOREIGN KEY (licenca_o3web_id)
        REFERENCES o3web_licencas (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS implantacao_cofre_senhas_auditoria (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cofre_senha_id BIGINT NOT NULL,
    acao VARCHAR(40) NOT NULL,
    usuario_email VARCHAR(180) NOT NULL DEFAULT 'sistema',
    detalhe VARCHAR(255) NULL,
    ip_origem VARCHAR(45) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_implantacao_cofre_auditoria_senha_id (cofre_senha_id),
    KEY idx_implantacao_cofre_auditoria_acao (acao),
    CONSTRAINT fk_implantacao_cofre_auditoria_senha
        FOREIGN KEY (cofre_senha_id)
        REFERENCES implantacao_cofre_senhas (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
