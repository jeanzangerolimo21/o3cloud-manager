ALTER TABLE financeiro_premiacoes_adendos
    ADD COLUMN IF NOT EXISTS campanha_id BIGINT NULL AFTER cliente_id,
    ADD INDEX IF NOT EXISTS idx_financeiro_premiacoes_adendos_campanha (campanha_id);

SET @fk_premiacoes_adendos_campanha := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'financeiro_premiacoes_adendos'
      AND CONSTRAINT_NAME = 'fk_financeiro_premiacoes_adendos_campanha'
);

SET @sql_premiacoes_adendos_campanha := IF(
    @fk_premiacoes_adendos_campanha = 0,
    'ALTER TABLE financeiro_premiacoes_adendos ADD CONSTRAINT fk_financeiro_premiacoes_adendos_campanha FOREIGN KEY (campanha_id) REFERENCES regras_campanhas_comissao(id)',
    'SELECT 1'
);

PREPARE stmt_premiacoes_adendos_campanha FROM @sql_premiacoes_adendos_campanha;
EXECUTE stmt_premiacoes_adendos_campanha;
DEALLOCATE PREPARE stmt_premiacoes_adendos_campanha;
