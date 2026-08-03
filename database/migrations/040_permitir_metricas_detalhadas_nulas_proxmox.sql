ALTER TABLE proxmox_vm_inventory
    MODIFY COLUMN discos_qtd INT NULL DEFAULT NULL,
    MODIFY COLUMN interfaces_qtd INT NULL DEFAULT NULL;
