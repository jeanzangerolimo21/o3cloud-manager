CREATE TABLE IF NOT EXISTS proxmox_vm_inventory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    node VARCHAR(120) NOT NULL,
    vmid INT NOT NULL,
    tipo VARCHAR(20) NOT NULL DEFAULT 'qemu',
    nome VARCHAR(180) NULL,
    status VARCHAR(40) NULL,
    cpu_cores DECIMAL(10,2) NULL,
    memoria_mb BIGINT NULL,
    disco_gb DECIMAL(15,2) NULL,
    ips TEXT NULL,
    tags VARCHAR(255) NULL,
    template TINYINT(1) NOT NULL DEFAULT 0,
    uptime_seconds BIGINT NULL,
    cliente_id BIGINT NULL,
    contrato_id BIGINT NULL,
    implantacao_id BIGINT NULL,
    ultimo_sync_em DATETIME NULL,
    raw_payload LONGTEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_proxmox_vm_inventory_integracao_node_vmid (integracao_id, node, vmid),
    KEY idx_proxmox_vm_inventory_status (status, ativo),
    KEY idx_proxmox_vm_inventory_cliente (cliente_id),
    KEY idx_proxmox_vm_inventory_contrato (contrato_id),
    KEY idx_proxmox_vm_inventory_implantacao (implantacao_id),
    CONSTRAINT fk_proxmox_vm_inventory_integracao
        FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_proxmox_vm_inventory_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_proxmox_vm_inventory_contrato
        FOREIGN KEY (contrato_id)
        REFERENCES contratos (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_proxmox_vm_inventory_implantacao
        FOREIGN KEY (implantacao_id)
        REFERENCES implantacoes (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS proxmox_vm_sync_execucoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    modo VARCHAR(30) NOT NULL DEFAULT 'MANUAL',
    status VARCHAR(40) NOT NULL DEFAULT 'PENDENTE',
    iniciada_em DATETIME NULL,
    finalizada_em DATETIME NULL,
    vms_lidas INT NOT NULL DEFAULT 0,
    vms_atualizadas INT NOT NULL DEFAULT 0,
    mensagem TEXT NULL,
    executado_por VARCHAR(150) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_proxmox_vm_sync_integracao_status (integracao_id, status),
    KEY idx_proxmox_vm_sync_iniciada (iniciada_em),
    CONSTRAINT fk_proxmox_vm_sync_integracao
        FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
