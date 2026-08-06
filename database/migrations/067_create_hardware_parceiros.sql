CREATE TABLE IF NOT EXISTS dimensionamento_hardware_parceiros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    parceiro VARCHAR(120) NOT NULL,
    secao VARCHAR(120) NOT NULL,
    faixa_usuarios VARCHAR(80) NOT NULL,
    memoria VARCHAR(50) NULL,
    processador VARCHAR(50) NULL,
    disco VARCHAR(50) NULL,
    origem VARCHAR(80) NOT NULL DEFAULT 'MANUAL',
    ordem INT NOT NULL DEFAULT 0,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_dhp_parceiro (parceiro),
    INDEX idx_dhp_secao (secao),
    INDEX idx_dhp_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;