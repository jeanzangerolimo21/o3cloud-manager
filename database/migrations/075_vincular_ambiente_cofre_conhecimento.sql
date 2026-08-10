ALTER TABLE implantacao_cofre_senhas
    ADD COLUMN IF NOT EXISTS ambiente_id BIGINT NULL AFTER cliente_cnpj,
    ADD KEY IF NOT EXISTS idx_implantacao_cofre_ambiente_id (ambiente_id);

ALTER TABLE implantacao_cofre_senhas
    ADD CONSTRAINT fk_implantacao_cofre_ambiente
        FOREIGN KEY (ambiente_id)
        REFERENCES ambientes (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;

ALTER TABLE kb_bases
    ADD COLUMN IF NOT EXISTS ambiente_id BIGINT NULL AFTER caminho_relativo,
    ADD KEY IF NOT EXISTS idx_kb_bases_ambiente_id (ambiente_id);

ALTER TABLE kb_bases
    ADD CONSTRAINT fk_kb_bases_ambiente
        FOREIGN KEY (ambiente_id)
        REFERENCES ambientes (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
