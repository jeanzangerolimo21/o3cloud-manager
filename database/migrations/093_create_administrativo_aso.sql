CREATE TABLE IF NOT EXISTS administrativo_aso_colaboradores (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    cliente_id BIGINT NULL,
    cliente_nome VARCHAR(180) NULL,
    nome_completo VARCHAR(180) NOT NULL,
    cpf VARCHAR(20) NOT NULL,
    data_nascimento DATE NOT NULL,
    data_admissao DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ATIVO',
    criado_por VARCHAR(180) NULL,
    updated_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_adm_aso_colab_cliente (cliente_id, status),
    KEY idx_adm_aso_colab_nome (nome_completo),
    KEY idx_adm_aso_colab_cpf (cpf),
    CONSTRAINT fk_adm_aso_colab_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS administrativo_aso_exames (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    colaborador_id BIGINT NOT NULL,
    arquivo_original VARCHAR(255) NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    caminho VARCHAR(500) NOT NULL,
    url VARCHAR(500) NULL,
    mime_type VARCHAR(120) NULL,
    tamanho BIGINT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_adm_aso_exames_colab (colaborador_id, created_at),
    CONSTRAINT fk_adm_aso_exames_colab FOREIGN KEY (colaborador_id) REFERENCES administrativo_aso_colaboradores(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS administrativo_aso_lembretes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    colaborador_id BIGINT NOT NULL,
    demanda_id BIGINT NOT NULL,
    usuario_id BIGINT NOT NULL,
    data_aso DATE NOT NULL,
    antecedencia_dias INT NOT NULL,
    tipo_participacao VARCHAR(20) NOT NULL DEFAULT 'DONO',
    enviar_email TINYINT(1) NOT NULL DEFAULT 1,
    aviso_enviado TINYINT(1) NOT NULL DEFAULT 0,
    aviso_enviado_em DATETIME NULL,
    erro_email TEXT NULL,
    created_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_adm_aso_lembrete_due (aviso_enviado, data_aso, antecedencia_dias),
    KEY idx_adm_aso_lembrete_colab (colaborador_id),
    KEY idx_adm_aso_lembrete_demanda (demanda_id),
    CONSTRAINT fk_adm_aso_lembrete_colab FOREIGN KEY (colaborador_id) REFERENCES administrativo_aso_colaboradores(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_adm_aso_lembrete_demanda FOREIGN KEY (demanda_id) REFERENCES administrativo_demandas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_adm_aso_lembrete_usuario FOREIGN KEY (usuario_id) REFERENCES auth_usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
