CREATE TABLE IF NOT EXISTS proxmox_agendamentos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    cluster_nome VARCHAR(180) NULL,
    cluster_base_url VARCHAR(255) NULL,
    inventario_id BIGINT NULL,
    node_nome VARCHAR(120) NOT NULL,
    vmid INT NOT NULL,
    vm_nome VARCHAR(180) NULL,
    tipo VARCHAR(20) NOT NULL DEFAULT 'qemu',
    cpu_original INT NULL,
    cpu_nova INT NULL,
    cpu_final INT NULL,
    memoria_original_mb BIGINT NULL,
    memoria_nova_mb BIGINT NULL,
    memoria_final_mb BIGINT NULL,
    status_original VARCHAR(40) NULL,
    status_final VARCHAR(40) NULL,
    executar_em DATETIME NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'AGENDADO',
    desligar_se_necessario TINYINT(1) NOT NULL DEFAULT 1,
    religar_automaticamente TINYINT(1) NOT NULL DEFAULT 1,
    motivo TEXT NOT NULL,
    mensagem_erro TEXT NULL,
    worker_id VARCHAR(120) NULL,
    iniciado_em DATETIME NULL,
    finalizado_em DATETIME NULL,
    cancelado_em DATETIME NULL,
    created_by VARCHAR(150) NULL,
    cancelled_by VARCHAR(150) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_proxmox_agendamentos_status_execucao (status, executar_em),
    KEY idx_proxmox_agendamentos_vm_status (integracao_id, node_nome, vmid, status),
    KEY idx_proxmox_agendamentos_inventario (inventario_id),
    CONSTRAINT fk_proxmox_agendamentos_integracao
        FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_proxmox_agendamentos_inventario
        FOREIGN KEY (inventario_id)
        REFERENCES proxmox_vm_inventory (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS proxmox_agendamentos_eventos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    agendamento_id BIGINT NOT NULL,
    status VARCHAR(40) NOT NULL,
    mensagem TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_proxmox_agendamentos_eventos_agendamento (agendamento_id, created_at),
    CONSTRAINT fk_proxmox_agendamentos_eventos_agendamento
        FOREIGN KEY (agendamento_id)
        REFERENCES proxmox_agendamentos (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
