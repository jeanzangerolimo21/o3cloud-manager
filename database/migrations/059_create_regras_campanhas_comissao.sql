CREATE TABLE IF NOT EXISTS regras_campanhas_comissao (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
    percentual_parceiro DECIMAL(7,4) NOT NULL DEFAULT 0,
    percentual_executivo DECIMAL(7,4) NOT NULL DEFAULT 0,
    percentual_comissao DECIMAL(7,4) NULL,
    vigencia_inicio DATE NOT NULL,
    vigencia_fim DATE NOT NULL,
    descricao TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_by VARCHAR(180) NULL,
    updated_by VARCHAR(180) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_regras_campanhas_vigencia (vigencia_inicio, vigencia_fim),
    KEY idx_regras_campanhas_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE regras_campanhas_comissao
    ADD COLUMN IF NOT EXISTS percentual_parceiro DECIMAL(7,4) NOT NULL DEFAULT 0 AFTER nome,
    ADD COLUMN IF NOT EXISTS percentual_executivo DECIMAL(7,4) NOT NULL DEFAULT 0 AFTER percentual_parceiro;

UPDATE regras_campanhas_comissao
SET percentual_parceiro = percentual_comissao,
    percentual_executivo = percentual_comissao
WHERE percentual_comissao IS NOT NULL
  AND percentual_parceiro = 0
  AND percentual_executivo = 0;
