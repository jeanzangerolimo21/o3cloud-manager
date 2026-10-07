ALTER TABLE contratos_adendos
    ADD COLUMN valor_setup DECIMAL(15,2) NOT NULL DEFAULT 0.00 AFTER valor_pontual;

ALTER TABLE implantacoes
    DROP INDEX uk_implantacoes_contrato_ativo,
    ADD COLUMN adendo_id BIGINT NULL AFTER contrato_id,
    ADD COLUMN origem VARCHAR(20) NOT NULL DEFAULT 'CONTRATO' AFTER adendo_id,
    ADD COLUMN contrato_principal_ativo_id BIGINT
        GENERATED ALWAYS AS (CASE WHEN ativo = 1 AND adendo_id IS NULL THEN contrato_id ELSE NULL END) STORED,
    ADD COLUMN adendo_ativo_id BIGINT
        GENERATED ALWAYS AS (CASE WHEN ativo = 1 THEN adendo_id ELSE NULL END) STORED,
    ADD INDEX idx_implantacoes_adendo (adendo_id, ativo),
    ADD UNIQUE KEY uk_implantacoes_contrato_principal_ativo (contrato_principal_ativo_id),
    ADD UNIQUE KEY uk_implantacoes_adendo_ativo (adendo_ativo_id),
    ADD CONSTRAINT fk_implantacoes_adendo
        FOREIGN KEY (adendo_id) REFERENCES contratos_adendos(id)
        ON DELETE RESTRICT ON UPDATE CASCADE;
