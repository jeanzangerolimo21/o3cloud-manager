ALTER TABLE administrativo_aso_lembretes
    ADD COLUMN IF NOT EXISTS enviar_email TINYINT(1) NOT NULL DEFAULT 1 AFTER tipo_participacao;
