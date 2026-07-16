-- Limpeza completa do Catalogo Tecnico para reimportacao, incluindo precos.
-- Execute apenas se os dados atuais forem descartaveis.

START TRANSACTION;

DELETE FROM produto_recursos;
DELETE FROM produto_servidores;
DELETE FROM comercial_precos;
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
SELECT 'comercial_precos', COUNT(*) FROM comercial_precos
UNION ALL
SELECT 'produto_servidores', COUNT(*) FROM produto_servidores
UNION ALL
SELECT 'produto_recursos', COUNT(*) FROM produto_recursos;
