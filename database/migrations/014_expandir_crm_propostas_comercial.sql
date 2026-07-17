ALTER TABLE crm_propostas
    ADD COLUMN cliente_id BIGINT NULL AFTER oportunidade_id,
    ADD COLUMN contato_id BIGINT NULL AFTER cliente_id,
    ADD COLUMN parceiro_id BIGINT NULL AFTER contato_id,
    ADD COLUMN executivo_responsavel_id BIGINT NULL AFTER parceiro_id,
    ADD COLUMN codigo_proposta VARCHAR(32) NULL AFTER executivo_responsavel_id,
    ADD COLUMN cliente_nome VARCHAR(180) NULL AFTER codigo_proposta,
    ADD COLUMN contato_nome VARCHAR(150) NULL AFTER cliente_nome,
    ADD COLUMN contato_email VARCHAR(150) NULL AFTER contato_nome,
    ADD COLUMN contato_telefone VARCHAR(30) NULL AFTER contato_email,
    ADD COLUMN executivo_nome VARCHAR(150) NULL AFTER contato_telefone,
    ADD COLUMN executivo_email VARCHAR(150) NULL AFTER executivo_nome,
    ADD COLUMN executivo_telefone VARCHAR(30) NULL AFTER executivo_email,
    ADD COLUMN setup_dias INT NOT NULL DEFAULT 7 AFTER validade,
    ADD COLUMN mensalidade_dias INT NOT NULL DEFAULT 30 AFTER setup_dias,
    ADD COLUMN prazo_contratual_meses INT NOT NULL DEFAULT 24 AFTER mensalidade_dias,
    ADD COLUMN detalhes_negociacao TEXT NULL AFTER prazo_contratual_meses,
    ADD COLUMN total_mensal DECIMAL(12,2) NOT NULL DEFAULT 0.00 AFTER valor_total,
    ADD COLUMN parametrizacao_sistema DECIMAL(12,2) NOT NULL DEFAULT 0.00 AFTER total_mensal,
    ADD COLUMN setup_ambiente_cloud DECIMAL(12,2) NOT NULL DEFAULT 0.00 AFTER parametrizacao_sistema,
    ADD COLUMN total_instalacao DECIMAL(12,2) NOT NULL DEFAULT 0.00 AFTER setup_ambiente_cloud,
    ADD COLUMN licencas_snapshot LONGTEXT NULL AFTER itens_snapshot,
    ADD COLUMN servidores_snapshot LONGTEXT NULL AFTER licencas_snapshot,
    ADD INDEX idx_crm_propostas_cliente_id (cliente_id),
    ADD INDEX idx_crm_propostas_contato_id (contato_id),
    ADD INDEX idx_crm_propostas_parceiro_id (parceiro_id),
    ADD INDEX idx_crm_propostas_executivo_id (executivo_responsavel_id);

UPDATE crm_propostas p
LEFT JOIN crm_oportunidades o
    ON o.id = p.oportunidade_id
LEFT JOIN clientes cli
    ON cli.id = o.cliente_id
LEFT JOIN crm_contatos c
    ON c.id = o.contato_id
LEFT JOIN parceiros_executivos pe
    ON pe.id = o.executivo_responsavel_id
SET
    p.cliente_id = o.cliente_id,
    p.contato_id = o.contato_id,
    p.parceiro_id = o.parceiro_id,
    p.executivo_responsavel_id = o.executivo_responsavel_id,
    p.codigo_proposta = COALESCE(p.codigo_proposta, CONCAT('O3-', DATE_FORMAT(COALESCE(p.created_at, NOW()), '%Y%m%d-%H%i'))),
    p.cliente_nome = COALESCE(cli.nome_fantasia, cli.razao_social, o.empresa),
    p.contato_nome = c.nome,
    p.contato_email = c.email,
    p.contato_telefone = COALESCE(c.telefone, c.whatsapp),
    p.executivo_nome = pe.nome,
    p.executivo_email = pe.email,
    p.executivo_telefone = pe.telefone,
    p.total_mensal = COALESCE(p.valor_total, 0),
    p.total_instalacao = 0,
    p.parametrizacao_sistema = 0,
    p.setup_ambiente_cloud = 0,
    p.setup_dias = 7,
    p.mensalidade_dias = 30,
    p.prazo_contratual_meses = 24
WHERE p.codigo_proposta IS NULL
   OR p.cliente_id IS NULL
   OR p.total_mensal = 0;
