INSERT INTO auth_perfis (uuid, nome, codigo, descricao, ativo, mostrar_valores)
SELECT UUID(), 'Administrativo Gestor', 'ADMINISTRATIVO_GESTOR', 'Cria, distribui, edita e acompanha demandas administrativas.', 1, 0
WHERE NOT EXISTS (SELECT 1 FROM auth_perfis WHERE codigo = 'ADMINISTRATIVO_GESTOR');

INSERT INTO auth_perfis (uuid, nome, codigo, descricao, ativo, mostrar_valores)
SELECT UUID(), 'Administrativo Colaborador', 'ADMINISTRATIVO_COLABORADOR', 'Consulta as próprias demandas e inclui comentários.', 1, 0
WHERE NOT EXISTS (SELECT 1 FROM auth_perfis WHERE codigo = 'ADMINISTRATIVO_COLABORADOR');

INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT p.id, 'administrativo', 1, 'EDICAO'
FROM auth_perfis p
WHERE p.codigo = 'ADMINISTRATIVO_GESTOR'
ON DUPLICATE KEY UPDATE permitido=1, nivel_acesso='EDICAO';

INSERT INTO auth_perfil_permissoes (perfil_id, menu_key, permitido, nivel_acesso)
SELECT p.id, 'administrativo', 1, 'LEITURA'
FROM auth_perfis p
WHERE p.codigo = 'ADMINISTRATIVO_COLABORADOR'
ON DUPLICATE KEY UPDATE permitido=1, nivel_acesso='LEITURA';
