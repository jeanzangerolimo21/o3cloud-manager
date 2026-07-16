START TRANSACTION;

INSERT INTO catalogo_recursos_servidor (
    uuid,
    codigo,
    categoria,
    nome,
    descricao,
    tipo_recurso,
    valor_mensal,
    valor_instalacao,
    ordem,
    ativo
)
SELECT
    UUID(),
    p.codigo,
    COALESCE(NULLIF(p.codigo_externo, ''), 'Outro'),
    p.nome,
    p.descricao,
    p.tipo_recurso,
    p.valor_venda,
    p.valor_custo,
    0,
    p.ativo
FROM produtos p
INNER JOIN produtos_categorias c
    ON c.id = p.categoria_id
LEFT JOIN catalogo_recursos_servidor crs
    ON crs.codigo = p.codigo
WHERE c.codigo = 'RECURSOS_CLOUD'
  AND crs.id IS NULL;

UPDATE catalogo_recursos_servidor crs
INNER JOIN produtos p
    ON p.codigo = crs.codigo
INNER JOIN produtos_categorias c
    ON c.id = p.categoria_id
SET crs.categoria = COALESCE(NULLIF(p.codigo_externo, ''), crs.categoria),
    crs.nome = p.nome,
    crs.descricao = p.descricao,
    crs.tipo_recurso = p.tipo_recurso,
    crs.valor_mensal = p.valor_venda,
    crs.valor_instalacao = p.valor_custo,
    crs.ativo = p.ativo
WHERE c.codigo = 'RECURSOS_CLOUD';

COMMIT;
