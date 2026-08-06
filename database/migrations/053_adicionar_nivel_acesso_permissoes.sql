ALTER TABLE auth_perfil_permissoes
    ADD COLUMN IF NOT EXISTS nivel_acesso VARCHAR(20) NOT NULL DEFAULT 'EDICAO' AFTER permitido;

UPDATE auth_perfil_permissoes
SET nivel_acesso = 'EDICAO'
WHERE nivel_acesso IS NULL OR nivel_acesso = '';
