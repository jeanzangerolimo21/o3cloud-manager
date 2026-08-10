INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT p.id, 'eventos_participante_manual', 1, 'EDICAO'
FROM auth_perfis p
WHERE p.codigo = 'ADMIN'
ON DUPLICATE KEY UPDATE permitido=1, nivel_acesso='EDICAO';
