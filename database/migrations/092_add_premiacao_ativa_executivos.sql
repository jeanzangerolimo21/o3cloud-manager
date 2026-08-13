ALTER TABLE parceiros_executivos
    ADD COLUMN IF NOT EXISTS premiacao_ativa TINYINT(1) NOT NULL DEFAULT 0 AFTER informacoes_pagamento;
