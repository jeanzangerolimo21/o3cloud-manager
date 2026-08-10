# O3Cloud Manager v3.0

# 17 - SPRINTS

Versão: 3.0 Alpha

Última atualização: 06/08/2026

Status: Oficial

---

# Visão Geral

Este documento consolida a evolução das Sprints do projeto.

A referência oficial de planejamento continua sendo o `ROADMAP.md`.

---

# Sprints Concluídas

## Sprint 1

Entregas:

- Estrutura inicial do projeto
- Flask
- MariaDB
- Layout Base

Status:

✅ Concluído

---

## Sprint 2

Entregas:

- Módulo Ambientes
- CRUD completo
- Repository
- Service
- Routes
- Templates

Status:

✅ Concluído

---

## Sprint 3

Entregas:

- Estrutura administrativa
- Evolução da arquitetura
- Organização inicial dos domínios

Status:

✅ Concluído

---

## Sprint 4

Entregas:

- Módulo Clientes
- CRUD
- Integração OMIE
- Sincronização
- Bloqueios de edição
- Implantação

Status:

✅ Concluído

---

## Sprint 5

Entregas:

- Módulo Contratos
- CRUD
- Integração OMIE
- Contratos
- Itens de Contrato

Status:

✅ Concluído

---

## Sprint 6.1

Entregas:

- Fundação do Catálogo Técnico
- Estrutura inicial do módulo

Status:

✅ Concluído

---

## Sprint 6.2

Entregas:

- Estrutura do Catálogo Técnico
- Organização da base do módulo

Status:

✅ Concluído

---

## Sprint 6.3

Entregas:

- CRUD Categorias
- CRUD Produtos
- Repository padronizado
- Service padronizado
- Routes padronizadas
- Templates padronizados
- Componentes homologados
- BaseRepository atualizado

Status:

✅ Concluído

---

## Sprint 6.4

Entregas:

- CRUD Modelos
- CRUD Faixas
- Home do Catálogo Comercial ajustada
- Atalhos de acesso para Modelos e Faixas
- Contabilização de Categorias, Modelos e Faixas na visão geral
- Documentação da sprint atualizada

Status:

✅ Concluído

---

# Última Sprint Concluída

## Sprint 8

Objetivos:

- Consolidação comercial pós-assinatura
- Dashboard executivo/comercial
- Indicadores por parceiro e executivo
- Rastreabilidade proposta -> ClickSign -> contrato -> Omie
- Evolução de permissões e auditoria

Entregas:

- Dashboard Comercial inicial em `/propostas/dashboard`
- Agrupamentos por executivo, parceiro, status comercial e status ClickSign
- Atalhos no menu lateral e na tela de Propostas

Status:

✅ Concluída na primeira entrega

---

# Última Sprint Concluída

## Sprint 9

Implantação e Provisionamento

Objetivos:

- Módulo próprio de Implantação
- Workflow pós-contrato assinado
- Checklist técnico rastreável
- Acompanhamento por status, responsável e prazo
- Preparação de provisionamento
- Base para integração Proxmox, PBS e Zabbix segura e auditável

Escopo entregue:

- ✅ Fundação do domínio `implantacao` com migrations, repository, service, routes e templates
- ✅ Listagem, criação, visualização, edição e dashboard de implantações
- ✅ Kanban operacional com movimentação, histórico e notificação tolerante a SMTP ausente
- ✅ Administração de colunas do Kanban
- ✅ Checklist técnico rastreável com modelos, inclusão e remoção manual de itens
- ✅ Licenças O3Web, Faixas de Rede e Cofre de Senhas como telas operacionais da Implantação
- ✅ Cofre com senha criptografada, auditoria e navegação por parceiro -> cliente -> credenciais
- ✅ Rastreabilidade proposta -> contrato -> implantação nas telas operacionais
- ✅ Base de configuração para integrações Proxmox, PBS e Zabbix sem automação destrutiva

Documento de fechamento:

- `docs/19-FECHAMENTO-SPRINT-9.md`

Status:

✅ Concluída em 27/07/2026

---

# Última Sprint Concluída

## Sprint 10

Dashboard Executivo

Objetivos:

- Indicadores executivos
- Visão comercial e contratos
- Acompanhamento de implantação
- Base para rentabilidade e custos
- Drill-down para telas operacionais existentes

Escopo entregue:

- ✅ Dashboard Executivo dedicado em `/dashboard/executivo`
- ✅ Filtros executivos por periodo, parceiro, executivo e status
- ✅ Drill-down filtrado para Propostas, Contratos e Implantacao
- ✅ Evolucao mensal de propostas, receita ativa e volume operacional
- ✅ Base inicial para rentabilidade e custos, sem calculo definitivo de margem
- ✅ Carga por responsavel/implantador
- ✅ Rastreabilidade executiva proposta -> contrato -> implantacao

Documento de fechamento:

- `docs/20-FECHAMENTO-SPRINT-10.md`

Status:

✅ Concluída em 28/07/2026

---

# Ultima Sprint Encerrada

## Sprint 11

Integracoes e Melhorias Operacionais

Entregas:

- Menu Financeiro criado no sidebar com Dashboard Executivo, Produtos por Cliente, Faturamento e Contratos
- Tela `/dashboard/produtos-clientes` criada para diagnostico cliente -> contrato -> item contratado
- Vinculos Omie de maior impacto cadastrados no catalogo por seed idempotente
- Tela `/catalogo/produtos/custos` criada para exportar/importar custos por CSV
- Tela `/financeiro/faturamentos` criada para exportar modelo e importar faturamentos por competencia
- Pendencias de custos, faturamentos, parametros financeiros e rastreabilidade historica documentadas

Documento de fechamento:

- `docs/21-FECHAMENTO-SPRINT-11.md`

Status:

⚠️ Parcialmente concluida em 29/07/2026

---

## Sprint 12

Pendencias Operacionais e Preparacao da Versao Final

Entregas:

- `proposta_id` definido como vinculo opcional no fluxo operacional
- Contratos diretos/parceiros definidos como origem valida para implantacao
- Dashboard Executivo ajustado para exibir contratos sem proposta como contratos diretos
- Integracoes separadas em Negocio e Tecnicas
- OMIE e ClickSign exibidos a partir de variaveis de ambiente com segredos mascarados
- Comentarios de implantacao passaram a aceitar anexos

Documento de fechamento:

- `docs/22-FECHAMENTO-SPRINT-12.md`

Status:

✅ Concluida em 29/07/2026

---

## Sprint 13

Decisao, Preparacao Operacional e Validacoes Nao Destrutivas

Entregas:

- Decidido que dados reais oficiais ficam para a fase Beta com a equipe, sem carga prematura na Sprint 13
- Custos, faturamentos e parametros financeiros nao serao carregados antes do saneamento dos cadastros
- Comercial devera completar informacoes pendentes antes das validacoes oficiais
- Sprint 14 passa a focar consolidacao pre-Beta, diagnosticos, campos/telas pendentes e checklist de validacao

Documento de fechamento:

- `docs/23-FECHAMENTO-SPRINT-13.md`

Status:

✅ Concluida em 29/07/2026

---

# Sprint Encerrada

## Sprint 14

Consolidacao Pre-Beta e Preparacao de Validacao com a Equipe

Entregas consolidadas em 30/07/2026:

- Dashboard Executivo com diagnostico pre-Beta para cadastro comercial, fluxo operacional e dados financeiros
- Checklist inicial de validacao Beta por area: Comercial, Operacoes, Financeiro e Engenharia
- Indicacao explicita de que dados financeiros ausentes aguardam carga oficial da Beta
- Integracoes Tecnicas preparadas para Proxmox, PBS, Zabbix, FreeIPA e TrueNAS em modo diagnostico/nao destrutivo
- Infraestrutura recebeu itens para Backups PBS, Monitoramento Zabbix e Backup NAS
- Cadastros finais e revisao assistida com a equipe foram encaminhados para a fase Beta

Documento de fechamento:

- `docs/24-FECHAMENTO-SPRINT-14.md`

Status:

✅ Concluida em 30/07/2026

---

# Ultima Sprint Encerrada

## Sprint 15

Infraestrutura Operacional e Sincronismo Read-Only

Inicio registrado em 30/07/2026. Encerrada em 03/08/2026.

Entregas consolidadas:

- Sincronismo Proxmox VE em modo somente leitura.
- Telas operacionais de Clusters, Nodes, Maquinas Virtuais e Containers.
- Inventario Proxmox de recursos e nodes com dashboards operacionais.
- Backups PBS com escopos, namespaces, snapshots e sincronismo manual.
- Monitoramento Zabbix com cache, sincronismo manual, ordenacao por criticidade e filtros por status/criticidade.
- Backup NAS/TrueNAS com cache, sincronismo manual, alertas por pasta sem alteracao recente e aba de Backups OK.
- Atalhos para Integracoes Tecnicas removidos das telas operacionais e do menu lateral.
- Seguranca preservada: sem start, stop, reboot, migrate, delete ou alteracoes destrutivas.

Documento de revisao de fechamento:

- `docs/25-FECHAMENTO-SPRINT-15.md`

Pendencias encaminhadas:

- Validacao assistida com a operacao.
- Decisao futura sobre historico centralizado de sincronismos Zabbix/TrueNAS.
- Controle formal de acesso/perfis encaminhado para sprint futura.

Status:

✅ Concluida em 03/08/2026

---

# Melhorias Pre-Sprint 16

Registro:

- `docs/26-MELHORIAS-PRE-SPRINT-16.md`

Entregas consolidadas:

- Selecionar Representante Legal na proposta para ClickSign.
- Exigir nome completo e CPF do Representante Legal antes do envio.
- Bloquear reenvio duplicado para ClickSign quando ja existe envelope.
- Cancelar envelope pendente na ClickSign ao cancelar/rejeitar/expirar proposta.
- Exibir Gerar documento e Enviar na listagem de propostas aprovadas, respeitando status do documento.
- Bloquear nova geracao de documento para fluxo assinado/concluido.
- Refinar PDF, pipeline comercial, cofre de senhas e rastreabilidade operacional.

Status:

✅ Registrado em 03/08/2026 antes da abertura da Sprint 16

---


# Sprints Concluídas

## Sprint 16

Governanca, Acessos e Operacao Assistida

Inicio registrado em 03/08/2026.

Documento de abertura:

- `docs/27-ABERTURA-SPRINT-16.md`
- `docs/28-AUTENTICACAO-USUARIOS-SPRINT-16.md`
- `docs/29-BOOTSTRAP-ADMIN-SPRINT-16.md`
- `docs/30-ENTREGAS-OPERACIONAIS-SPRINT-16.md`
- `docs/31-ENTREGAS-GOVERNANCA-INTEGRACOES-SPRINT-16.md`

Objetivos iniciais:

- Definir controle de acesso e perfis por area operacional.
- Criar Configuracoes > Usuarios e Acessos.
- Prever usuarios locais convidados por e-mail.
- Prever sincronismo FreeIPA, configuracao LDAP e autenticacao Active Directory.
- Mapear telas administrativas e integracoes tecnicas para restricao por permissao.
- Priorizar auditoria operacional para acoes sensiveis.
- Criar roteiro de validacao assistida da Beta por area.
- Enderecar refinamentos operacionais priorizados pela equipe.
- Eventos CRM e importação de participantes implementados.
- Base de Conhecimento com pastas, artigos e arquivos implementada.
- Login global, sessao e matriz de permissoes por menu implementados para validacao assistida.
- Auditoria operacional centralizada implementada com sanitizacao de campos sensiveis.
- Comentarios internos em propostas, regras de campanhas/comissao e compartilhamento temporario do cofre implementados.
- Brevo, disparos de e-mail de eventos CRM e dimensionamento de hardware por parceiro implementados.

Documento de fechamento:

- `docs/33-FECHAMENTO-SPRINT-16.md`

Pendencias de validacao Beta:

- `docs/32-PENDENCIAS-TESTES-BETA-SPRINT-16.md`

Status:

✅ Concluida tecnicamente em 06/08/2026

---

# SPRINT 17
# MÓDULO FINANCEIRO
# COMISSÕES DE EXECUTIVOS

---

## Status

Planejado

---

## Objetivo

Expandir o módulo Financeiro do O3Cloud Manager adicionando o gerenciamento completo de Comissões de Executivos, permitindo parametrização de regras comerciais, cálculo automático das comissões, aprovações gerenciais, integração com contratos e controle financeiro dos pagamentos realizados.

Este módulo deverá permitir o gerenciamento completo do ciclo de comissionamento dos executivos comerciais da O3Cloud.

---

# Escopo

Esta Sprint contempla:

- Dashboard de Comissões
- Cadastro de Parâmetros
- Cadastro de Regras
- Cadastro de Executivos
- Cálculo Automático
- Comissão Recorrente
- Simulador de Comissão
- Aprovação
- Fechamento Mensal
- Pagamentos
- Relatórios
- Auditoria

---

# Arquitetura

Seguir integralmente:

- AGENTS.md
- DOMAIN_RULES.md
- Definition Of Done
- Architecture Freeze

Não alterar arquitetura existente.

Este módulo fará parte do módulo Financeiro.

---

# Banco de Dados

Criar migrations seguindo o padrão do projeto.

Sugestão de tabelas:

financeiro_comissoes

financeiro_comissoes_parametros

financeiro_comissoes_regras

financeiro_comissoes_fechamentos

financeiro_comissoes_pagamentos

financeiro_comissoes_historico

---

# Cadastro de Executivos

Campos

- UUID
- Nome
- Usuário
- Departamento
- Ativo
- Observações

---

# Cadastro de Comissão

Campos

- UUID
- Executivo
- Cliente
- Contrato
- Produto
- Categoria
- Tipo de Serviço
- Valor da Venda
- Percentual Aplicado
- Valor da Comissão
- Competência
- Data da Venda
- Status
- Observações

---

# Status

Pendente

Calculada

Em Aprovação

Aprovada

Paga

Cancelada

Estornada

---

# Cadastro de Regras

O sistema deverá permitir parametrização por:

- Produto
- Categoria
- Serviço
- Fabricante
- Tipo de Contrato
- Tipo de Cliente
- Faixa de Valor
- Campanhas Comerciais

Jamais utilizar percentuais fixos no código.

Todo cálculo deverá utilizar regras cadastradas pelo usuário.

---

# Comissão Recorrente

O sistema deverá permitir:

Pagamento Único

Pagamento Recorrente

Pagamento por Quantidade de Meses

Pagamento Enquanto Contrato Estiver Ativo

Data Inicial

Data Final

Suspensão Automática caso o contrato seja encerrado.

---

# Simulador de Comissão

Antes da venda ser concluída o Executivo poderá simular:

Valor da Venda

Percentual Aplicado

Valor Estimado da Comissão

Comissão Recorrente

Total Acumulado

Margem Comercial (caso permitido pelo perfil)

Esta funcionalidade será utilizada apenas para simulação, não gerando registros financeiros.

---

# Fluxo Operacional

Contrato Comercial

↓

Aprovação Comercial

↓

Integração OMIE

↓

Aplicação da Regra de Comissão

↓

Cálculo Automático

↓

Gestor Comercial Aprova

↓

Financeiro Libera

↓

Pagamento

↓

Histórico

↓

Auditoria

---

# Dashboard de Comissões

Widgets

Comissão do Mês

Valor Pago

Valor Pendente

Total Vendido

Meta Comercial

Percentual Atingido

Ranking dos Executivos

Comissão por Produto

Comissão por Categoria

Comissão por Cliente

Gráfico Evolução Mensal

---

# Dashboard Executivo

Meu Total Vendido

Minha Comissão

Minha Meta

Valor Recebido

Valor Pendente

Ranking

Próximos Pagamentos

---

# Fechamento Mensal

O Gestor poderá:

Fechar Competência

Recalcular Comissão

Cancelar Fechamento

Reabrir Competência

Exportar Relatórios

---

# Relatórios

Comissão por Executivo

Comissão por Cliente

Comissão por Produto

Comissão por Categoria

Comissão por Período

Ranking Comercial

Valores Pagos

Valores Pendentes

Comparativo Mensal

Exportação PDF

Exportação Excel

---

# Integração OMIE

Sempre que possível utilizar os contratos e faturamentos sincronizados com a OMIE para cálculo das comissões.

O cálculo deverá considerar apenas contratos elegíveis conforme regras parametrizadas.

---

# Auditoria

Registrar:

Usuário

Data

Hora

IP

Operação

Competência

Valores Anteriores

Valores Novos

Responsável pela Aprovação

---

# Permissões

Perfis

Administrador

Diretoria

Financeiro

Gestor Comercial

Executivo

Cada perfil deverá utilizar o sistema de permissões do O3Cloud Manager.

---

# Segurança

Executivos visualizarão apenas:

Suas próprias comissões

Suas metas

Seus pagamentos

Jamais visualizarão comissões de outros Executivos.

Gestores visualizarão apenas sua equipe.

Administradores e Diretoria visualizarão todas as informações.

---

# Notificações

Nova Comissão Calculada

Comissão Aprovada

Comissão Rejeitada

Pagamento Efetuado

Competência Fechada

Competência Reaberta

---

# Critérios de Aceite

Cadastro de Regras funcionando.

Cadastro de Executivos funcionando.

Simulador funcionando.

Cálculo automático funcionando.

Comissão recorrente funcionando.

Dashboard funcionando.

Relatórios funcionando.

Permissões funcionando.

Auditoria implementada.

Integração OMIE preservada.

---

# Definition Of Done

Repository

Service

Routes

Templates

Testes

Documentação

Changelog atualizado

Sprint atualizada

Roadmap atualizado

Architecture Freeze preservado.

---

# Observações Técnicas

O módulo deverá ser desenvolvido de forma totalmente parametrizada.

Nenhuma regra de comissão poderá ficar fixa no código.

Todas as regras deverão ser cadastradas através da interface administrativa.

A arquitetura deverá permitir futuras integrações com:

- O3Cloud Infrastructure
- IA Comercial
- BI
- Power BI
- Dashboards Executivos
- Automação via n8n

---

# Melhorias Futuras (V2)

- Comissão por Margem de Lucro
- Comissão por Meta Atingida
- Comissão por Grupo Econômico
- Comissão por Equipe
- Gamificação Comercial
- Ranking em Tempo Real
- IA para previsão de comissão
- IA para projeção de metas
- Integração com Power BI
- Aprovação Digital via Clicksign
- Workflow automatizado via O3Infra

# SPRINT 18
# MÓDULO ADMINISTRATIVO

---

## Status

Concluida tecnicamente em 06/08/2026. Atualizacao final registrada em 07/08/2026.

---

## Atualizacao Final - 07/08/2026

- Remocao de usuarios de acesso restrita a Administradores, com auditoria e protecoes operacionais.
- Logs backend estruturados e documentados para operacao por SSH.
- Validacao de CNPJ unico em Clientes, melhorias de Propostas, pesquisa no Cofre de Senhas, vinculo de ambientes no Cofre/Base de Conhecimento e ajustes de navegacao/template incorporados ao pacote final.
- Validacoes dessas entregas foram adicionadas a `docs/34-PENDENCIAS-TESTES-BETA-SPRINT-18.md`.

---

## Objetivo

Desenvolver o Módulo Administrativo do O3Cloud Manager responsável pelo gerenciamento das atividades internas da empresa, agendas corporativas, demandas administrativas, produtividade dos colaboradores e acompanhamento operacional pelos gestores.

Este módulo deverá centralizar todas as tarefas administrativas internas da empresa, permitindo que gestores distribuam atividades aos colaboradores, acompanhem a execução das demandas e monitorem a produtividade da equipe.

---

# Escopo

Esta Sprint contempla:

- Dashboard Administrativo
- Cadastro de Demandas
- Agenda Corporativa
- Agenda por Colaborador
- Comentários
- Histórico
- Notificações
- Alertas
- Auditoria
- Relatórios

---

# Estrutura do módulo

Administrativo

├── Dashboard

├── Demandas

├── Agenda Corporativa

├── Colaboradores

├── Relatórios

└── Configurações

---

# Arquitetura

Seguir integralmente:

- AGENTS.md
- DOMAIN_RULES.md
- Definition Of Done
- Architecture Freeze

Não alterar arquitetura existente.

---

# Banco de Dados

Criar migrations seguindo padrão do projeto.

Sugestão de entidades:

administrativo_demandas

administrativo_agendas

administrativo_tarefas

administrativo_comentarios

administrativo_historico

---

# Cadastro de Demandas

CRUD Completo

Campos

- UUID
- Título
- Descrição
- Categoria
- Prioridade
- Responsável
- Departamento
- Data Inicial
- Data Limite
- Hora
- Status
- Observações
- Permitir Comentários
- Possui Anexos
- Criado Por
- Data Criação
- Última Alteração

---

# Categorias

Administrativo

Financeiro

Comercial

Implantação

Suporte

Infraestrutura

RH

Diretoria

Outros

---

# Prioridades

Baixa

Normal

Alta

Urgente

---

# Status

Pendente

Em andamento

Concluída

Cancelada

Atrasada

---

# Fluxo

Gestor

↓

Cria Demanda

↓

Seleciona Colaborador

↓

Sistema cria tarefa

↓

Agenda atualizada

↓

Colaborador recebe notificação

↓

Executa atividade

↓

Conclui

↓

Gestor acompanha

---

# Agenda Corporativa

Cada colaborador poderá possuir uma agenda própria.

A agenda somente poderá ser criada por um Gestor.

---

# Cadastro do Colaborador

Adicionar campo:

Possui Agenda

SIM

NÃO

Caso:

NÃO

não exibir menu Agenda.

Caso:

SIM

criar automaticamente agenda vinculada ao usuário.

---

# Visualizações

Hoje

Semana

Mês

Lista

---

# Cada tarefa possuirá

Título

Descrição

Categoria

Prioridade

Status

Responsável

Data

Hora

Comentários

Histórico

Anexos

---

# Comentários

Cada tarefa poderá possuir comentários.

Campos

Usuário

Data

Hora

Comentário

Histórico completo.

---

# Tela do Colaborador

Visualiza apenas:

Sua Agenda

Suas Demandas

Seus Comentários

Seu Histórico

Jamais poderá visualizar agendas de terceiros.

---

# Tela do Gestor

Visualiza:

Agenda Geral

Agenda Individual

Agenda por Departamento

Agenda por Equipe

Agenda por Período

Pode:

Criar

Editar

Excluir

Cancelar

Reagendar

Transferir Responsável

Alterar Prioridade

Concluir

Duplicar

---

# Dashboard Administrativo

Widgets

Demandas Abertas

Demandas Concluídas

Demandas Atrasadas

Demandas Urgentes

Agenda Hoje

Agenda Semana

Pendências

Produtividade

Tempo Médio

Ranking Colaboradores

---

# Dashboard Colaborador

Minha Agenda

Próximas Atividades

Pendências

Comentários Recentes

Concluídas Hoje

---

# Alertas

Sempre que o colaborador realizar login.

Verificar:

Existem tarefas pendentes com data inferior ao dia atual?

Caso positivo:

Exibir alerta amarelo.

Mensagem

⚠ Existem tarefas pendentes de dias anteriores.

---

# Menu

Exemplo

Agenda (3)

onde

3 = quantidade pendente.

---

# Notificações

Nova Demanda

Demanda Concluída

Demanda Cancelada

Demanda Reagendada

Demanda Atrasada

Comentário Novo

---

# Relatórios

Demandas por Colaborador

Demandas por Departamento

Demandas por Período

Agenda Geral

Agenda Individual

Produtividade

Pendências

Tempo Médio

---

# Auditoria

Registrar:

Usuário

Data

Hora

IP

Operação

Tabela

Registro

Valores anteriores

Valores novos

---

# Permissões

Gestor

Administrador

Colaborador

Cada perfil deverá utilizar o sistema de permissões do O3Cloud Manager.

---

# Critérios de Aceite

CRUD funcionando.

Agenda funcionando.

Comentários funcionando.

Alertas funcionando.

Notificações funcionando.

Dashboards implementados.

Relatórios implementados.

Permissões funcionando.

Auditoria implementada.

---

# Definition Of Done

Repository

Service

Routes

Templates

Testes

Documentação

Changelog atualizado

Sprint atualizada

Roadmap atualizado

Architecture Freeze preservado.

---

# Observação

Este módulo deverá ser implementado totalmente desacoplado de integrações externas.

Na versão 2.0 as notificações, workflows e automações poderão ser migradas para o O3Cloud Infrastructure (O3Infra), preservando os contratos internos do sistema.



Documento de testes Beta:

- `docs/34-PENDENCIAS-TESTES-BETA-SPRINT-18.md`

Documento de fechamento:

- `docs/35-FECHAMENTO-SPRINT-18.md`

---

# Sprint 19 – Gestão de Clientes Inadimplentes

## 1. Objetivo

Criar dentro do módulo **Financeiro** do O3Cloud Manager uma funcionalidade para controle de inadimplência por contrato.

A funcionalidade deve permitir que a equipe Financeira:

* selecione um contrato;
* registre que o contrato possui pendência financeira;
* bloqueie operacionalmente o cliente no O3Cloud Manager;
* notifique a equipe de Suporte;
* notifique o cliente;
* destaque visualmente o cliente em todo o sistema;
* impeça novas propostas e novas implantações enquanto houver pendência ativa;
* posteriormente libere o cliente após:

  * quitação da pendência; ou
  * realização de acordo.

A funcionalidade não deve apagar histórico. Toda inclusão e liberação de inadimplência deve permanecer registrada para auditoria.

---

# 2. Localização no Sistema

Adicionar ao módulo:

Financeiro

novo item de menu:

Financeiro
├── Dashboard
├── Contratos
├── Faturamento
└── Inadimplentes

Nome da tela:

**Inadimplentes**

---

# 3. Regra Principal

A inadimplência será registrada por **Contrato**.

Entretanto:

> Se um cliente possuir pelo menos um contrato com inadimplência ATIVA, o Cliente deve ser considerado com pendência financeira em todo o O3Cloud Manager.

Portanto:

Contrato com pendência
↓
Cliente com restrição financeira
↓
Bloqueios operacionais

Quando não existir mais nenhuma inadimplência ativa vinculada aos contratos daquele cliente:

Cliente
↓
Restrição removida
↓
Operações liberadas

---

# 4. Nova Tela – Inadimplentes

URL sugerida:

`/financeiro/inadimplentes`

A tela deverá possuir:

* contratos atualmente inadimplentes;
* cliente;
* número do contrato;
* valor mensal;
* data do bloqueio;
* responsável pelo bloqueio;
* status;
* observação;
* ações.

Filtros:

* cliente;
* número do contrato;
* status;
* período;
* responsável.

Status principais:

* PENDENTE
* LIBERADO

Na interface:

PENDENTE → vermelho

LIBERADO → verde ou cinza

---

# 5. Nova Inadimplência

Adicionar botão:

`+ Nova Inadimplência`

A experiência deve seguir o padrão existente de:

Ambientes → Novo Ambiente

Fluxo:

1. Usuário acessa Financeiro → Inadimplentes.
2. Seleciona Nova Inadimplência.
3. Pesquisa e seleciona um contrato.
4. O sistema carrega automaticamente:

   * cliente;
   * número do contrato;
   * status;
   * valor mensal;
   * e-mail do cliente.
5. Financeiro informa:

   * motivo;
   * observações;
   * data da ocorrência, se necessário.
6. Confirma a inclusão.
7. Sistema registra a inadimplência.
8. Sistema coloca o cliente em restrição financeira.
9. Sistema envia as notificações.
10. Sistema passa a destacar esse cliente nas demais telas.

Não permitir registrar uma segunda inadimplência ATIVA para o mesmo contrato.

---

# 6. Notificação ao Suporte

Após a confirmação da inadimplência, enviar automaticamente e-mail para:

`sac@o3cloud.com.br` e `palntao@o3ti.com.br`


Assunto sugerido:

`[O3Cloud Manager] Bloqueio por pendência financeira – {cliente}`

Conteúdo mínimo:

Cliente:
{cliente}

Contrato:
{numero_contrato}

Status:
Pendência financeira registrada

Solicitação:
Realizar o bloqueio do ambiente do cliente devido a pendência financeira.

Registrado por:
{usuario}

Data:
{data_hora}

Observações:
{observacao}

IMPORTANTE:

O O3Cloud Manager não deve bloquear diretamente VM ou ambiente nesta primeira implementação.

O sistema apenas:

* registra a restrição;
* sinaliza o cliente;
* notifica o Suporte para executar o procedimento operacional.

A automação direta de bloqueio de ambiente poderá ser avaliada em sprint futuro.

---

# 7. Notificação ao Cliente

Após a inclusão da inadimplência, enviar também um e-mail para o endereço cadastrado na tela de Clientes.

Utilizar:

`clientes.email`

Se não existir e-mail:

* não impedir o cadastro da inadimplência;
* registrar que a notificação ao cliente não pôde ser enviada;
* exibir aviso para o Financeiro.

O conteúdo deve ser profissional e neutro.

Não expor informações técnicas internas.

Exemplo conceitual:

Assunto:

`Pendência financeira – O3Cloud`

Mensagem:

Informar que foi identificada uma pendência financeira relacionada ao contrato e solicitar contato com o setor Financeiro para regularização.

Os textos finais devem ficar configuráveis, evitando conteúdo fixo dentro da Route.

---

# 8. Destaque Visual do Cliente

Enquanto existir inadimplência ativa:

Todas as telas relevantes que apresentem referência ao cliente deverão deixar clara a restrição.

Adicionar destaque visual vermelho.

Exemplos:

## Tela Cliente

Exibir no topo:

`PENDÊNCIA FINANCEIRA`

com:

* fundo vermelho;
* ícone de alerta;
* data da restrição;
* contrato relacionado.

## Listagens

Onde o cliente aparecer, utilizar:

* badge vermelho;
* ícone de alerta; ou
* linha com indicação visual.

Texto sugerido:

`Pendência Financeira`

Evitar pintar telas inteiras de vermelho.

Utilizar destaque consistente e visível sem prejudicar a leitura.

---

# 9. Regra Transversal de Bloqueio

Enquanto o cliente possuir pendência financeira ativa:

## PROIBIR

* criação de novas propostas;
* criação de novas implantações.

A proteção deve existir na camada de **Service**, e não somente na interface.

Isso é obrigatório.

Mesmo que alguém tente chamar diretamente uma rota POST, a operação deve ser recusada.

Retorno funcional sugerido:

`Não é possível realizar esta operação. O cliente possui pendências financeiras ativas.`

---

# 10. Propostas

Ao tentar criar uma proposta para cliente inadimplente:

Bloquear a ação.

Exibir:

`Cliente com pendência financeira. Regularize a situação financeira antes de criar uma nova proposta.`

Se existir tela de seleção de cliente:

O cliente pode continuar aparecendo na pesquisa, porém deve estar identificado:

`⚠ PENDÊNCIA FINANCEIRA`

Não permitir concluir o cadastro.

---

# 11. Implantações

Aplicar exatamente a mesma regra.

Ao tentar criar nova implantação:

Verificar se o cliente possui inadimplência ativa.

Se possuir:

* impedir criação;
* mostrar mensagem;
* não gravar registro parcial.

Clientes já em implantação não devem ser apagados ou alterados automaticamente.

O bloqueio é para **novas implantações**.

---

# 12. Liberação Financeira

Na própria tela Financeiro → Inadimplentes, uma pendência PENDENTE deve possuir ação:

`Liberar`

Ao clicar:

Abrir modal ou formulário de liberação.

O Financeiro deverá obrigatoriamente selecionar uma das opções:

### QUITOU PENDÊNCIA

Cliente efetuou o pagamento integral da pendência.

Código sugerido:

`QUITACAO`

### REALIZOU ACORDO

Foi firmado acordo financeiro e o cliente está autorizado a continuar utilizando/contratando os serviços.

Código sugerido:

`ACORDO`

Também permitir:

* observação da liberação;
* data;
* responsável.

---

# 13. Regra de Liberação do Cliente

Após liberar uma inadimplência:

Verificar:

`Existe outra inadimplência ATIVA em outro contrato deste cliente?`

### Se SIM

Manter cliente:

`COM PENDÊNCIA FINANCEIRA`

Não liberar:

* propostas;
* implantações.

### Se NÃO

Remover restrição financeira do cliente.

Liberar novamente:

* novas propostas;
* novas implantações.

Remover os avisos vermelhos.

Isso é extremamente importante para clientes que possuem vários contratos.

Enviar email para o contato de email do cadastro do cliente, e tambem para sac@o3cloud.com.br e plantao@o3ti.com.br;
Informando da liberação do sistema;

---

# 14. Histórico

Nunca excluir registros de inadimplência.

O sistema deve preservar:

* contrato;
* cliente;
* data da inclusão;
* usuário que incluiu;
* motivo;
* observação;
* data da liberação;
* usuário que liberou;
* tipo de liberação;
* observação da liberação.

Exemplo:

Cliente ABC

Contrato 2026/00125

Bloqueado:
01/08/2026

Liberado:
07/08/2026

Motivo da liberação:
ACORDO

---

# 15. Modelagem Sugerida

Criar tabela:

`financeiro_inadimplencias`

Campos sugeridos:

```sql
id BIGINT AUTO_INCREMENT PRIMARY KEY,
uuid CHAR(36) NOT NULL,

contrato_id BIGINT NOT NULL,

status ENUM(
    'PENDENTE',
    'LIBERADO'
) NOT NULL DEFAULT 'PENDENTE',

motivo VARCHAR(255) NULL,

observacoes TEXT NULL,

bloqueado_em DATETIME NOT NULL,

bloqueado_por BIGINT NULL,

tipo_liberacao ENUM(
    'QUITACAO',
    'ACORDO'
) NULL,

observacao_liberacao TEXT NULL,

liberado_em DATETIME NULL,

liberado_por BIGINT NULL,

email_suporte_enviado TINYINT(1) DEFAULT 0,

email_cliente_enviado TINYINT(1) DEFAULT 0,

erro_email_suporte TEXT NULL,

erro_email_cliente TEXT NULL,

ativo TINYINT(1) NOT NULL DEFAULT 1,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP
```

FK:

`contrato_id → contratos.id`

Não é obrigatório armazenar `cliente_id`.

O cliente deve ser obtido através:

inadimplência
→ contrato
→ cliente

Isso evita duplicidade desnecessária de relacionamento.

---

# 16. Índices

Criar:

```sql
INDEX idx_inadimplencia_contrato (contrato_id)

INDEX idx_inadimplencia_status (status)

INDEX idx_inadimplencia_bloqueado_em (bloqueado_em)
```

Também criar mecanismo para impedir duas inadimplências simultaneamente ativas para o mesmo contrato.

A implementação pode ser feita por regra no Service e validação transacional.

---

# 17. Arquitetura Python

Seguir obrigatoriamente o padrão atual do O3Cloud Manager:

Repository
↓
Service
↓
Routes
↓
Templates
↓
Testes

Criar:

```text
app/financeiro/inadimplencias/
├── __init__.py
├── repository.py
├── service.py
└── routes.py
```

ou adaptar à organização atual do módulo Financeiro sem quebrar a arquitetura existente.

Templates:

```text
app/templates/financeiro/inadimplencias/
├── index.html
├── form.html
└── view.html
```

---

# 18. Repository

Métodos mínimos:

```python
listar()
total()
buscar_por_id()
buscar_ativa_por_contrato()
listar_ativas_por_cliente()
cliente_possui_pendencia()
criar()
liberar()
```

Repository não deve:

* enviar e-mail;
* bloquear proposta;
* bloquear implantação;
* decidir regra de liberação.

Repository apenas persiste dados.

---

# 19. Service

Criar:

`InadimplenciaService`

Responsável por:

```python
registrar()
liberar()
cliente_possui_pendencia()
validar_operacao_cliente()
```

Fluxo de `registrar()`:

1. validar contrato;
2. validar se não existe pendência ativa;
3. criar registro;
4. confirmar transação;
5. disparar notificações;
6. retornar resultado.

Fluxo de `liberar()`:

1. localizar inadimplência;
2. validar status;
3. exigir QUITACAO ou ACORDO;
4. registrar liberação;
5. verificar outras pendências do cliente;
6. recalcular situação financeira;
7. liberar operações apenas se nenhuma outra pendência permanecer ativa.

---

# 20. Serviço Central de Validação Financeira

Não duplicar a regra em Propostas e Implantação.

Criar uma função reutilizável:

```python
InadimplenciaService.validar_operacao_cliente(cliente_id)
```

Exemplo:

```python
if InadimplenciaService.cliente_possui_pendencia(cliente_id):
    raise RegraNegocioError(
        "Cliente possui pendências financeiras ativas."
    )
```

Utilizar essa validação no:

* Service de Propostas;
* Service de Implantação.

No futuro poderá ser reutilizada em outros módulos.

---

# 21. E-mails

Utilizar o serviço de e-mail existente no O3Cloud Manager.

Não colocar SMTP diretamente no módulo de inadimplência.

Criar métodos de alto nível, por exemplo:

```python
notificar_bloqueio_suporte()
notificar_pendencia_cliente()
```

Se já existir provider de comunicação, reutilizá-lo.

Configurar o destinatário do suporte no `.env` ou tabela de configurações:

```env
FINANCEIRO_EMAIL_SUPORTE=sac@o3cloud.com.br
```

Evitar endereço fixo espalhado pelo código.

---

# 22. Falha de E-mail

A falha no envio de um e-mail NÃO deve desfazer o registro da inadimplência.

Exemplo:

Pendência registrada com sucesso
+
Falha ao enviar e-mail

Resultado:

* inadimplência continua ativa;
* cliente continua bloqueado;
* sistema registra erro;
* interface avisa Financeiro.

Nunca executar rollback da inadimplência porque SMTP/API ficou indisponível.

---

# 23. Notificação na Liberação

Recomendação:

Quando a pendência for liberada, enviar também e-mail para:

`sac@o3cloud.com.br`

informando:

`Cliente liberado financeiramente`

para que o Suporte possa retirar eventual bloqueio aplicado ao ambiente.

Dados:

* cliente;
* contrato;
* tipo da liberação;
* responsável;
* data;
* observação.

Essa notificação é altamente recomendada porque o bloqueio operacional do ambiente foi solicitado anteriormente ao Suporte.

O envio para o cliente na liberação pode ser parametrizável.

---

# 24. Segurança

Apenas usuários autorizados do Financeiro devem poder:

* registrar inadimplência;
* liberar inadimplência.

Outros usuários poderão visualizar o aviso financeiro conforme permissão, mas não alterar o status.

Registrar obrigatoriamente:

* usuário;
* data;
* ação.

---

# 25. Interface – Listagem

Exemplo:

```text
INADIMPLENTES

[ + Nova Inadimplência ]

Cliente          Contrato       Desde       Status       Ações
----------------------------------------------------------------
Cliente ABC      2026/00125     05/08       PENDENTE     Ver | Liberar
Cliente XYZ      2026/00190     07/08       PENDENTE     Ver | Liberar
```

Usar badge vermelho:

`PENDENTE`

Para histórico:

`LIBERADO`

---

# 26. Interface – Cliente

Adicionar alerta no topo das telas relacionadas ao cliente:

```text
⚠ PENDÊNCIA FINANCEIRA

Este cliente possui pendências financeiras ativas.

Contrato: 2026/00125
Desde: 05/08/2026
```

Não exibir detalhes financeiros sensíveis desnecessariamente para perfis sem autorização.

---

# 27. Critérios de Aceite

A Sprint estará concluída quando:

1. Financeiro conseguir abrir tela Inadimplentes.
2. Conseguir selecionar contrato.
3. Sistema identificar automaticamente o cliente.
4. Não permitir pendência ativa duplicada para o mesmo contrato.
5. Registrar inadimplência.
6. Enviar notificação para `sac@o3cloud.com.br`.
7. Enviar notificação para `clientes.email`.
8. Falha de e-mail não cancelar o bloqueio.
9. Cliente aparecer com destaque vermelho.
10. Nova proposta para cliente inadimplente ser bloqueada.
11. Nova implantação para cliente inadimplente ser bloqueada.
12. Bloqueio existir também no Service e não apenas na interface.
13. Financeiro conseguir liberar pendência.
14. Liberação exigir:

    * QUITACAO; ou
    * ACORDO.
15. Histórico permanecer salvo.
16. Cliente continuar bloqueado caso outro contrato ainda possua pendência ativa.
17. Cliente ser liberado quando não houver mais pendências ativas.
18. Alertas visuais desaparecerem após liberação.
19. Novas propostas voltarem a ser permitidas.
20. Novas implantações voltarem a ser permitidas.
21. Testes existentes continuarem passando.
22. Documentação, DER, modelo físico e CHANGELOG serem atualizados.

---

# 28. Testes Obrigatórios

Testar:

* cliente com 1 contrato;
* cliente com vários contratos;
* inadimplência em apenas um dos contratos;
* inadimplência em dois contratos simultaneamente;
* liberação de apenas um contrato;
* liberação do último contrato pendente;
* quitação;
* acordo;
* cliente sem e-mail;
* erro no envio para suporte;
* tentativa de criar proposta;
* tentativa de criar implantação;
* tentativa direta por POST;
* duplicidade de inadimplência;
* usuário sem permissão;
* histórico após liberação.

---

# 29. Fora do Escopo

Não implementar nesta Sprint:

* bloqueio automático no Proxmox;
* shutdown de VM;
* bloqueio de rede;
* suspensão automática de VPS;
* integração automática com cobrança do OMIE;
* baixa automática por boleto;
* liberação automática por API bancária.

Esses itens poderão ser evoluções futuras.

Nesta Sprint, o Financeiro controla a restrição no O3Cloud Manager e o Suporte recebe a solicitação operacional por e-mail.

---

# 30. Resultado Esperado

O fluxo final deverá ser:

```text
Financeiro
    ↓
Seleciona Contrato
    ↓
Registra Pendência
    ↓
O3Cloud Manager
    ├── registra histórico
    ├── marca cliente com restrição
    ├── bloqueia novas propostas
    ├── bloqueia novas implantações
    ├── envia e-mail ao Suporte
    └── envia e-mail ao Cliente

Após regularização:

Financeiro
    ↓
Liberar
    ↓
[Quitação] ou [Acordo]
    ↓
Verificar outras pendências
    ↓
Se nenhuma:
    ├── retirar restrição
    ├── liberar propostas
    ├── liberar implantações
    ├── remover alertas vermelhos
    └── notificar liberação
```

A arquitetura deve preservar histórico completo e permitir futuras automações sem necessidade de remodelar o módulo.
 _____


# Sprint Final Planejada

## Integracao Receita Federal para Cadastro de Clientes

Status:

Planejada para a sprint final

Objetivo:

Permitir que o cadastro manual de novos clientes consulte uma API de dados da Receita Federal, ou provedor homologado, a partir do CNPJ informado, preenchendo automaticamente os dados cadastrais disponiveis.

Escopo previsto:

- Consultar dados cadastrais pelo CNPJ durante o cadastro de cliente.
- Preencher campos compativeis do cliente, mantendo revisao manual antes do salvamento.
- Tratar indisponibilidade da API como aviso operacional, sem bloquear cadastro manual.
- Definir provedor, limites, cache, autenticacao e auditoria tecnica apenas na sprint final.

Observacao:

Esta integracao fica fora da Sprint 15 e das sprints intermediarias de infraestrutura, permanecendo como backlog final para fechamento da versao.

---

# Diretriz

Toda evolução do projeto deve permanecer alinhada ao ROADMAP.md, que é a fonte oficial para sequência das próximas etapas.
