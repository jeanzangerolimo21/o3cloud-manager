ALTER TABLE crm_sucesso_cliente_pesquisas
    ADD COLUMN IF NOT EXISTS comentario_texto TEXT NULL AFTER respostas_json;
