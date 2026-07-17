ALTER TABLE crm_propostas
    DROP FOREIGN KEY fk_crm_propostas_oportunidade;

ALTER TABLE crm_propostas
    MODIFY COLUMN oportunidade_id BIGINT NULL;

ALTER TABLE crm_propostas
    ADD CONSTRAINT fk_crm_propostas_oportunidade
        FOREIGN KEY (oportunidade_id)
        REFERENCES crm_oportunidades (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
