ALTER TABLE auth_perfis
    ADD COLUMN IF NOT EXISTS dashboard_principal VARCHAR(80) NULL AFTER mostrar_valores;

UPDATE auth_perfis
SET dashboard_principal = 'financeiro.dashboard'
WHERE dashboard_principal IS NULL OR dashboard_principal = '';

UPDATE auth_perfis SET dashboard_principal = 'financeiro.dashboard_executivo' WHERE codigo = 'DIRETORIA';
UPDATE auth_perfis SET dashboard_principal = 'propostas.dashboard' WHERE codigo = 'COMERCIAL';
UPDATE auth_perfis SET dashboard_principal = 'implantacao.index' WHERE codigo = 'OPERACOES';
UPDATE auth_perfis SET dashboard_principal = 'administrativo.index' WHERE codigo IN ('ADMINISTRATIVO_GESTOR', 'ADMINISTRATIVO_COLABORADOR');
