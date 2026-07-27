CREATE TABLE IF NOT EXISTS implantacao_kanban_colunas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    codigo VARCHAR(60) NOT NULL,
    titulo VARCHAR(120) NOT NULL,
    ordem INT NOT NULL DEFAULT 10,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    sistema TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_implantacao_kanban_colunas_codigo (codigo),
    KEY idx_implantacao_kanban_colunas_ativo_ordem (ativo, ordem)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'FILA', 'Fila', 10, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'FILA');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'CRIACAO_GRUPO', 'Criação de Grupo', 20, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'CRIACAO_GRUPO');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'KICKOFF', 'Kickoff', 30, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'KICKOFF');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'VPN', 'VPN', 40, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'VPN');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'PROVISIONAMENTO_SERVIDORES', 'Provisionamento de Servidores', 50, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'PROVISIONAMENTO_SERVIDORES');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'PARAMETRIZACAO_SOFTWARE', 'Parametrização de Software', 60, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'PARAMETRIZACAO_SOFTWARE');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'PARAMETRIZACAO_VR_SOFT', 'Parametrização VR Soft', 70, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'PARAMETRIZACAO_VR_SOFT');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'PARAMETRIZACAO_LOGUS', 'Parametrização Logus', 80, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'PARAMETRIZACAO_LOGUS');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'PARAMETRIZACAO_DBSCIENCE', 'Parametrização DBScience', 90, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'PARAMETRIZACAO_DBSCIENCE');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'PARAMETRIZACAO_HAARE', 'Parametrização Haare', 100, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'PARAMETRIZACAO_HAARE');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'PARAMETRIZACAO_TARGET', 'Parametrização Target', 110, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'PARAMETRIZACAO_TARGET');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'PARAMETRIZACAO_O3_CLOUD', 'Parametrização O3 Cloud', 120, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'PARAMETRIZACAO_O3_CLOUD');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'PARAMETRIZACAO_LJ_SISTEMAS', 'Parametrização LJ Sistemas', 130, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'PARAMETRIZACAO_LJ_SISTEMAS');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'PARAMETRIZACAO_E_GESTORA', 'Parametrização E-Gestora', 140, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'PARAMETRIZACAO_E_GESTORA');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'HOMOLOGACAO', 'Homologação', 150, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'HOMOLOGACAO');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'VIRADA', 'Virada', 160, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'VIRADA');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'REVISAO', 'Revisão', 170, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'REVISAO');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'FINALIZADO', 'Finalizado', 180, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'FINALIZADO');
INSERT INTO implantacao_kanban_colunas (uuid, codigo, titulo, ordem, ativo, sistema)
SELECT UUID(), 'CANCELADOS', 'Cancelados', 190, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM implantacao_kanban_colunas WHERE codigo = 'CANCELADOS');
