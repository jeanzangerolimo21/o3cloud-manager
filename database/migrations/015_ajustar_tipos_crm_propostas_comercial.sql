ALTER TABLE crm_propostas
    MODIFY COLUMN cliente_id BIGINT NULL,
    MODIFY COLUMN contato_id BIGINT NULL,
    MODIFY COLUMN parceiro_id BIGINT NULL,
    MODIFY COLUMN executivo_responsavel_id BIGINT NULL;

ALTER TABLE crm_propostas
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
    p.cliente_nome = COALESCE(p.cliente_nome, cli.nome_fantasia, cli.razao_social, o.empresa),
    p.contato_nome = COALESCE(p.contato_nome, c.nome),
    p.contato_email = COALESCE(p.contato_email, c.email),
    p.contato_telefone = COALESCE(p.contato_telefone, c.telefone, c.whatsapp),
    p.executivo_nome = COALESCE(p.executivo_nome, pe.nome),
    p.executivo_email = COALESCE(p.executivo_email, pe.email),
    p.executivo_telefone = COALESCE(p.executivo_telefone, pe.telefone),
    p.total_mensal = CASE WHEN COALESCE(p.total_mensal, 0) = 0 THEN COALESCE(p.valor_total, 0) ELSE p.total_mensal END,
    p.setup_dias = COALESCE(p.setup_dias, 7),
    p.mensalidade_dias = COALESCE(p.mensalidade_dias, 30),
    p.prazo_contratual_meses = COALESCE(p.prazo_contratual_meses, 24)
WHERE p.codigo_proposta IS NULL
   OR p.cliente_id IS NULL
   OR p.total_mensal = 0
   OR p.cliente_nome IS NULL;
