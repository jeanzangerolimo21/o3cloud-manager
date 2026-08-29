INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT perfil_id, 'proxmox_agendamentos', 1, nivel_acesso
FROM auth_perfil_permissoes
WHERE menu_key IN ('maquinas_virtuais', 'nodes')
  AND permitido = 1
ON DUPLICATE KEY UPDATE permitido = 1, nivel_acesso = VALUES(nivel_acesso);
