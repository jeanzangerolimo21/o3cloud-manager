-- Carga inicial da Tabela de Precos do Catalogo Comercial.
-- Idempotente: pode ser executada novamente para atualizar os registros-base.

START TRANSACTION;

INSERT INTO produtos_categorias (
    uuid,
    codigo,
    nome,
    descricao,
    cor,
    ordem,
    ativo
)
SELECT
    UUID(),
    'LICENCIAMENTO',
    'Licenciamento',
    'Produtos de licenciamento por usuario.',
    '#0d6efd',
    10,
    1
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1
    FROM produtos_categorias
    WHERE codigo = 'LICENCIAMENTO'
);

DROP TEMPORARY TABLE IF EXISTS tmp_tabela_precos_licencas;
CREATE TEMPORARY TABLE tmp_tabela_precos_licencas (
    produto_codigo VARCHAR(30) NOT NULL,
    produto_nome VARCHAR(150) NOT NULL,
    software VARCHAR(100) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    usuarios_inicio INT NOT NULL,
    usuarios_fim INT NOT NULL,
    valor_mensal DECIMAL(12,2) NOT NULL,
    valor_setup DECIMAL(12,2) NOT NULL,
    tem_projeto TINYINT(1) NOT NULL DEFAULT 0,
    ordem INT NOT NULL DEFAULT 0
) ENGINE=Memory;

INSERT INTO tmp_tabela_precos_licencas (
    produto_codigo,
    produto_nome,
    software,
    descricao,
    usuarios_inicio,
    usuarios_fim,
    valor_mensal,
    valor_setup,
    tem_projeto,
    ordem
) VALUES
('LOGUS_STORE', 'Logus Store', 'Logus Store', 'Logus Store - Valor Fixo/ Usuario', 5, 5, 45.00, 42.00, 0, 5),
('LOGUS', 'Logus', 'Logus - 5 a 10 Usuarios', 'Logus - 5 a 10 Usuarios', 5, 10, 225.00, 205.00, 0, 10),
('LOGUS', 'Logus', 'Logus - 11 a 20 Usuarios', 'Logus - 11 a 20 Usuarios', 11, 20, 220.00, 195.00, 0, 20),
('LOGUS', 'Logus', 'Logus - 21 a 30 Usuarios', 'Logus - 21 a 30 Usuarios', 21, 30, 200.00, 155.00, 0, 30),
('LOGUS', 'Logus', 'Logus - 31 a 40 Usuarios', 'Logus - 31 a 40 Usuarios', 31, 40, 185.00, 125.00, 0, 40),
('LOGUS', 'Logus', 'Logus - 41 a 60 Usuarios', 'Logus - 41 a 60 Usuarios', 41, 60, 170.00, 120.00, 0, 60),
('TARGET', 'Target', 'Target 5-15 Usuarios', 'Servidores dedicado (BD e Aplicacao)', 5, 15, 145.00, 135.00, 0, 15),
('TARGET', 'Target', 'Target 15-25 Usuarios', 'Servidores dedicado (BD e Aplicacao)', 15, 25, 125.00, 120.00, 0, 25),
('TARGET', 'Target', 'Target 26-50 Usuarios', 'Servidores dedicado (BD e Aplicacao)', 26, 50, 92.00, 87.00, 0, 50),
('TARGET', 'Target', 'Target 51-100 Usuarios', 'Servidores dedicado (BD e Aplicacao)', 51, 100, 80.00, 75.00, 0, 100),
('USUARIO_ADICIONAL', 'Usuario Adicional', 'Usuario Adicional', 'Usuario adicional - O3 CLOUD', 1, 1, 180.00, 110.00, 0, 1),
('VR', 'VR', 'VR 2 Usuarios', 'VR 2 Usuarios', 2, 2, 299.00, 297.50, 1, 2),
('VR', 'VR', 'VR 3 Usuarios', 'VR 3 Usuarios', 3, 3, 205.00, 199.00, 1, 3),
('VR', 'VR', 'VR 4 Usuarios', 'VR 4 Usuarios', 4, 4, 155.00, 152.00, 1, 4),
('VR', 'VR', 'VR 5 Usuarios', 'VR 5 Usuarios', 5, 5, 160.00, 155.00, 1, 5),
('VR', 'VR', 'VR 06-10 Usuarios', 'VR 06-10 Usuarios', 6, 10, 150.00, 140.00, 1, 10),
('VR', 'VR', 'VR 11-20 Usuarios', 'VR 11-20 Usuarios', 11, 20, 135.00, 119.18, 1, 20),
('VR', 'VR', 'VR 21-30 Usuarios', 'VR 21-30 Usuarios', 21, 30, 125.00, 108.65, 1, 30),
('VR', 'VR', 'VR 31-40 Usuarios', 'VR 31-40 Usuarios', 31, 40, 120.00, 101.47, 1, 40),
('VR', 'VR', 'VR 41-60 Usuarios', 'VR 41-60 Usuarios', 41, 60, 115.00, 94.75, 1, 60),
('VR', 'VR', 'VR 61-90 Usuarios', 'VR 61-90 Usuarios', 61, 90, 95.00, 79.44, 1, 90),
('VR', 'VR', 'VR 91-120 Usuarios', 'VR 91-120 Usuarios', 91, 120, 92.00, 82.01, 1, 120);

UPDATE produtos p
JOIN (
    SELECT DISTINCT produto_codigo, produto_nome
    FROM tmp_tabela_precos_licencas
) src
    ON src.produto_codigo = p.codigo
JOIN produtos_categorias c
    ON c.codigo = 'LICENCIAMENTO'
SET p.categoria_id = c.id,
    p.nome = src.produto_nome,
    p.descricao = CONCAT('Produto de licenciamento: ', src.produto_nome),
    p.unidade = 'UN',
    p.tipo_recurso = 'LICENCA',
    p.valor_venda = 0,
    p.valor_custo = 0,
    p.origem = 'MANUAL',
    p.ativo = 1;

INSERT INTO produtos (
    uuid,
    categoria_id,
    codigo,
    codigo_externo,
    nome,
    descricao,
    unidade,
    tipo_recurso,
    valor_venda,
    valor_custo,
    origem,
    ativo
)
SELECT
    UUID(),
    c.id,
    src.produto_codigo,
    '',
    src.produto_nome,
    CONCAT('Produto de licenciamento: ', src.produto_nome),
    'UN',
    'LICENCA',
    0,
    0,
    'MANUAL',
    1
FROM (
    SELECT DISTINCT produto_codigo, produto_nome
    FROM tmp_tabela_precos_licencas
) src
JOIN produtos_categorias c
    ON c.codigo = 'LICENCIAMENTO'
LEFT JOIN produtos p
    ON p.codigo = src.produto_codigo
WHERE p.id IS NULL;

UPDATE produto_modelos pm
JOIN produtos p
    ON p.id = pm.produto_id
JOIN (
    SELECT DISTINCT produto_codigo
    FROM tmp_tabela_precos_licencas
) src
    ON src.produto_codigo = p.codigo
SET pm.nome = 'STANDARD',
    pm.descricao = 'Modelo padrao da tabela inicial de precos.',
    pm.ordem = 0,
    pm.padrao = 1,
    pm.versao = '',
    pm.ativo = 1
WHERE pm.codigo = 'STANDARD';

INSERT INTO produto_modelos (
    uuid,
    produto_id,
    codigo,
    nome,
    descricao,
    ordem,
    padrao,
    versao,
    ativo
)
SELECT
    UUID(),
    p.id,
    'STANDARD',
    'STANDARD',
    'Modelo padrao da tabela inicial de precos.',
    0,
    1,
    '',
    1
FROM produtos p
JOIN (
    SELECT DISTINCT produto_codigo
    FROM tmp_tabela_precos_licencas
) src
    ON src.produto_codigo = p.codigo
LEFT JOIN produto_modelos pm
    ON pm.produto_id = p.id
   AND pm.codigo = 'STANDARD'
WHERE pm.id IS NULL;

UPDATE produto_faixas pf
JOIN produto_modelos pm
    ON pm.id = pf.modelo_id
   AND pm.codigo = 'STANDARD'
JOIN produtos p
    ON p.id = pm.produto_id
JOIN tmp_tabela_precos_licencas src
    ON src.produto_codigo = p.codigo
   AND src.usuarios_inicio = pf.usuarios_inicio
   AND src.usuarios_fim = pf.usuarios_fim
SET pf.codigo = CONCAT('FX_', src.usuarios_inicio, '_', src.usuarios_fim),
    pf.nome = src.software,
    pf.descricao = src.descricao,
    pf.permite_upgrade_manual = 1,
    pf.ordem = src.ordem,
    pf.ativo = 1;

INSERT INTO produto_faixas (
    uuid,
    modelo_id,
    codigo,
    nome,
    usuarios_inicio,
    usuarios_fim,
    permite_upgrade_manual,
    descricao,
    ordem,
    ativo
)
SELECT
    UUID(),
    pm.id,
    CONCAT('FX_', src.usuarios_inicio, '_', src.usuarios_fim),
    src.software,
    src.usuarios_inicio,
    src.usuarios_fim,
    1,
    src.descricao,
    src.ordem,
    1
FROM tmp_tabela_precos_licencas src
JOIN produtos p
    ON p.codigo = src.produto_codigo
JOIN produto_modelos pm
    ON pm.produto_id = p.id
   AND pm.codigo = 'STANDARD'
LEFT JOIN produto_faixas pf
    ON pf.modelo_id = pm.id
   AND pf.usuarios_inicio = src.usuarios_inicio
   AND pf.usuarios_fim = src.usuarios_fim
WHERE pf.id IS NULL;

UPDATE comercial_precos cp
JOIN produto_faixas pf
    ON pf.id = cp.faixa_id
JOIN produto_modelos pm
    ON pm.id = pf.modelo_id
   AND pm.codigo = 'STANDARD'
JOIN produtos p
    ON p.id = pm.produto_id
JOIN tmp_tabela_precos_licencas src
    ON src.produto_codigo = p.codigo
   AND src.usuarios_inicio = pf.usuarios_inicio
   AND src.usuarios_fim = pf.usuarios_fim
SET cp.valor_mensal = src.valor_mensal,
    cp.valor_setup = src.valor_setup,
    cp.tem_projeto = src.tem_projeto,
    cp.ativo = 1;

INSERT INTO comercial_precos (
    uuid,
    faixa_id,
    valor_mensal,
    valor_setup,
    tem_projeto,
    ativo
)
SELECT
    UUID(),
    pf.id,
    src.valor_mensal,
    src.valor_setup,
    src.tem_projeto,
    1
FROM tmp_tabela_precos_licencas src
JOIN produtos p
    ON p.codigo = src.produto_codigo
JOIN produto_modelos pm
    ON pm.produto_id = p.id
   AND pm.codigo = 'STANDARD'
JOIN produto_faixas pf
    ON pf.modelo_id = pm.id
   AND pf.usuarios_inicio = src.usuarios_inicio
   AND pf.usuarios_fim = src.usuarios_fim
LEFT JOIN comercial_precos cp
    ON cp.faixa_id = pf.id
WHERE cp.id IS NULL;

DROP TEMPORARY TABLE IF EXISTS tmp_tabela_precos_recursos;
CREATE TEMPORARY TABLE tmp_tabela_precos_recursos (
    codigo VARCHAR(30) NOT NULL,
    categoria_recurso VARCHAR(100) NOT NULL,
    nome VARCHAR(150) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    valor_mensal DECIMAL(12,2) NOT NULL,
    valor_instalacao DECIMAL(12,2) NOT NULL,
    tipo_recurso VARCHAR(20) NOT NULL,
    ordem INT NOT NULL DEFAULT 0
) ENGINE=Memory;

INSERT INTO tmp_tabela_precos_recursos (
    codigo,
    categoria_recurso,
    nome,
    descricao,
    valor_mensal,
    valor_instalacao,
    tipo_recurso,
    ordem
) VALUES
('UPGRADE_A', 'Outro', 'Pacote upgrade A', '2vCPU, 8GB Memoria, 300GB NVME', 505.00, 0.00, 'SERVICO', 10),
('UPGRADE_B', 'Outro', 'Pacote upgrade B', '2vCPU, 8GB Memoria, 400GB NVME', 640.00, 0.00, 'SERVICO', 20),
('UPGRADE_C', 'Outro', 'Pacote upgrade C', '4vCPU, 12GB Memoria, 500GB NVME', 775.00, 0.00, 'SERVICO', 30),
('UPGRADE_D', 'Outro', 'Pacote upgrade D', '4vCPU, 20GB Memoria, 600GB NVME', 1038.00, 0.00, 'SERVICO', 40),
('NAS_STORAGE', 'Disco', 'NAS STORAGE', 'NAS Storage BKP', 0.50, 0.50, 'STORAGE', 50),
('VCPU', 'Processador', 'vCPUs', 'Processador virtual', 27.00, 0.00, 'CPU', 60),
('RAM', 'Memoria', 'RAM', 'Memoria dedicada', 9.50, 9.50, 'RAM', 70),
('NVME', 'Disco', 'NVME', 'Armazenamento NVME', 0.95, 0.95, 'DISCO', 80),
('SNAPSHOT_PADRAO_3_DIAS', 'Backup', 'SNAPSHOT PADRAO 3 DIAS', 'Padrao 3 Snapshots (1/dia)', 0.65, 0.65, 'BACKUP', 90),
('IPV4_IPV6', 'IP Fixo', 'IPV4/IPV6', '1 endereco IPv4/Ipv6 fixo', 85.00, 85.00, 'SERVICO', 100),
('SUPORTE_PREMIUM_VCPU', 'Suporte Premium', 'Suporte Premium P/vCPU', 'Atendimento prioritario', 20.00, 20.00, 'SERVICO', 110),
('WINDOWS_SERVER_VCPU', 'Sistema Operacional', 'Windows Server P/vCPU', 'Licenca SO', 60.00, 60.00, 'LICENCA', 120),
('O3_WEB', 'Call de Acesso', 'O3 WEB', 'Acesso via navegador', 24.90, 24.90, 'SERVICO', 130),
('REMOTEAPP_RDP', 'Call de Acesso', 'RemoteAPP/RDP', 'Acesso via RemoteAPP', 24.90, 24.90, 'SERVICO', 140),
('VPN_PEER_TO_PEER', 'VPN', 'VPN Peer to Peer', 'Conexao ponto a ponto', 65.00, 65.00, 'SERVICO', 150),
('VPN_CLIENT', 'VPN', 'VPN Client', 'VPN para multiplos clientes', 119.90, 150.00, 'SERVICO', 160);

UPDATE catalogo_recursos_servidor crs
JOIN tmp_tabela_precos_recursos src
    ON src.codigo = crs.codigo
SET crs.categoria = src.categoria_recurso,
    crs.nome = src.nome,
    crs.descricao = src.descricao,
    crs.tipo_recurso = src.tipo_recurso,
    crs.valor_mensal = src.valor_mensal,
    crs.valor_instalacao = src.valor_instalacao,
    crs.ordem = src.ordem,
    crs.ativo = 1;

INSERT INTO catalogo_recursos_servidor (
    uuid,
    codigo,
    categoria,
    nome,
    descricao,
    tipo_recurso,
    valor_mensal,
    valor_instalacao,
    ordem,
    ativo
)
SELECT
    UUID(),
    src.codigo,
    src.categoria_recurso,
    src.nome,
    src.descricao,
    src.tipo_recurso,
    src.valor_mensal,
    src.valor_instalacao,
    src.ordem,
    1
FROM tmp_tabela_precos_recursos src
LEFT JOIN catalogo_recursos_servidor crs
    ON crs.codigo = src.codigo
WHERE crs.id IS NULL;

COMMIT;

SELECT 'categorias_licenciamento' AS secao, COUNT(*) AS total
FROM produtos_categorias
WHERE codigo = 'LICENCIAMENTO'
UNION ALL
SELECT 'produtos_licenca', COUNT(*)
FROM produtos
WHERE codigo IN (
    SELECT DISTINCT produto_codigo
    FROM tmp_tabela_precos_licencas
)
UNION ALL
SELECT 'modelos_standard', COUNT(*)
FROM produto_modelos pm
INNER JOIN produtos p
    ON p.id = pm.produto_id
WHERE pm.codigo = 'STANDARD'
  AND p.codigo IN (
    SELECT DISTINCT produto_codigo
    FROM tmp_tabela_precos_licencas
)
UNION ALL
SELECT 'faixas_licenca', COUNT(*)
FROM produto_faixas pf
INNER JOIN produto_modelos pm
    ON pm.id = pf.modelo_id
INNER JOIN produtos p
    ON p.id = pm.produto_id
WHERE p.codigo IN (
    SELECT DISTINCT produto_codigo
    FROM tmp_tabela_precos_licencas
)
UNION ALL
SELECT 'precos_licenca', COUNT(*)
FROM comercial_precos cp
INNER JOIN produto_faixas pf
    ON pf.id = cp.faixa_id
INNER JOIN produto_modelos pm
    ON pm.id = pf.modelo_id
INNER JOIN produtos p
    ON p.id = pm.produto_id
WHERE p.codigo IN (
    SELECT DISTINCT produto_codigo
    FROM tmp_tabela_precos_licencas
)
UNION ALL
SELECT 'recursos_servidor', COUNT(*)
FROM catalogo_recursos_servidor
WHERE codigo IN (
    SELECT codigo
    FROM tmp_tabela_precos_recursos
);
