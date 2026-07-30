ALTER TABLE o3web_licencas
    ADD COLUMN cliente_id BIGINT NULL AFTER uuid,
    ADD COLUMN cliente_cnpj VARCHAR(32) NULL AFTER cliente_nome,
    ADD INDEX idx_o3web_licencas_cliente_id (cliente_id),
    ADD INDEX idx_o3web_licencas_cliente_cnpj (cliente_cnpj),
    ADD CONSTRAINT fk_o3web_licencas_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
