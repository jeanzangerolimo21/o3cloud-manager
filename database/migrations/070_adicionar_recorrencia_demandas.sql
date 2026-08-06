ALTER TABLE administrativo_demandas
    ADD COLUMN IF NOT EXISTS recorrente TINYINT(1) NOT NULL DEFAULT 0 AFTER possui_anexos,
    ADD COLUMN IF NOT EXISTS recorrencia_tipo VARCHAR(20) NULL AFTER recorrente,
    ADD COLUMN IF NOT EXISTS recorrencia_dia_semana TINYINT NULL AFTER recorrencia_tipo,
    ADD COLUMN IF NOT EXISTS recorrencia_dia_mes TINYINT NULL AFTER recorrencia_dia_semana,
    ADD COLUMN IF NOT EXISTS recorrencia_mes TINYINT NULL AFTER recorrencia_dia_mes,
    ADD COLUMN IF NOT EXISTS recorrencia_data_fim DATE NULL AFTER recorrencia_mes,
    ADD COLUMN IF NOT EXISTS recorrencia_id BIGINT NULL AFTER recorrencia_data_fim,
    ADD KEY idx_adm_demandas_recorrencia (recorrencia_id, data_limite);
