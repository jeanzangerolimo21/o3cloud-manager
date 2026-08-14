# Checklist de Fechamento Sprint 17

Data: 14/08/2026

Status: Concluido tecnicamente em 14/08/2026

## Objetivo

Consolidar o que falta para encerrar o Sprint 17 e liberar a entrada no Sprint Final de homologacao da versao Beta.

## Estado atual

O Sprint 17 ja possui as entregas principais implementadas:

- Comissoes e Premiacoes com base em contratos, campanhas, recebimentos OMIE e primeiro titulo/parcela ativo.
- Regras Campanhas reaproveitadas para exibir contratos elegiveis por vigencia.
- Recebimentos OMIE em cache local e sincronismo dedicado `OMIE_RECEBIMENTOS`.
- Expansao de contratos OMIE com vendedor, projeto, observacao e valores comerciais.
- Administrativo ASO com colaborador, agendamento, lembretes e anexos de exames.
- Receita por Servidor no Financeiro com base em Proxmox, ambientes e contratos ativos.
- 2FA por e-mail e TOTP para autenticacao remota.
- Remocao dos alertas antigos da Visao Geral e Dashboard Executivo.
- Correcao da Etapa 7 de permissoes para perfis somente leitura em Clientes e Contatos, ocultando acoes indevidas e evitando loop de redirecionamento em acesso negado.
- Alertas operacionais por e-mail para usuarios selecionados, consolidando Zabbix critico, PBS fora do prazo e TrueNAS sem modificacao ha mais de 5 dias.

## Conferencias operacionais antes do Sprint Final

1. Banco de dados

- Confirmado em 14/08/2026 que nao existem CPFs duplicados em `administrativo_aso_colaboradores`.
- Aplicada e registrada `database/migrations/096_unique_administrativo_aso_colaboradores_cpf.sql`.
- Confirmada como aplicada e registrada `database/migrations/097_auth_2fa_email.sql`.
- Aplicada/conferida e registrada `database/migrations/098_auth_usuarios_alertas_operacao.sql`.
- Aplicada e registrada `database/migrations/099_permissao_administrativo_aso.sql`.

2. Validacao funcional assistida

Status: concluida pelo usuario em 14/08/2026 nas 8 etapas solicitadas.

Itens validados:

- Login normal sem 2FA, 2FA por e-mail, TOTP e dispositivo confiavel.
- Fluxos de ASO, agendamentos, compartilhamento e lembretes.
- Premiações, regra de primeiro titulo/parcela ativo e receitas por servidor.
- Remocao dos alertas antigos em Visao Geral e Dashboard Executivo.
- Alertas operacionais por usuario e comando de envio.
- Permissoes dos perfis, incluindo o perfil Infraestrutura para Retencao de Cache, Automacoes de Sincronismo e Backups do Sistema.

3. Revisao de permissao e perfis

- Perfil Operacao com permissao de leitura em Clientes e Contatos validado.
- Acesso a `comissoes` e `receitas_servidor` validado para perfis autorizados.
- Configuracao administrativa de 2FA/TOTP mantida restrita a Administrador.
- Exclusao de Executivo mantida para Administrador e Diretoria.
- Exclusao de agendamento ASO mantida para Administrador e Gestor Administrativo.
- Perfil Infraestrutura validado para `cache_sistema`, `sincronismos_agendados` e `backups_sistema`, removendo bloqueio redundante por ADMIN nas rotas.

4. Qualidade tecnica

- `venv/bin/python -B -m py_compile` executado nos arquivos Python alterados em 14/08/2026 sem erro.
- `venv/bin/python -B -m pytest` executado em 14/08/2026 com `34 passed`.
- Revisar `git diff` para garantir que so existem alteracoes esperadas.
- Conferir que nao ha arquivos temporarios ou artefatos locais no Git.

## Validacao ja executada

Em 14/08/2026:

```text
venv/bin/python -B -m pytest
34 passed
```

Tambem foi executada compilacao Python nos arquivos alterados de autenticacao, configuracoes, financeiro, dashboards, controle de acesso e rotas de Contatos sem erro de sintaxe. O e-mail de 2FA foi ajustado para enviar corpo HTML com codigo em destaque, mantendo texto simples como fallback. As templates alteradas de Clientes e Contatos foram parseadas com Jinja sem erro.

## Documentacao finalizada em 14/08/2026

- `docs/05-SPRINT_ATUAL` atualizado para Sprint 17 concluido tecnicamente.
- `docs/17-SPRINTS.md` atualizado com a conclusao tecnica do Sprint 17.
- `docs/CHANGELOG.md` atualizado com a entrada final de fechamento.
- `docs/00-VISAO-GERAL.md` e `docs/ROADMAP.md` atualizados para indicar Sprint 17 encerrado e Sprint Final como proximo.

## Criterio para entrar no Sprint Final

O Sprint Final pode iniciar quando:

- workspace estiver revisado e pronto para commit/tag da versao Beta.

Ja concluido em 14/08/2026 para banco local/alvo:

- migrations `096`, `097`, `098` e `099` aplicadas/conferidas e registradas em `schema_migrations`;
- CPFs duplicados em ASO conferidos antes da migration `096`;
- constraint unica `uk_adm_aso_colab_cpf` confirmada.

Ja concluido em 14/08/2026:

- validacao funcional assistida dos fluxos criticos;
- testes automatizados com `34 passed`;
- documentacao de fechamento do Sprint 17 atualizada.

## Sprint Final - foco proposto

O Sprint Final deve ser exclusivamente de homologacao e fechamento da versao:

1. congelar escopo funcional;
2. aplicar migrations pendentes no ambiente Beta;
3. gerar backup completo antes da homologacao;
4. validar usuarios, perfis, SMTP, 2FA e TOTP;
5. validar fluxos financeiros, comerciais, administrativos e infraestrutura com dados reais controlados;
6. registrar evidencias e aceite;
7. fechar changelog da versao;
8. criar branch/tag/release Beta final;
9. executar healthcheck e plano de rollback;
10. preparar transicao para versao oficial.
