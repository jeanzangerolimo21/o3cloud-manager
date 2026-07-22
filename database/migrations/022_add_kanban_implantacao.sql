ALTER TABLE implantacoes
    ADD COLUMN etapa_kanban VARCHAR(60) NOT NULL DEFAULT 'FILA' AFTER status,
    ADD COLUMN implantador_nome VARCHAR(150) NULL AFTER responsavel,
    ADD COLUMN implantador_email VARCHAR(150) NULL AFTER implantador_nome,
    ADD INDEX idx_implantacoes_etapa_kanban (etapa_kanban),
    ADD INDEX idx_implantacoes_implantador_email (implantador_email);
