ALTER TABLE proxmox_node_inventory
    ADD COLUMN IF NOT EXISTS disco_disponivel_gb DECIMAL(15,2) NULL AFTER disco_usado_gb,
    ADD COLUMN IF NOT EXISTS storages_qtd INT NOT NULL DEFAULT 0 AFTER disco_disponivel_gb;
