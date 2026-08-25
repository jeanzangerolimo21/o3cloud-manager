ALTER TABLE crm_sucesso_cliente_pesquisas
    ADD COLUMN IF NOT EXISTS lote_uuid CHAR(36) NULL AFTER token,
    ADD COLUMN IF NOT EXISTS titulo VARCHAR(160) NULL AFTER cliente_id,
    ADD COLUMN IF NOT EXISTS referencia_data DATE NULL AFTER titulo,
    ADD KEY IF NOT EXISTS idx_cs_pesquisa_lote (lote_uuid),
    ADD KEY IF NOT EXISTS idx_cs_pesquisa_referencia (referencia_data);

UPDATE crm_sucesso_cliente_pesquisas
SET lote_uuid = uuid,
    referencia_data = DATE(created_at),
    titulo = 'Pesquisa de satisfação da implantação'
WHERE lote_uuid IS NULL OR referencia_data IS NULL OR titulo IS NULL;
