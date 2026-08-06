# Entregas de Governanca e Integracoes - Sprint 16

Versao: 3.0 Alpha

Data: 06/08/2026

Status: Implementado para validacao assistida

---

# Objetivo

Registrar o segundo pacote de entregas da Sprint 16, implementado em 05/08/2026, com foco em governanca de acesso, auditoria operacional, CRM comercial, cofre de senhas, integracoes de e-mail e catalogo tecnico por parceiro.

---

# Governanca de Acesso

## Funcionalidades

- Tela de login global criada no modulo `autenticacao`.
- Controle de sessao aplicado antes das rotas protegidas.
- Permissoes por menu vinculadas a perfis internos.
- Nivel de acesso por permissao: visualizacao ou edicao.
- Controle `mostrar_valores` por perfil para ocultar valores comerciais/financeiros quando aplicavel.
- Perfis administrativos podem configurar acessos por area operacional.
- Primeiro administrador mantido por bootstrap seguro, sem senha em migration.
- Usuario pode possuir foto de perfil.

## Regras

- Endpoints publicos ficam limitados a login, logout, arquivos estaticos, aceite de convite e compartilhamento publico do cofre.
- Rotas sem sessao redirecionam para login.
- Acoes de escrita exigem permissao de edicao quando o endpoint mapeado for protegido.
- Acesso negado em GET redireciona com aviso; demais metodos retornam 403.

## Migrations

- `database/migrations/051_expandir_auth_perfis_permissoes.sql`
- `database/migrations/052_permitir_email_opcional_usuario_externo.sql`
- `database/migrations/053_adicionar_nivel_acesso_permissoes.sql`
- `database/migrations/057_adicionar_foto_usuario.sql`

## Arquivos principais

- `app/autenticacao/`
- `app/core/access_control.py`
- `app/configuracoes/auth_service.py`
- `app/repositories/auth_repository.py`
- `app/templates/autenticacao/`
- `app/templates/configuracoes/usuarios/`

---

# Auditoria Operacional

## Funcionalidades

- Registro centralizado de eventos sensiveis em `auth_auditoria`.
- Captura de usuario, acao, entidade, identificador, detalhes, IP de origem e user agent.
- Sanitizacao de detalhes antes da persistencia.
- Tela administrativa de auditoria em Configuracoes.
- Indices para consulta por usuario, entidade e data.
- Retencao inicial limitada pela migration para eventos antigos acima de 30 dias.

## Dados Sensiveis

Os detalhes de auditoria mascaram chaves como:

- senha
- password
- token
- segredo
- secret
- app_key
- app_secret
- access_token
- bind_password
- chave_ativacao
- cpf
- cnpj

## Migration

- `database/migrations/054_expandir_auth_auditoria_login.sql`

## Arquivos principais

- `app/core/auditoria.py`
- `app/templates/configuracoes/auditoria/`

---

# Propostas - Comentarios Internos

## Funcionalidades

- Comentarios internos vinculados a proposta.
- Autor registrado por e-mail.
- Compartilhamento do comentario por lista de e-mails.
- Comentarios podem ser desativados sem remocao fisica do historico principal.
- Atalho de comentarios internos incluido na visualizacao da proposta.

## Migrations

- `database/migrations/055_create_proposta_comentarios_internos.sql`
- `database/migrations/056_trocar_compartilhamento_comentario_proposta_para_email.sql`

## Arquivos principais

- `app/propostas/routes.py`
- `app/propostas/service.py`
- `app/repositories/proposta_repository.py`
- `app/templates/propostas/comentarios_internos.html`

---

# Regras de Campanhas e Comissao

## Funcionalidades

- Cadastro de regras de campanha comercial.
- Percentual separado para parceiro e executivo.
- Vigencia com data inicial e final.
- Validacao contra sobreposicao de vigencias ativas.
- Inativacao logica de regras.
- Auditoria em criacao, alteracao e exclusao logica.

## Migration

- `database/migrations/059_create_regras_campanhas_comissao.sql`

## Arquivos principais

- `app/regras_campanhas/routes.py`
- `app/regras_campanhas/service.py`
- `app/repositories/regra_campanha_repository.py`
- `app/templates/regras_campanhas/`

---

# Cofre de Senhas

## Funcionalidades

- Compartilhamento publico temporario por token.
- Token persistido apenas como hash.
- Controle de expiracao, primeiro acesso, revogacao e IP.
- Tela publica de acesso ao compartilhamento.
- Tela de link expirado/revogado.
- Vinculo opcional de senha com inventarios Proxmox, PBS e Zabbix.
- Listagem de hosts Zabbix sincronizados para associacao operacional.

## Migration

- `database/migrations/061_create_cofre_compartilhamentos.sql`
- `database/migrations/062_cofre_vinculos_inventarios_zabbix.sql`

## Arquivos principais

- `app/implantacao/cofre_senhas_service.py`
- `app/repositories/cofre_senha_repository.py`
- `app/repositories/zabbix_host_repository.py`
- `app/templates/implantacao/cofre_senhas/compartilhamento.html`
- `app/templates/implantacao/cofre_senhas/compartilhamento_expirado.html`

---

# Eventos CRM - Disparos por E-mail

## Funcionalidades

- Eventos CRM passam a permitir disparo de e-mail para participantes.
- Registro de disparos com status, totais, erro, anexo e configuracao usada.
- Suporte a anexo no disparo.
- Integracao com servico de e-mail ativo.

## Migration

- `database/migrations/066_create_crm_evento_disparos_email.sql`

## Arquivos principais

- `app/leads/evento_routes.py`
- `app/repositories/evento_email_repository.py`

---

# Servicos de E-mail - Brevo

## Funcionalidades

- Configuracao de servico de e-mail por provedor: SMTP ou Brevo.
- Campos especificos para Brevo: remetente, nome, reply-to, limite diario, ambiente, URL da API e chave criptografada.
- Envio via API Brevo com suporte a HTML e anexo.
- Teste de configuracao preservado na area Configuracoes > Servicos de Email.

## Migration

- `database/migrations/065_adicionar_brevo_servicos_email.sql`

## Arquivos principais

- `app/integracoes/brevo_service.py`
- `app/configuracoes/email_service.py`
- `app/repositories/email_config_repository.py`
- `app/templates/configuracoes/email/`

---

# Parceiros e Dimensionamento Tecnico

## Funcionalidades

- Parceiros passam a ter categoria: Platinium, Ouro, Prata ou Bronze.
- Categoria pode ser exibida nas listagens e detalhes do parceiro.
- Catalogo tecnico passa a ter tabela de hardware por parceiro.
- Importacao CSV de dimensionamento de hardware por parceiro.
- Normalizacao de titulos de tabelas Base44 para nomes de parceiros.

## Migrations

- `database/migrations/058_adicionar_categoria_parceiro.sql`
- `database/migrations/067_create_hardware_parceiros.sql`

## Arquivos principais

- `app/catalogo/hardware_parceiros_service.py`
- `app/repositories/hardware_parceiros_repository.py`
- `app/templates/catalogo/servidores/hardware_form.html`
- `app/templates/parceiros/_categoria_badge.html`

---

# Validacao Pendente

Este pacote ainda deve passar pela validacao assistida da Beta antes de fechamento final da Sprint 16:

- Aplicar migrations 051 a 067 em ambiente homologado.
- Revisar matriz de permissoes por perfil com a equipe.
- Validar login, bloqueio de rotas e fluxo de convite.
- Validar exibicao/ocultacao de valores por perfil.
- Validar auditoria sem exposicao de segredos.
- Validar disparos Brevo com chave real e limite operacional.
- Validar compartilhamento temporario do cofre com dados reais controlados.
- Validar importacao de hardware por parceiro com planilha oficial.
