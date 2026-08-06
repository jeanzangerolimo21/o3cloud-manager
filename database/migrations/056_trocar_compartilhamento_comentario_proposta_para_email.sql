ALTER TABLE crm_proposta_comentario_compartilhamentos
    DROP FOREIGN KEY fk_proposta_comentario_comp_usuario;

ALTER TABLE crm_proposta_comentario_compartilhamentos
    ADD COLUMN email VARCHAR(180) NULL AFTER comentario_id;

UPDATE crm_proposta_comentario_compartilhamentos c
INNER JOIN auth_usuarios u ON u.id = c.usuario_id
SET c.email = LOWER(COALESCE(NULLIF(u.email, ''), u.login));

DELETE FROM crm_proposta_comentario_compartilhamentos
WHERE email IS NULL OR email = '';

ALTER TABLE crm_proposta_comentario_compartilhamentos
    DROP INDEX uk_proposta_comentario_usuario,
    DROP INDEX idx_proposta_comentario_comp_usuario,
    DROP COLUMN usuario_id,
    MODIFY email VARCHAR(180) NOT NULL,
    ADD UNIQUE KEY uk_proposta_comentario_email (comentario_id, email),
    ADD KEY idx_proposta_comentario_comp_email (email);
