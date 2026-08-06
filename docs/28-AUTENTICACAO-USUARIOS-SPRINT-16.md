# Plano de Autenticacao e Gestao de Usuarios - Sprint 16

Versao: 3.0 Alpha

Data: 03/08/2026

Status: Implementado para validacao assistida

---

# Objetivo

Criar em Configuracoes uma area de gerenciamento de usuarios e autenticacao, permitindo usuarios locais convidados por e-mail e integracao com provedores corporativos como FreeIPA, LDAP e Active Directory.

---

# Local no Sistema

Menu previsto:

- Configuracoes
- Usuarios e Acessos

A tela deve centralizar:

- Usuarios do sistema.
- Perfis e permissoes.
- Convites pendentes.
- Origem de autenticacao de cada usuario.
- Configuracoes de provedores externos.
- Testes de comunicacao e autenticacao.

---

# Modos de Autenticacao

## 1. Usuario Local com Convite por E-mail

Objetivo:

Permitir cadastrar manualmente um usuario e enviar convite por e-mail para que ele defina a propria senha de acesso.

Regras:

- Administrador informa nome, e-mail, perfil inicial e status.
- Sistema gera token de convite com expiracao.
- E-mail de convite usa o servico SMTP configurado em Configuracoes.
- Usuario acessa link do convite e cadastra senha propria.
- Senha deve ser armazenada apenas com hash seguro.
- Convite expirado deve permitir reenvio pelo administrador.
- Usuario local pode ser bloqueado/desativado sem exclusao fisica.

## 2. FreeIPA

Objetivo:

Permitir sincronizar usuarios do FreeIPA quando existir integracao tecnica configurada.

Regras:

- FreeIPA deve aparecer como opcao quando houver configuracao ativa.
- Sincronismo deve importar usuarios e grupos permitidos.
- Grupos FreeIPA devem ser mapeados para perfis internos do O3Cloud Manager.
- Sincronismo nao deve importar senhas.
- Login deve validar credenciais contra o provedor, quando o modo de autenticacao do usuario for FreeIPA.
- Falhas de sincronismo devem ser auditadas sem expor segredo.

## 3. LDAP Generico

Objetivo:

Permitir configurar um servidor LDAP generico e testar comunicacao antes de ativar autenticacao.

Campos previstos:

- Nome da configuracao.
- Host.
- Porta.
- Uso de TLS/StartTLS.
- Base DN.
- Bind DN.
- Senha do bind mascarada.
- Filtro de usuarios.
- Filtro de grupos.
- Atributo de login.
- Atributo de e-mail.
- Atributo de nome.

Acoes previstas:

- Salvar configuracao.
- Testar comunicacao.
- Testar busca de usuario.
- Testar autenticacao com usuario informado.
- Ativar/desativar configuracao.

## 4. Active Directory

Objetivo:

Permitir cadastrar servidor Active Directory, validar comunicacao e validar autenticacao de usuarios.

Campos previstos:

- Nome da configuracao.
- Dominio.
- Host ou controlador de dominio.
- Porta.
- TLS/LDAPS.
- Base DN.
- Usuario de bind ou conta de servico.
- Senha da conta de servico mascarada.
- UPN suffix.
- Filtro de usuarios.
- Filtro de grupos.

Acoes previstas:

- Salvar configuracao.
- Testar comunicacao com o controlador de dominio.
- Validar autenticacao de usuario.
- Sincronizar usuarios/grupos permitidos.
- Mapear grupos AD para perfis internos.

---

# Gestao de Usuarios

Campos principais:

- Nome.
- E-mail.
- Login.
- Origem: Local, FreeIPA, LDAP ou Active Directory.
- Perfil principal.
- Perfis adicionais, quando aplicavel.
- Status: convidado, ativo, bloqueado, inativo.
- Ultimo login.
- Data de criacao.
- Data de ultima sincronizacao externa.

Acoes principais:

- Novo usuario local.
- Enviar convite.
- Reenviar convite.
- Bloquear usuario.
- Reativar usuario.
- Alterar perfil.
- Sincronizar usuarios externos.
- Testar autenticacao externa.

---

# Regras de Seguranca

- Senhas locais nunca devem ser armazenadas em texto puro.
- Senhas de bind LDAP/AD/FreeIPA devem permanecer mascaradas na interface.
- Tokens de convite devem ter expiracao e uso unico.
- Toda acao administrativa sensivel deve ser auditada.
- Logs nao devem registrar senhas, tokens, CPF, chaves ou segredos.
- Telas de Usuarios e Acessos devem ser acessiveis apenas a administradores.
- O primeiro administrador deve ser criado por bootstrap controlado ou migration/seed segura.

---

# Modelo de Dados Candidato

Tabelas candidatas:

- `auth_usuarios`
- `auth_perfis`
- `auth_permissoes`
- `auth_usuario_perfis`
- `auth_convites`
- `auth_provedores`
- `auth_grupo_perfil_mapas`
- `auth_auditoria`

Observacao:

O desenho definitivo deve ser validado antes da migration para evitar conflito com futuras integracoes FreeIPA/LDAP/AD.

---

# Implementacao Inicial

Status: implementada para validacao assistida em 06/08/2026

Entregas realizadas:

- Criada migration `database/migrations/050_create_auth_usuarios_acessos.sql`.
- Criadas tabelas candidatas para perfis, usuarios, convites, provedores e auditoria.
- Criada tela `Configuracoes > Usuarios e Acessos`.
- Permitido cadastrar e editar usuarios com origem Local, FreeIPA, LDAP ou Active Directory.
- Permitido reenviar convite para usuario local.
- Criada tela de aceite de convite para cadastro de senha.
- Permitido cadastrar provedores FreeIPA, LDAP e Active Directory.
- Permitido testar comunicacao de provedor e, quando `ldap3` estiver disponivel, validar autenticacao LDAP/AD.
- Senhas de bind e senhas locais ficam protegidas por criptografia/hash, sem exibicao em texto puro.
- Acoes administrativas registram auditoria basica.
- Criada migration `database/migrations/060_create_auth_grupo_perfil_mapas.sql`.
- Criada tela administrativa de mapeamento de grupos externos para perfis internos em Usuarios e Acessos.
- Criada tela de login global em `app/autenticacao`.
- Implementada protecao gradual de rotas por sessao e permissao.
- Criada matriz de permissoes por menu em `auth_perfil_permissoes`.
- Adicionado nivel de acesso por permissao: visualizacao ou edicao.
- Adicionado controle `mostrar_valores` por perfil.
- Adicionada foto de usuario.
- Expandida auditoria com IP de origem, user agent e sanitizacao de detalhes sensiveis.

Pendencias da proxima etapa:

- Implementar sincronismo real de usuarios e grupos por FreeIPA/LDAP/AD.
- Validar matriz de permissoes por perfil com a equipe.
- Validar comportamento de visualizacao/edicao em rotas sensiveis.

---

# Criterios de Aceite

- Configuracoes deve exibir Usuarios e Acessos.
- Administrador deve poder cadastrar usuario local e enviar convite por e-mail.
- Usuario convidado deve conseguir definir senha propria por link valido.
- FreeIPA deve permitir sincronismo apenas quando houver integracao ativa configurada.
- LDAP deve permitir cadastrar configuracao e testar comunicacao.
- Active Directory deve permitir cadastrar servidor e validar autenticacao.
- Provedores externos permitem mapeamento administrativo de grupos para perfis internos.
- Acoes administrativas devem gerar auditoria.
- Segredos devem permanecer mascarados e fora dos logs.
- Rotas protegidas devem exigir sessao autenticada.
- Perfis sem edicao devem conseguir visualizar apenas quando a permissao permitir.

---

# Encaminhamento Tecnico

Fases atendidas para validacao assistida:

1. Base local de usuarios, perfis, permissoes e auditoria.
2. Convite por e-mail e cadastro de senha.
3. Tela de provedores externos com LDAP/AD configuravel e teste de comunicacao.
4. Bootstrap seguro do primeiro administrador.
5. Login global e protecao gradual das rotas sensiveis por permissao.

Fases pendentes de ambiente externo homologado:

- Sincronismo real de usuarios e grupos por FreeIPA/LDAP/AD.
- Revisao da matriz de permissoes por perfil com a equipe.
