ALTER TABLE proxmox_agendamentos
    ADD COLUMN IF NOT EXISTS cpu_sockets_original INT NULL AFTER cpu_original,
    ADD COLUMN IF NOT EXISTS cpu_cores_por_socket_original INT NULL AFTER cpu_sockets_original,
    ADD COLUMN IF NOT EXISTS cpu_sockets_final INT NULL AFTER cpu_final,
    ADD COLUMN IF NOT EXISTS cpu_cores_por_socket_final INT NULL AFTER cpu_sockets_final;
