ALTER TABLE produtos
    ADD COLUMN parceiro_id BIGINT NULL AFTER categoria_id,
    ADD KEY idx_produtos_parceiro (parceiro_id),
    ADD CONSTRAINT fk_produtos_parceiro
        FOREIGN KEY (parceiro_id)
        REFERENCES parceiros (id);
