ALTER TABLE contratos_adendos
    ADD COLUMN IF NOT EXISTS valor_setup DECIMAL(15,2) NOT NULL DEFAULT 0.00 AFTER valor_pontual;

ALTER TABLE implantacoes
    ADD COLUMN IF NOT EXISTS adendo_id BIGINT NULL AFTER contrato_id,
    ADD COLUMN IF NOT EXISTS origem VARCHAR(20) NOT NULL DEFAULT 'CONTRATO' AFTER adendo_id;

ALTER TABLE implantacoes
    DROP INDEX IF EXISTS uk_implantacoes_contrato_ativo,
    ADD INDEX idx_implantacoes_adendo (adendo_id, ativo),
    ADD UNIQUE KEY uk_implantacoes_adendo (adendo_id),
    ADD CONSTRAINT fk_implantacoes_adendo
        FOREIGN KEY (adendo_id) REFERENCES contratos_adendos(id)
        ON DELETE RESTRICT ON UPDATE CASCADE;
