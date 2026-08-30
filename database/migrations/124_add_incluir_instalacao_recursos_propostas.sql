ALTER TABLE crm_propostas
    ADD COLUMN IF NOT EXISTS incluir_instalacao_recursos TINYINT(1) NOT NULL DEFAULT 0 AFTER setup_ambiente_cloud;
