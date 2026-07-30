ALTER TABLE parceiros
    ADD COLUMN cnpj VARCHAR(32) NULL AFTER uuid,
    ADD COLUMN segmento VARCHAR(100) NULL AFTER cnpj,
    ADD COLUMN razao_social VARCHAR(150) NULL AFTER segmento,
    ADD COLUMN nome_fantasia VARCHAR(150) NULL AFTER razao_social,
    ADD COLUMN endereco VARCHAR(200) NULL AFTER nome_fantasia,
    ADD COLUMN cidade VARCHAR(100) NULL AFTER endereco,
    ADD COLUMN uf CHAR(2) NULL AFTER cidade,
    ADD COLUMN contato_1_nome VARCHAR(150) NULL AFTER site,
    ADD COLUMN contato_1_email VARCHAR(150) NULL AFTER contato_1_nome,
    ADD COLUMN contato_1_telefone VARCHAR(30) NULL AFTER contato_1_email,
    ADD COLUMN contato_2_nome VARCHAR(150) NULL AFTER contato_1_telefone,
    ADD COLUMN contato_2_email VARCHAR(150) NULL AFTER contato_2_nome,
    ADD COLUMN contato_2_telefone VARCHAR(30) NULL AFTER contato_2_email,
    ADD COLUMN contato_3_nome VARCHAR(150) NULL AFTER contato_2_telefone,
    ADD COLUMN contato_3_email VARCHAR(150) NULL AFTER contato_3_nome,
    ADD COLUMN contato_3_telefone VARCHAR(30) NULL AFTER contato_3_email,
    ADD COLUMN executivo_responsavel_id BIGINT NULL AFTER contato_3_telefone,
    ADD COLUMN status_negociacao VARCHAR(30) NULL AFTER executivo_responsavel_id,
    ADD COLUMN informacoes_gerais TEXT NULL AFTER status_negociacao,
    ADD CONSTRAINT fk_parceiros_executivo_responsavel
        FOREIGN KEY (executivo_responsavel_id)
        REFERENCES parceiros_executivos (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
