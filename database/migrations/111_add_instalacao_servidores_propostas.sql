ALTER TABLE crm_propostas
    ADD COLUMN instalacao_servidores DECIMAL(12,2) NOT NULL DEFAULT 0.00 AFTER setup_ambiente_cloud;

UPDATE crm_propostas
SET instalacao_servidores = GREATEST(
        COALESCE(total_instalacao, 0) - COALESCE(parametrizacao_sistema, 0) - COALESCE(setup_ambiente_cloud, 0),
        0
    );
