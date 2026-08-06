ALTER TABLE parceiros
    ADD COLUMN IF NOT EXISTS categoria_parceiro VARCHAR(20) NULL AFTER segmento;

UPDATE parceiros
SET categoria_parceiro = 'PLATINIUM'
WHERE LOWER(COALESCE(informacoes_gerais, '')) LIKE '%categoria base44:%platinium%';

UPDATE parceiros
SET categoria_parceiro = 'OURO'
WHERE LOWER(COALESCE(informacoes_gerais, '')) LIKE '%categoria base44:%ouro%';

UPDATE parceiros
SET categoria_parceiro = 'PRATA'
WHERE LOWER(COALESCE(informacoes_gerais, '')) LIKE '%categoria base44:%prata%';

UPDATE parceiros
SET categoria_parceiro = 'BRONZE'
WHERE LOWER(COALESCE(informacoes_gerais, '')) LIKE '%categoria base44:%bronze%';
