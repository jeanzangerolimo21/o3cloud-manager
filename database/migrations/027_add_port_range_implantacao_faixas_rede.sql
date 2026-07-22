ALTER TABLE implantacao_faixas_rede
    ADD COLUMN porta_inicio INT NULL AFTER vpn,
    ADD COLUMN porta_fim INT NULL AFTER porta_inicio,
    ADD INDEX idx_implantacao_faixas_rede_fw_portas (fw_wan, porta_inicio, porta_fim);
