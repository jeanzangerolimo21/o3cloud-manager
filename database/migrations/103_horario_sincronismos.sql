ALTER TABLE config_sincronismos_agendados
    ADD COLUMN IF NOT EXISTS horario_execucao TIME NULL AFTER frequencia_minutos;
