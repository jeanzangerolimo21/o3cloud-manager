ALTER TABLE crm_propostas
    ADD COLUMN IF NOT EXISTS comentarios_comerciais TEXT NULL AFTER observacoes,
    ADD COLUMN IF NOT EXISTS semaforo_fechamento ENUM('FRIO', 'MORNO', 'QUENTE') NOT NULL DEFAULT 'FRIO' AFTER comentarios_comerciais;

UPDATE crm_propostas
SET semaforo_fechamento = CASE
    WHEN status = 'APROVADA' THEN 'QUENTE'
    WHEN status IN ('ENVIADA', 'EM_ANALISE') THEN 'MORNO'
    ELSE 'FRIO'
END
WHERE semaforo_fechamento IS NULL OR semaforo_fechamento = 'FRIO';
