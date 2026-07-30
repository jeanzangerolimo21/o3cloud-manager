ALTER TABLE clientes
    MODIFY COLUMN cnpj VARCHAR(32) NULL;

ALTER TABLE parceiros
    MODIFY COLUMN cnpj VARCHAR(32) NULL;

ALTER TABLE o3web_licencas
    MODIFY COLUMN cliente_cnpj VARCHAR(32) NULL;

ALTER TABLE implantacao_faixas_rede
    MODIFY COLUMN cliente_cnpj VARCHAR(32) NULL;

ALTER TABLE implantacao_cofre_senhas
    MODIFY COLUMN cliente_cnpj VARCHAR(32) NULL;
