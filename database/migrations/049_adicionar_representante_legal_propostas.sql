ALTER TABLE crm_propostas
    ADD COLUMN representante_legal_id BIGINT NULL AFTER contato_id,
    ADD INDEX idx_crm_propostas_representante_legal_id (representante_legal_id);
