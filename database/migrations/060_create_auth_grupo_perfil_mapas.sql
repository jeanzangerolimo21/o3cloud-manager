CREATE TABLE IF NOT EXISTS auth_grupo_perfil_mapas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NULL,
    provedor_tipo VARCHAR(30) NOT NULL,
    grupo_externo VARCHAR(180) NOT NULL,
    perfil_id BIGINT NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_by VARCHAR(120) NULL,
    updated_by VARCHAR(120) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_auth_grupo_perfil_integracao (integracao_id),
    KEY idx_auth_grupo_perfil_tipo (provedor_tipo),
    KEY idx_auth_grupo_perfil_grupo (grupo_externo),
    KEY idx_auth_grupo_perfil_ativo (ativo),
    CONSTRAINT fk_auth_grupo_perfil_perfil
        FOREIGN KEY (perfil_id) REFERENCES auth_perfis(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_auth_grupo_perfil_integracao
        FOREIGN KEY (integracao_id) REFERENCES implantacao_integracoes_config(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE auth_grupo_perfil_mapas
    ADD COLUMN IF NOT EXISTS integracao_id BIGINT NULL AFTER uuid,
    ADD COLUMN IF NOT EXISTS provedor_tipo VARCHAR(30) NOT NULL AFTER integracao_id,
    ADD COLUMN IF NOT EXISTS grupo_externo VARCHAR(180) NOT NULL AFTER provedor_tipo,
    ADD COLUMN IF NOT EXISTS perfil_id BIGINT NOT NULL AFTER grupo_externo,
    ADD COLUMN IF NOT EXISTS ativo TINYINT(1) NOT NULL DEFAULT 1 AFTER perfil_id;
