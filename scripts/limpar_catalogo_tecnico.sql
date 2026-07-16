-- Limpeza operacional do Catalogo Tecnico para nova importacao Base44.
-- Escopo:
-- - produto_recursos
-- - produto_servidores
-- - produto_faixas
-- - produto_modelos
-- - produtos
-- - produtos_categorias
--
-- Nao remove tabelas auxiliares de tipos:
-- - produto_tipos_recurso
-- - produto_tipos_servidor
--
-- Execute apenas se tiver certeza de que os registros atuais sao de teste.

START TRANSACTION;

DELETE FROM produto_recursos;
DELETE FROM produto_servidores;
DELETE FROM produto_faixas;
DELETE FROM produto_modelos;
DELETE FROM produtos;
DELETE FROM produtos_categorias;

COMMIT;

SELECT 'produtos_categorias' AS tabela, COUNT(*) AS total FROM produtos_categorias
UNION ALL
SELECT 'produtos', COUNT(*) FROM produtos
UNION ALL
SELECT 'produto_modelos', COUNT(*) FROM produto_modelos
UNION ALL
SELECT 'produto_faixas', COUNT(*) FROM produto_faixas
UNION ALL
SELECT 'produto_servidores', COUNT(*) FROM produto_servidores
UNION ALL
SELECT 'produto_recursos', COUNT(*) FROM produto_recursos;
