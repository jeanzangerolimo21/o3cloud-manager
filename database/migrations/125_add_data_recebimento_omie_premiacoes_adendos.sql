ALTER TABLE financeiro_premiacoes_adendos
    ADD COLUMN IF NOT EXISTS data_recebimento_omie DATE NULL AFTER data_lancamento,
    ADD INDEX IF NOT EXISTS idx_financeiro_premiacoes_adendos_recebimento (data_recebimento_omie);
