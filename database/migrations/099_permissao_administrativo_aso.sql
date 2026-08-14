INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT perfil_id, 'administrativo_aso', permitido, nivel_acesso
FROM auth_perfil_permissoes
WHERE menu_key = 'administrativo'
  AND permitido = 1
ON DUPLICATE KEY UPDATE
    permitido = VALUES(permitido),
    nivel_acesso = VALUES(nivel_acesso);
