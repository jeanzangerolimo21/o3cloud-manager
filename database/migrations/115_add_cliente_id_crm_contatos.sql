ALTER TABLE crm_contatos
    ADD COLUMN IF NOT EXISTS cliente_id BIGINT NULL AFTER lead_id,
    ADD INDEX IF NOT EXISTS idx_crm_contatos_cliente_id (cliente_id),
    ADD CONSTRAINT fk_crm_contatos_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;

UPDATE crm_contatos c
JOIN clientes cli
  ON c.cliente_id IS NULL
 AND c.empresa IS NOT NULL
 AND TRIM(c.empresa) <> ''
 AND (
      UPPER(TRIM(c.empresa)) = UPPER(TRIM(cli.nome_fantasia))
      OR UPPER(TRIM(c.empresa)) = UPPER(TRIM(cli.razao_social))
 )
SET c.cliente_id = cli.id,
    c.empresa = COALESCE(cli.nome_fantasia, cli.razao_social, c.empresa);
