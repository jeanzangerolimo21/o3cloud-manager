ALTER TABLE proxmox_vm_inventory
    ADD COLUMN IF NOT EXISTS cpu_sockets INT NOT NULL DEFAULT 1 AFTER cpu_cores;


UPDATE proxmox_vm_inventory
SET cpu_sockets = CAST(JSON_UNQUOTE(JSON_EXTRACT(raw_payload, '$.config.sockets')) AS UNSIGNED)
WHERE raw_payload IS NOT NULL
  AND JSON_UNQUOTE(JSON_EXTRACT(raw_payload, '$.config.sockets')) REGEXP '^[0-9]+$';
