# Acompanhamento Sprint 17 - 13/08/2026

## Objetivo

Registrar as etapas realizadas em 13/08/2026 e separar o que ja foi consolidado no `develop` do que permanece em andamento no workspace para continuidade do Sprint 17.

## Base consultada

- Commit `a06604b47d7666f93ffc29b64b8ea1e002e40fe1` em `develop`.
- `docs/CHANGELOG.md`.
- `docs/05-SPRINT_ATUAL`.
- `docs/17-SPRINTS.md`.
- Estado local do workspace em 14/08/2026.

## Entrega consolidada em 13/08/2026

Commit:

```text
a06604b Implementa ASO, premiacoes e receitas por servidor
```

Escopo principal entregue:

1. ASO administrativo

- Criado modulo operacional de ASO em `Administrativo > Agendamento ASO`.
- Cadastro de colaborador passou a permitir criacao de agendamento ASO no mesmo fluxo.
- Agendamento ASO passou a integrar a agenda do Gestor Administrativo.
- Adicionado compartilhamento de agendamento com outro usuario que possua agenda habilitada.
- Lembretes por e-mail passaram a aceitar antecedencia de 7, 15 ou 30 dias.
- Campo `Exames realizados` passou a aceitar anexos multiplos com exibicao dos nomes selecionados.

2. Premiacoes

- Parceiros receberam flag `premiacao_ativa`.
- Executivos ja podem ter status de premiacao alterado rapidamente pela listagem.
- Tela `Financeiro > Premiações` passou a listar somente contratos com Parceiro ou Executivo habilitado para premiacao.
- Calculo passou a considerar Parceiro, Executivo ou ambos conforme regra de campanha.
- Premiacoes passaram a considerar somente o primeiro titulo/parcela ativo do contrato.
- Executivos podem ser removidos operacionalmente por Administrador e Diretoria, com inativacao e retirada do vinculo com parceiro, preservando historico financeiro.

3. Receita por Servidor

- Criada tela `Financeiro > Receitas por Servidor`.
- Adicionada permissao/menu `receitas_servidor`.
- Receita recorrente mensal passou a ser calculada por node Proxmox sincronizado.
- Calculo cruza node, recurso Proxmox, ambiente ativo e contrato ativo vinculado.
- Cada contrato e contado uma unica vez por node para evitar duplicidade quando houver varias VMs/containers.

4. Implantacao e Kanban

- Listagem de Implantacoes passou a exibir CNPJ do cliente.
- Cards do Kanban de Implantacao passaram a exibir CNPJ do cliente.

5. Restricoes operacionais

- Cadastro e edicao de Parceiros passaram a ocultar `Importar de Cliente` para perfis nao Administrador.

6. Banco de dados e automacoes

- Migrations consolidadas no commit:
  - `092_add_premiacao_ativa_executivos.sql`
  - `093_create_administrativo_aso.sql`
  - `094_add_enviar_email_aso_lembretes.sql`
  - `095_add_premiacao_ativa_parceiros.sql`
- Cron operacional recebeu processamento de lembretes ASO.

## Documentacao atualizada em 13/08/2026

- `docs/00-VISAO-GERAL.md` passou a registrar a atualizacao operacional de 13/08/2026.
- `docs/05-SPRINT_ATUAL` passou a descrever Sprint 17 como `Comissoes, Premiacoes, ASO e Receita por Servidor`.
- `docs/06-MODELO-DE-PERMISSOES.md` recebeu a permissao `receitas_servidor`.
- `docs/12-DER.md` e `docs/13-MODELO-FISICO-DADOS.md` receberam estruturas de ASO, recebimentos e premiacoes.
- `docs/17-SPRINTS.md` recebeu a atualizacao de 13/08/2026.
- `docs/CHANGELOG.md` recebeu a entrada `2026-08-13 - Ajustes Operacionais ASO, Premiações e Receita por Servidor`.

## Frente em andamento no workspace em 14/08/2026

Alteracoes ainda nao consolidadas em commit:

- 2FA por e-mail no login.
- Tela `autenticacao/2fa_email.html`.
- Campos `exigir_2fa` e `two_factor_metodo` em usuarios.
- Tabelas `auth_2fa_codigos` e `auth_dispositivos_confiaveis`.
- Dispositivo confiavel por 30 dias.
- Auditoria de senha validada, envio de codigo, sucesso/falha de 2FA e login concluido.
- CPF unico para colaboradores ASO.
- Exclusao de colaborador ASO com remocao de exames e cancelamento de demandas vinculadas.
- Ajuste de permissao para exclusao de agendamentos ASO limitado a Administrador e Gestor Administrativo.
- Migrations pendentes:
  - `096_unique_administrativo_aso_colaboradores_cpf.sql`
  - `097_auth_2fa_email.sql`

## Validacao 2FA por e-mail - 14/08/2026

A frente de 2FA por e-mail foi revisada tecnicamente e considerada adequada como primeira etapa de duplo fator para usuarios locais.

Pontos confirmados:

- fluxo de login valida senha antes de iniciar o desafio 2FA;
- codigo numerico possui expiracao de 10 minutos;
- codigo e armazenado apenas como hash;
- desafios anteriores sao expirados ao reenviar novo codigo;
- validacao usa comparacao segura por `hmac.compare_digest`;
- limite de tentativas bloqueia o desafio apos 5 tentativas;
- login so e concluido depois da validacao do codigo;
- dispositivo confiavel usa token aleatorio, armazenado somente como hash, com expiracao de 30 dias;
- eventos de senha validada, codigo enviado, falha, bloqueio e sucesso sao auditados;
- recurso depende de SMTP configurado em `Configuracoes > Servicos de Email` ou variaveis SMTP do ambiente.

Testes adicionados:

- `tests/test_auth_2fa_email_service.py`

Validacao executada:

```text
venv/bin/python -B -m pytest tests/test_auth_2fa_email_service.py tests/test_backup_service.py tests/test_atualizacao_service.py
19 passed
```

Status: aprovado para homologacao assistida apos aplicacao da migration `097_auth_2fa_email.sql` no banco alvo.

## TOTP para autenticacao remota - 14/08/2026

TOTP foi implementado como segunda etapa de duplo fator para usuarios locais, especialmente para acessos remotos e perfis administrativos.

Pontos entregues:

- metodo `TOTP` suportado em `two_factor_metodo`;
- geracao de segredo TOTP individual por usuario;
- URI `otpauth://` e chave manual exibidas durante a configuracao;
- primeiro codigo precisa ser validado antes de gravar `two_factor_configurado_em`;
- segredo TOTP e protegido usando o mesmo mecanismo de criptografia do Cofre de Senhas;
- login `/login/2fa` escolhe validacao por EMAIL ou TOTP conforme metodo do usuario;
- reenvio de codigo fica disponivel apenas para metodo EMAIL;
- usuario pode configurar e desativar TOTP em `Minha Conta`;
- administrador nao consegue marcar TOTP para usuario que ainda nao concluiu a configuracao;
- dispositivo confiavel de 30 dias continua funcionando para EMAIL e TOTP.

Testes adicionados ou ampliados:

- `tests/test_auth_2fa_email_service.py`

Validacao executada:

```text
venv/bin/python -B -m pytest tests/test_auth_2fa_email_service.py tests/test_backup_service.py tests/test_atualizacao_service.py
23 passed
```

Status: aprovado para homologacao assistida apos aplicacao da migration `097_auth_2fa_email.sql` no banco alvo.

## Pendencias para finalizacao do Sprint 17

1. Validar fluxo completo de Comissoes e Premiacoes com dados reais controlados.
2. Confirmar regra final de pagamento/premiacao com Comercial e Financeiro.
3. Validar `Financeiro > Receitas por Servidor` contra contratos ativos e ambientes Proxmox reais.
4. Validar ASO com Gestor Administrativo, usuarios com agenda e envio SMTP.
5. Aplicar e validar migrations pendentes `096` e `097` no banco alvo, com atencao a CPFs duplicados antes da constraint unica.
6. Atualizar DER, modelo fisico, permissoes e changelog apos consolidar a frente em andamento.
7. Executar checklist de homologacao e registrar evidencias.

## Proximo passo recomendado

Antes de fechar o Sprint 17, concluir a revisao das alteracoes pendentes do workspace e rodar uma validacao funcional minima:

- login normal, login com 2FA por e-mail e login com TOTP;
- criacao/edicao/exclusao de colaborador ASO;
- criacao de agendamento ASO e lembrete por e-mail;
- listagem de premiacoes por contrato;
- receitas por servidor;
- permissoes dos menus Financeiro, Administrativo e Configuracoes.
