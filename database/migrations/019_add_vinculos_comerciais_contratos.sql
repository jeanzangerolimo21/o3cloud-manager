ALTER TABLE contratos
    ADD COLUMN contato_id BIGINT NULL AFTER cliente_id,
    ADD COLUMN proposta_id BIGINT NULL AFTER contato_id,
    ADD INDEX idx_contratos_contato_id (contato_id),
    ADD INDEX idx_contratos_proposta_id (proposta_id);
