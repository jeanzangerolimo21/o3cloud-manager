ALTER TABLE implantacoes
    ADD COLUMN implantacao_principal_id BIGINT NULL AFTER contrato_id,
    ADD INDEX idx_implantacoes_principal (implantacao_principal_id),
    ADD CONSTRAINT fk_implantacoes_principal
        FOREIGN KEY (implantacao_principal_id) REFERENCES implantacoes(id);
