UPDATE clientes SET cnpj = NULL WHERE cnpj IS NOT NULL AND TRIM(cnpj) = '';
UPDATE clientes SET cnpj = UPPER(REGEXP_REPLACE(cnpj, '[^0-9A-Za-z]', '')) WHERE cnpj IS NOT NULL;
