DELETE FROM financeiro_recebimentos
WHERE contrato_id IS NULL
   OR cliente_id IS NULL
   OR COALESCE(numero_documento_fiscal, '') = '';
