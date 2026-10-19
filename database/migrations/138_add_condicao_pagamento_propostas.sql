ALTER TABLE crm_propostas
    ADD COLUMN condicao_pagamento VARCHAR(40) NULL AFTER prazo_contratual_meses;
