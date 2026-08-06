ALTER TABLE config_email_servicos
    ADD COLUMN IF NOT EXISTS provedor VARCHAR(20) NOT NULL DEFAULT 'SMTP' AFTER nome,
    ADD COLUMN IF NOT EXISTS brevo_sender_email VARCHAR(255) NULL AFTER smtp_from,
    ADD COLUMN IF NOT EXISTS brevo_sender_name VARCHAR(160) NULL AFTER brevo_sender_email,
    ADD COLUMN IF NOT EXISTS brevo_reply_to VARCHAR(255) NULL AFTER brevo_sender_name,
    ADD COLUMN IF NOT EXISTS brevo_daily_limit INT NULL AFTER brevo_reply_to,
    ADD COLUMN IF NOT EXISTS brevo_environment VARCHAR(30) NULL AFTER brevo_daily_limit,
    ADD COLUMN IF NOT EXISTS brevo_api_url VARCHAR(255) NULL AFTER brevo_environment,
    ADD COLUMN IF NOT EXISTS brevo_api_key_encrypted TEXT NULL AFTER brevo_api_url,
    ADD KEY IF NOT EXISTS idx_config_email_servicos_provedor (provedor);