ALTER TABLE proxmox_vm_inventory
    ADD COLUMN IF NOT EXISTS discos_qtd INT NOT NULL DEFAULT 0 AFTER disco_gb,
    ADD COLUMN IF NOT EXISTS interfaces_qtd INT NOT NULL DEFAULT 0 AFTER discos_qtd;

CREATE INDEX IF NOT EXISTS idx_proxmox_vm_inventory_tipo_node ON proxmox_vm_inventory (tipo, node, ativo);
