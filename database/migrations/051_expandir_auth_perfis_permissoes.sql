ALTER TABLE auth_perfis
    ADD COLUMN IF NOT EXISTS mostrar_valores TINYINT(1) NOT NULL DEFAULT 0 AFTER ativo;

CREATE TABLE IF NOT EXISTS auth_perfil_permissoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    perfil_id BIGINT NOT NULL,
    menu_key VARCHAR(120) NOT NULL,
    permitido TINYINT(1) NOT NULL DEFAULT 1,
    nivel_acesso VARCHAR(20) NOT NULL DEFAULT 'EDICAO',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_auth_perfil_menu (perfil_id, menu_key),
    KEY idx_auth_perfil_permissoes_menu (menu_key),
    CONSTRAINT fk_auth_perfil_permissoes_perfil
        FOREIGN KEY (perfil_id) REFERENCES auth_perfis(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

UPDATE auth_perfis
SET mostrar_valores = 1
WHERE codigo IN ('ADMIN', 'DIRETORIA', 'FINANCEIRO');

UPDATE auth_perfis
SET mostrar_valores = 0
WHERE codigo IN ('COMERCIAL', 'OPERACOES', 'SUPORTE');

INSERT IGNORE INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT p.id, v.menu_key, 1, 'EDICAO'
FROM auth_perfis p
JOIN (
    SELECT 'DIRETORIA' AS codigo, 'visao_geral' AS menu_key UNION ALL
    SELECT 'DIRETORIA', 'dashboard_executivo' UNION ALL
    SELECT 'DIRETORIA', 'produtos_clientes' UNION ALL
    SELECT 'DIRETORIA', 'faturamento' UNION ALL
    SELECT 'DIRETORIA', 'contratos' UNION ALL
    SELECT 'DIRETORIA', 'dashboard_comercial' UNION ALL
    SELECT 'DIRETORIA', 'propostas' UNION ALL
    SELECT 'DIRETORIA', 'implantacao' UNION ALL
    SELECT 'FINANCEIRO', 'visao_geral' UNION ALL
    SELECT 'FINANCEIRO', 'dashboard_executivo' UNION ALL
    SELECT 'FINANCEIRO', 'produtos_clientes' UNION ALL
    SELECT 'FINANCEIRO', 'faturamento' UNION ALL
    SELECT 'FINANCEIRO', 'contratos' UNION ALL
    SELECT 'FINANCEIRO', 'clientes' UNION ALL
    SELECT 'COMERCIAL', 'visao_geral' UNION ALL
    SELECT 'COMERCIAL', 'clientes' UNION ALL
    SELECT 'COMERCIAL', 'leads' UNION ALL
    SELECT 'COMERCIAL', 'contatos' UNION ALL
    SELECT 'COMERCIAL', 'oportunidades' UNION ALL
    SELECT 'COMERCIAL', 'pipeline_comercial' UNION ALL
    SELECT 'COMERCIAL', 'propostas' UNION ALL
    SELECT 'COMERCIAL', 'dashboard_comercial' UNION ALL
    SELECT 'COMERCIAL', 'parceiros' UNION ALL
    SELECT 'COMERCIAL', 'catalogo_comercial' UNION ALL
    SELECT 'OPERACOES', 'visao_geral' UNION ALL
    SELECT 'OPERACOES', 'ambientes' UNION ALL
    SELECT 'OPERACOES', 'implantadores' UNION ALL
    SELECT 'OPERACOES', 'clientes' UNION ALL
    SELECT 'OPERACOES', 'implantacao' UNION ALL
    SELECT 'OPERACOES', 'kanban_implantacao' UNION ALL
    SELECT 'OPERACOES', 'licencas_o3web' UNION ALL
    SELECT 'OPERACOES', 'faixas_rede' UNION ALL
    SELECT 'OPERACOES', 'cofre_senhas' UNION ALL
    SELECT 'OPERACOES', 'clusters' UNION ALL
    SELECT 'OPERACOES', 'nodes' UNION ALL
    SELECT 'OPERACOES', 'maquinas_virtuais' UNION ALL
    SELECT 'OPERACOES', 'containers' UNION ALL
    SELECT 'OPERACOES', 'backups_pbs' UNION ALL
    SELECT 'OPERACOES', 'monitoramento_zabbix' UNION ALL
    SELECT 'OPERACOES', 'backup_nas' UNION ALL
    SELECT 'SUPORTE', 'visao_geral' UNION ALL
    SELECT 'SUPORTE', 'clientes' UNION ALL
    SELECT 'SUPORTE', 'implantacao' UNION ALL
    SELECT 'SUPORTE', 'kanban_implantacao' UNION ALL
    SELECT 'SUPORTE', 'cofre_senhas' UNION ALL
    SELECT 'SUPORTE', 'clusters' UNION ALL
    SELECT 'SUPORTE', 'nodes' UNION ALL
    SELECT 'SUPORTE', 'maquinas_virtuais' UNION ALL
    SELECT 'SUPORTE', 'containers' UNION ALL
    SELECT 'SUPORTE', 'backups_pbs' UNION ALL
    SELECT 'SUPORTE', 'monitoramento_zabbix' UNION ALL
    SELECT 'SUPORTE', 'backup_nas'
) v ON v.codigo = p.codigo;
