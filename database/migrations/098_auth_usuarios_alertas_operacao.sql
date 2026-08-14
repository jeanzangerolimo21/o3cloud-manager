ALTER TABLE auth_usuarios
    ADD COLUMN IF NOT EXISTS receber_alertas_operacao TINYINT(1) NOT NULL DEFAULT 0 AFTER two_factor_configurado_em,
    ADD COLUMN IF NOT EXISTS alertas_operacao_periodicidade VARCHAR(20) NOT NULL DEFAULT 'DIARIA' AFTER receber_alertas_operacao,
    ADD COLUMN IF NOT EXISTS alertas_operacao_horario TIME NOT NULL DEFAULT '08:00:00' AFTER alertas_operacao_periodicidade,
    ADD COLUMN IF NOT EXISTS alertas_operacao_ultimo_envio_em DATETIME NULL AFTER alertas_operacao_horario;

CREATE INDEX IF NOT EXISTS idx_auth_usuarios_alertas_operacao
    ON auth_usuarios (receber_alertas_operacao, status, alertas_operacao_periodicidade, alertas_operacao_horario);
