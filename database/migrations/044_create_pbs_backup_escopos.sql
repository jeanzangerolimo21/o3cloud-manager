CREATE TABLE IF NOT EXISTS pbs_backup_escopos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    integracao_id BIGINT NOT NULL,
    nome VARCHAR(150) NOT NULL,
    datastore VARCHAR(120) NOT NULL,
    namespaces TEXT NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    observacoes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_pbs_backup_escopo_integracao_nome (integracao_id, nome),
    KEY idx_pbs_backup_escopo_integracao_ativo (integracao_id, ativo),
    CONSTRAINT fk_pbs_backup_escopo_integracao
        FOREIGN KEY (integracao_id)
        REFERENCES implantacao_integracoes_config (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO pbs_backup_escopos (uuid, integracao_id, nome, datastore, namespaces, ativo, observacoes)
SELECT UUID(), i.id, 'Cluster C1 - DISCO2', 'DISCO2',
       'EVEO-SP-C1-03
EVEO-SP-C1-04
EVEO-SP-C1-05
EVEO-SP-C1-06
EVEO-SP-C1-07
EVEO-SP-C1-08
EVEO-SP-C1-09
EVEO-SP-C1-10
EVEO-SP-C1-11',
       1, 'Escopo inicial criado a partir do mapeamento operacional informado.'
FROM implantacao_integracoes_config i
WHERE i.tipo = 'pbs' AND i.ativo = 1
  AND NOT EXISTS (
      SELECT 1 FROM pbs_backup_escopos e
      WHERE e.integracao_id = i.id AND e.nome = 'Cluster C1 - DISCO2'
  )
ORDER BY i.id
LIMIT 1;
