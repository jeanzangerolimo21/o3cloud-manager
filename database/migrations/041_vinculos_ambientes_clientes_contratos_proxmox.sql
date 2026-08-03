CREATE TABLE IF NOT EXISTS ambiente_clientes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    ambiente_id BIGINT NOT NULL,
    cliente_id BIGINT NOT NULL,
    principal TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_ambiente_clientes (ambiente_id, cliente_id),
    KEY idx_ambiente_clientes_cliente (cliente_id),
    CONSTRAINT fk_ambiente_clientes_ambiente
        FOREIGN KEY (ambiente_id) REFERENCES ambientes(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ambiente_clientes_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ambiente_contratos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    ambiente_id BIGINT NOT NULL,
    contrato_id BIGINT NOT NULL,
    principal TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_ambiente_contratos (ambiente_id, contrato_id),
    KEY idx_ambiente_contratos_contrato (contrato_id),
    CONSTRAINT fk_ambiente_contratos_ambiente
        FOREIGN KEY (ambiente_id) REFERENCES ambientes(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ambiente_contratos_contrato
        FOREIGN KEY (contrato_id) REFERENCES contratos(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ambiente_proxmox_recursos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    ambiente_id BIGINT NOT NULL,
    proxmox_inventory_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_ambiente_proxmox_recursos (ambiente_id, proxmox_inventory_id),
    KEY idx_ambiente_proxmox_recurso (proxmox_inventory_id),
    CONSTRAINT fk_ambiente_proxmox_recursos_ambiente
        FOREIGN KEY (ambiente_id) REFERENCES ambientes(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ambiente_proxmox_recursos_inventory
        FOREIGN KEY (proxmox_inventory_id) REFERENCES proxmox_vm_inventory(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO ambiente_clientes (uuid, ambiente_id, cliente_id, principal)
SELECT UUID(), id, cliente_id, 1
FROM ambientes
WHERE cliente_id IS NOT NULL;

INSERT IGNORE INTO ambiente_contratos (uuid, ambiente_id, contrato_id, principal)
SELECT UUID(), id, contrato_id, 1
FROM ambientes
WHERE contrato_id IS NOT NULL;
