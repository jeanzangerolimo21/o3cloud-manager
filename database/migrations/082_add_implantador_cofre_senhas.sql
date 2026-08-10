ALTER TABLE implantacao_cofre_senhas
    ADD COLUMN IF NOT EXISTS implantador_id BIGINT NULL AFTER ambiente_id,
    ADD KEY IF NOT EXISTS idx_implantacao_cofre_implantador_id (implantador_id);

ALTER TABLE implantacao_cofre_senhas
    ADD CONSTRAINT fk_implantacao_cofre_implantador
        FOREIGN KEY (implantador_id)
        REFERENCES implantadores (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
