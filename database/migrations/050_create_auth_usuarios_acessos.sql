CREATE TABLE IF NOT EXISTS auth_perfis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    nome VARCHAR(80) NOT NULL,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    descricao TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_auth_perfis_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_usuarios (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(180) NOT NULL UNIQUE,
    login VARCHAR(120) NOT NULL UNIQUE,
    origem VARCHAR(30) NOT NULL DEFAULT 'LOCAL',
    perfil_id BIGINT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'CONVIDADO',
    senha_hash VARCHAR(255) NULL,
    externo_id VARCHAR(180) NULL,
    ultimo_login_em DATETIME NULL,
    ultima_sincronizacao_em DATETIME NULL,
    created_by VARCHAR(120) NULL,
    updated_by VARCHAR(120) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_auth_usuarios_status (status),
    KEY idx_auth_usuarios_origem (origem),
    CONSTRAINT fk_auth_usuarios_perfil FOREIGN KEY (perfil_id) REFERENCES auth_perfis(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_convites (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    usuario_id BIGINT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    email VARCHAR(180) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDENTE',
    expira_em DATETIME NOT NULL,
    usado_em DATETIME NULL,
    enviado_em DATETIME NULL,
    created_by VARCHAR(120) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_auth_convites_usuario (usuario_id),
    KEY idx_auth_convites_status (status),
    CONSTRAINT fk_auth_convites_usuario FOREIGN KEY (usuario_id) REFERENCES auth_usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_provedores (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    host VARCHAR(255) NULL,
    porta INT NULL,
    dominio VARCHAR(180) NULL,
    base_dn VARCHAR(255) NULL,
    bind_dn VARCHAR(255) NULL,
    bind_password_encrypted TEXT NULL,
    usar_tls TINYINT(1) NOT NULL DEFAULT 0,
    usar_starttls TINYINT(1) NOT NULL DEFAULT 0,
    filtro_usuarios VARCHAR(255) NULL,
    filtro_grupos VARCHAR(255) NULL,
    atributo_login VARCHAR(80) NULL,
    atributo_email VARCHAR(80) NULL,
    atributo_nome VARCHAR(80) NULL,
    upn_suffix VARCHAR(120) NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    ultimo_teste_status VARCHAR(20) NULL,
    ultimo_teste_mensagem TEXT NULL,
    ultimo_teste_em DATETIME NULL,
    created_by VARCHAR(120) NULL,
    updated_by VARCHAR(120) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_auth_provedores_tipo (tipo),
    KEY idx_auth_provedores_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_auditoria (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    usuario_email VARCHAR(180) NULL,
    acao VARCHAR(120) NOT NULL,
    entidade VARCHAR(80) NOT NULL,
    entidade_id BIGINT NULL,
    detalhes TEXT NULL,
    ip_origem VARCHAR(80) NULL,
    user_agent VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_auth_auditoria_entidade (entidade, entidade_id),
    KEY idx_auth_auditoria_usuario (usuario_email),
    KEY idx_auth_auditoria_entidade_created (entidade, created_at),
    KEY idx_auth_auditoria_acao (acao),
    KEY idx_auth_auditoria_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO auth_perfis (uuid, nome, codigo, descricao)
SELECT UUID(), 'Administrador', 'ADMIN', 'Acesso completo ao sistema'
WHERE NOT EXISTS (SELECT 1 FROM auth_perfis WHERE codigo = 'ADMIN');

INSERT INTO auth_perfis (uuid, nome, codigo, descricao)
SELECT UUID(), 'Diretoria', 'DIRETORIA', 'Acesso executivo e leitura gerencial'
WHERE NOT EXISTS (SELECT 1 FROM auth_perfis WHERE codigo = 'DIRETORIA');

INSERT INTO auth_perfis (uuid, nome, codigo, descricao)
SELECT UUID(), 'Financeiro', 'FINANCEIRO', 'Operacao financeira e contratos'
WHERE NOT EXISTS (SELECT 1 FROM auth_perfis WHERE codigo = 'FINANCEIRO');

INSERT INTO auth_perfis (uuid, nome, codigo, descricao)
SELECT UUID(), 'Comercial', 'COMERCIAL', 'Operacao comercial e propostas'
WHERE NOT EXISTS (SELECT 1 FROM auth_perfis WHERE codigo = 'COMERCIAL');

INSERT INTO auth_perfis (uuid, nome, codigo, descricao)
SELECT UUID(), 'Operacoes', 'OPERACOES', 'Operacao tecnica e implantacao'
WHERE NOT EXISTS (SELECT 1 FROM auth_perfis WHERE codigo = 'OPERACOES');

INSERT INTO auth_perfis (uuid, nome, codigo, descricao)
SELECT UUID(), 'Suporte', 'SUPORTE', 'Atendimento e suporte operacional'
WHERE NOT EXISTS (SELECT 1 FROM auth_perfis WHERE codigo = 'SUPORTE');
