CREATE TABLE IF NOT EXISTS administrativo_departamentos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL UNIQUE,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_adm_departamentos_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS administrativo_demandas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    titulo VARCHAR(180) NOT NULL,
    descricao TEXT NULL,
    categoria VARCHAR(40) NOT NULL DEFAULT 'OUTROS',
    prioridade VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
    responsavel_id BIGINT NULL,
    departamento_id BIGINT NULL,
    data_inicial DATE NULL,
    data_limite DATE NULL,
    hora TIME NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    observacoes TEXT NULL,
    permitir_comentarios TINYINT(1) NOT NULL DEFAULT 1,
    possui_anexos TINYINT(1) NOT NULL DEFAULT 0,
    criado_por VARCHAR(180) NULL,
    updated_by VARCHAR(180) NULL,
    concluida_em DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_adm_demandas_status (status),
    KEY idx_adm_demandas_responsavel (responsavel_id, status),
    KEY idx_adm_demandas_data_limite (data_limite, status),
    KEY idx_adm_demandas_departamento (departamento_id),
    CONSTRAINT fk_adm_demanda_responsavel FOREIGN KEY (responsavel_id) REFERENCES auth_usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_adm_demanda_departamento FOREIGN KEY (departamento_id) REFERENCES administrativo_departamentos(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS administrativo_historico (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    demanda_id BIGINT NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    comentario TEXT NULL,
    status_anterior VARCHAR(20) NULL,
    status_novo VARCHAR(20) NULL,
    responsavel_anterior_id BIGINT NULL,
    responsavel_novo_id BIGINT NULL,
    autor_email VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_adm_historico_demanda (demanda_id, created_at),
    CONSTRAINT fk_adm_historico_demanda FOREIGN KEY (demanda_id) REFERENCES administrativo_demandas(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS administrativo_comentarios (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    demanda_id BIGINT NOT NULL,
    comentario TEXT NOT NULL,
    autor_email VARCHAR(180) NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_adm_comentarios_demanda (demanda_id, created_at),
    CONSTRAINT fk_adm_comentario_demanda FOREIGN KEY (demanda_id) REFERENCES administrativo_demandas(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS administrativo_anexos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    demanda_id BIGINT NOT NULL,
    comentario_id BIGINT NULL,
    arquivo_original VARCHAR(255) NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    caminho VARCHAR(500) NOT NULL,
    url VARCHAR(500) NULL,
    mime_type VARCHAR(120) NULL,
    tamanho BIGINT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_adm_anexos_demanda (demanda_id),
    CONSTRAINT fk_adm_anexo_demanda FOREIGN KEY (demanda_id) REFERENCES administrativo_demandas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_adm_anexo_comentario FOREIGN KEY (comentario_id) REFERENCES administrativo_comentarios(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS administrativo_agendas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    usuario_id BIGINT NOT NULL UNIQUE,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_adm_agenda_usuario FOREIGN KEY (usuario_id) REFERENCES auth_usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS administrativo_notificacoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    usuario_id BIGINT NOT NULL,
    demanda_id BIGINT NULL,
    tipo VARCHAR(40) NOT NULL,
    titulo VARCHAR(180) NOT NULL,
    mensagem TEXT NOT NULL,
    lida_em DATETIME NULL,
    email_enviado TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_adm_notificacoes_usuario (usuario_id, lida_em, created_at),
    CONSTRAINT fk_adm_notificacao_usuario FOREIGN KEY (usuario_id) REFERENCES auth_usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_adm_notificacao_demanda FOREIGN KEY (demanda_id) REFERENCES administrativo_demandas(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE auth_usuarios ADD COLUMN IF NOT EXISTS possui_agenda TINYINT(1) NOT NULL DEFAULT 0 AFTER status;

INSERT INTO administrativo_departamentos (uuid, nome, created_by)
SELECT UUID(), nome, 'migration'
FROM (
    SELECT 'Administrativo' AS nome UNION ALL SELECT 'Financeiro' UNION ALL SELECT 'Comercial'
    UNION ALL SELECT 'Implantacao' UNION ALL SELECT 'Suporte' UNION ALL SELECT 'Infraestrutura'
    UNION ALL SELECT 'RH' UNION ALL SELECT 'Diretoria' UNION ALL SELECT 'Outros'
) AS departamentos
WHERE NOT EXISTS (SELECT 1 FROM administrativo_departamentos d WHERE d.nome = departamentos.nome);
