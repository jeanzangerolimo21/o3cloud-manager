-- Vinculos iniciais de servicos Omie ao catalogo para a Sprint 11.
-- Idempotente: pode ser executado novamente sem duplicar produtos.
-- Observacao: valor_custo permanece 0.00 enquanto a fonte oficial de custo nao for validada.

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
SELECT UUID(), 'INFRAESTRUTURA', 'Infraestrutura', 'Servicos de infraestrutura cloud vinculados ao Omie.', '#198754', 20, 1
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM produtos_categorias WHERE codigo = 'INFRAESTRUTURA'
);

INSERT INTO produtos_categorias (
    uuid,
    codigo,
    nome,
    descricao,
    cor,
    ordem,
    ativo
)
SELECT UUID(), 'BACKUP', 'Backup', 'Servicos de backup e cobrancas relacionadas.', '#6f42c1', 30, 1
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM produtos_categorias WHERE codigo = 'BACKUP'
);

DROP TEMPORARY TABLE IF EXISTS tmp_catalogo_omie_sprint11;
CREATE TEMPORARY TABLE tmp_catalogo_omie_sprint11 (
    categoria_codigo VARCHAR(30) NOT NULL,
    produto_codigo VARCHAR(30) NOT NULL,
    codigo_externo VARCHAR(50) NOT NULL,
    nome VARCHAR(150) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    unidade VARCHAR(30) NOT NULL,
    tipo_recurso VARCHAR(20) NOT NULL,
    valor_venda DECIMAL(12,2) NOT NULL,
    valor_custo DECIMAL(12,2) NOT NULL,
    ordem INT NOT NULL DEFAULT 0
) ENGINE=Memory;

INSERT INTO tmp_catalogo_omie_sprint11 (
    categoria_codigo,
    produto_codigo,
    codigo_externo,
    nome,
    descricao,
    unidade,
    tipo_recurso,
    valor_venda,
    valor_custo,
    ordem
) VALUES
('INFRAESTRUTURA', 'OMIE_SVC_11594065909', '11594065909', 'Infraestrutura Servidores Cloud', 'Vinculo do servico Omie INFRAESTRUTURA SERVIDORES CLOUD ao catalogo.', 'UN', 'SERVICO', 0.00, 0.00, 10),
('LICENCIAMENTO', 'OMIE_SVC_11582064055', '11582064055', 'Licenciamento de Uso O3 Cloud', 'Vinculo do servico Omie LICENCIAMENTO DE USO O3 CLOUD ao catalogo.', 'UN', 'LICENCA', 0.00, 0.00, 20),
('BACKUP', 'OMIE_SVC_11669237290', '11669237290', 'O3 Cloud Backup Retroativo', 'Vinculo do servico Omie de parcelamento retroativo O3 Cloud Backup ao catalogo.', 'UN', 'BACKUP', 0.00, 0.00, 30),
('INFRAESTRUTURA', 'OMIE_SVC_11582049146', '11582049146', 'Pacote Upgrade O3 Cloud', 'Vinculo do servico Omie PACOTE UPGRADE ao catalogo.', 'UN', 'SERVICO', 0.00, 0.00, 40),
('LICENCIAMENTO', 'OMIE_SVC_11611378386', '11611378386', 'Licenciamento O3 Cloud Files', 'Vinculo do servico Omie LICENCIAMENTO O3 CLOUD FILES ao catalogo.', 'UN', 'LICENCA', 0.00, 0.00, 50),
('LICENCIAMENTO', 'OMIE_SVC_11611366206', '11611366206', 'Licenciamento Servidor de Arquivos e AD', 'Vinculo do servico Omie LICENCIAMENTO - SERVIDOR DE ARQUIVOS + AD ao catalogo.', 'UN', 'LICENCA', 0.00, 0.00, 60),
('INFRAESTRUTURA', 'OMIE_SVC_11594073198', '11594073198', 'Endereco IPv4 IPv6 Fixo', 'Vinculo do servico Omie ENDERECO IPV4/IPV6 FIXO ao catalogo.', 'UN', 'SERVICO', 0.00, 0.00, 70);

UPDATE produtos p
JOIN tmp_catalogo_omie_sprint11 src
    ON src.produto_codigo = p.codigo
JOIN produtos_categorias c
    ON c.codigo = src.categoria_codigo
SET p.categoria_id = c.id,
    p.codigo_externo = src.codigo_externo,
    p.nome = src.nome,
    p.descricao = src.descricao,
    p.unidade = src.unidade,
    p.tipo_recurso = src.tipo_recurso,
    p.valor_venda = src.valor_venda,
    p.valor_custo = src.valor_custo,
    p.origem = 'OMIE',
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
    src.codigo_externo,
    src.nome,
    src.descricao,
    src.unidade,
    src.tipo_recurso,
    src.valor_venda,
    src.valor_custo,
    'OMIE',
    1
FROM tmp_catalogo_omie_sprint11 src
JOIN produtos_categorias c
    ON c.codigo = src.categoria_codigo
LEFT JOIN produtos p
    ON p.codigo = src.produto_codigo
WHERE p.id IS NULL;

DROP TEMPORARY TABLE IF EXISTS tmp_catalogo_omie_sprint11;

COMMIT;
