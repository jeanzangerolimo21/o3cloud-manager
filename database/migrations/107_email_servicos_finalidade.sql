ALTER TABLE config_email_servicos
    ADD COLUMN IF NOT EXISTS finalidade VARCHAR(40) NOT NULL DEFAULT 'GERAL' AFTER provedor,
    ADD KEY IF NOT EXISTS idx_config_email_servicos_finalidade (finalidade);

UPDATE config_email_servicos
SET finalidade = 'GERAL'
WHERE finalidade IS NULL OR finalidade = '';
