ALTER TABLE implantacao_cofre_senhas
    ADD COLUMN IF NOT EXISTS usuario_2 VARCHAR(160) NULL AFTER senha_encrypted,
    ADD COLUMN IF NOT EXISTS senha_2_encrypted TEXT NULL AFTER usuario_2;

ALTER TABLE implantacao_cofre_compartilhamentos
    ADD COLUMN IF NOT EXISTS credencial VARCHAR(20) NOT NULL DEFAULT 'principal' AFTER cofre_senha_id;

CREATE INDEX IF NOT EXISTS idx_cofre_compartilhamento_credencial
    ON implantacao_cofre_compartilhamentos (cofre_senha_id, credencial);
