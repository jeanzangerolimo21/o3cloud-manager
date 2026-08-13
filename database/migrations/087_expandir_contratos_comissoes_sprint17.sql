ALTER TABLE contratos
    ADD COLUMN IF NOT EXISTS observacao_contrato TEXT NULL AFTER observacoes,
    ADD COLUMN IF NOT EXISTS vendedor_nome VARCHAR(150) NULL AFTER codigo_vendedor,
    ADD COLUMN IF NOT EXISTS projeto_nome VARCHAR(150) NULL AFTER codigo_projeto,
    ADD COLUMN IF NOT EXISTS valor_servicos_bruto DECIMAL(15,2) NULL AFTER valor_promocional,
    ADD COLUMN IF NOT EXISTS valor_descontos DECIMAL(15,2) NULL AFTER valor_servicos_bruto,
    ADD COLUMN IF NOT EXISTS valor_servicos_liquido DECIMAL(15,2) NULL AFTER valor_descontos,
    ADD INDEX IF NOT EXISTS idx_contratos_vendedor_nome (vendedor_nome),
    ADD INDEX IF NOT EXISTS idx_contratos_projeto_nome (projeto_nome);
