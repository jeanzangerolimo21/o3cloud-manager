CREATE TABLE IF NOT EXISTS crm_proposta_comentarios_internos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    proposta_id BIGINT NOT NULL,
    comentario TEXT NOT NULL,
    autor_email VARCHAR(180) NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_proposta_comentarios_proposta (proposta_id, created_at),
    CONSTRAINT fk_proposta_comentarios_proposta
        FOREIGN KEY (proposta_id) REFERENCES crm_propostas(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS crm_proposta_comentario_compartilhamentos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    comentario_id BIGINT NOT NULL,
    usuario_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_proposta_comentario_usuario (comentario_id, usuario_id),
    KEY idx_proposta_comentario_comp_usuario (usuario_id),
    CONSTRAINT fk_proposta_comentario_comp_comentario
        FOREIGN KEY (comentario_id) REFERENCES crm_proposta_comentarios_internos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_proposta_comentario_comp_usuario
        FOREIGN KEY (usuario_id) REFERENCES auth_usuarios(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
