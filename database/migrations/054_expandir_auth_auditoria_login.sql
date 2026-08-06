ALTER TABLE auth_auditoria
    ADD COLUMN IF NOT EXISTS ip_origem VARCHAR(80) NULL AFTER detalhes,
    ADD COLUMN IF NOT EXISTS user_agent VARCHAR(255) NULL AFTER ip_origem;

ALTER TABLE auth_auditoria
    ADD KEY IF NOT EXISTS idx_auth_auditoria_usuario (usuario_email),
    ADD KEY IF NOT EXISTS idx_auth_auditoria_entidade_created (entidade, created_at);

DELETE FROM auth_auditoria
WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
