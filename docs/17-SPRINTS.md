# O3Cloud Manager v3.0

# 17 - SPRINTS

Versão: 3.0 Alpha

Última atualização: 10/08/2026

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

Planejado - estrutura revisada em 10/08/2026 antes do fechamento do pacote Beta.

---

## Estrutura Atualizada em 10/08/2026

Antes de iniciar o Sprint Final de homologacao da Beta, o Sprint 17 permanece como frente pendente para organizar o modulo Financeiro de Comissoes e fechar a nova Visao Geral operacional do sistema.

Pendencias de estruturacao:

- confirmar regras de comissionamento por executivo, produto, contrato e recorrencia;
- definir criterios de aprovacao, fechamento mensal, pagamento e auditoria;
- revisar indicadores executivos que devem alimentar a Visao Geral;
- manter evidencias de calculo e rastreabilidade para homologacao posterior;
- nao considerar o pacote Beta fechado antes desta estrutura estar alinhada.

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
3. Pesquisa e seleciona um contrato por número, cliente, razão social ou CNPJ.
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

`sac@o3cloud.com.br` e `plantao@o3ti.com.br`


Assunto sugerido:

`[O3Cloud Manager] Bloqueio por pendência financeira – {cliente}`

Conteúdo mínimo:

Cliente:
{cliente}

Razão Social:
{razao_social}

CNPJ:
{cnpj}

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

Informar que foi identificada uma pendência financeira relacionada ao contrato, incluindo razão social e CNPJ do contrato bloqueado.

Incluir os canais de regularização:

* telefone: 19 3142-0232 opção 3;
* telefone/WhatsApp: 19 99912-4028;
* e-mail: contas@o3cloud.com.br.

Os textos finais devem ficar centralizados no Service, evitando conteúdo fixo dentro da Route.

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

Enviar e-mail para o contato de e-mail do cadastro do cliente, e também para `sac@o3cloud.com.br` e `plantao@o3ti.com.br`, informando a liberação do sistema.

Os e-mails de liberação enviados ao cliente e ao time técnico devem incluir:

* cliente;
* razão social;
* CNPJ no padrão `00.000.000/0000-00`;
* número do contrato;
* tipo de liberação;
* responsável e data quando aplicável.

---

# 14. Histórico

Não executar exclusão física de registros de inadimplência no fluxo operacional.

Para ciclos de teste e saneamento controlado, o perfil `ADMIN` pode remover um histórico da lista por exclusão lógica (`ativo=0`). Essa ação deve retirar o registro das consultas operacionais e do bloqueio financeiro, mas preservar o registro no banco.

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
* observação da liberação;
* ativo/inativo para remoção lógica administrativa.

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

A implementação deve combinar regra no Service e validação transacional. Para MariaDB, evitar `UNIQUE(contrato_id, status)` simples, pois isso bloquearia múltiplos históricos `LIBERADO`. A regra inicial da Sprint 19 deve usar leitura transacional do contrato antes de inserir e índice de apoio em `contrato_id`, `status` e `ativo`.

Migration prevista:

`database/migrations/076_create_financeiro_inadimplencias.sql`

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

Criar ou adaptar ao padrão atual do módulo Financeiro:

```text
app/financeiro/inadimplencias_repository.py
app/financeiro/inadimplencias_service.py
app/financeiro/routes.py
```

O módulo Financeiro atual ainda utiliza `routes.py`, `service.py` e `repository.py` em estrutura plana. A Sprint 19 pode isolar a persistência e regra em arquivos próprios de inadimplência, mantendo as rotas no blueprint financeiro existente para reduzir impacto de registro de blueprint.

Adicionar nova chave de permissão:

`inadimplentes`

Essa chave deve entrar em `MENU_PERMISSOES`, `ENDPOINT_PERMISSOES` e no menu lateral do grupo Financeiro.

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
* decidir regra de liberação;
* decidir permissão de exclusão administrativa.

Repository apenas persiste dados.

---

# 19. Service

Criar:

`InadimplenciaService`

Responsável por:

```python
registrar()
liberar()
excluir_historico()
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
FINANCEIRO_EMAIL_SUPORTE=sac@o3cloud.com.br,plantao@o3ti.com.br
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

`sac@o3cloud.com.br` e `plantao@o3ti.com.br`

informando:

`Cliente liberado financeiramente`

para que o Suporte possa retirar eventual bloqueio aplicado ao ambiente.

Dados:

* cliente;
* razão social;
* CNPJ;
* contrato;
* tipo da liberação;
* responsável;
* data;
* observação.

Essa notificação é altamente recomendada porque o bloqueio operacional do ambiente foi solicitado anteriormente ao Suporte.

O envio para o cliente na liberação deve ocorrer pelo serviço de e-mail existente e incluir razão social e CNPJ do contrato liberado.

---

# 24. Segurança

Apenas usuários autorizados do Financeiro devem poder:

* registrar inadimplência;
* liberar inadimplência.

Apenas o perfil `ADMIN` deve poder:

* remover histórico de inadimplência da lista por inativação lógica (`ativo=0`).

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
Cliente ABC      2026/00125     05/08       PENDENTE     Ver | Liberar | Excluir histórico (ADMIN)
Cliente XYZ      2026/00190     07/08       LIBERADO     Ver | Excluir histórico (ADMIN)
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
23. Busca e visualização de CNPJ usarem o padrão `00.000.000/0000-00`, aceitando CNPJ com ou sem máscara.
24. E-mails de bloqueio e liberação incluírem razão social e CNPJ para cliente e time técnico.
25. ADMIN conseguir remover histórico por inativação lógica, enquanto outros perfis não veem a ação e são bloqueados no backend.

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

# Sprint 20 – Módulo de Relatórios Customizáveis

## 1. Objetivo

Criar no O3Cloud Manager um módulo central de **Relatórios Customizáveis**, permitindo que usuários autorizados construam relatórios de acordo com a necessidade de cada departamento.

O sistema possui vários módulos e diferentes necessidades operacionais. Portanto, não criar apenas relatórios fixos.

A solução deve permitir:

* selecionar a fonte de dados;
* escolher os campos que serão exibidos;
* aplicar filtros;
* filtrar por período;
* ordenar;
* agrupar;
* realizar cálculos quando existirem campos numéricos;
* salvar modelos de relatórios;
* executar novamente modelos salvos;
* exportar resultados;
* imprimir diretamente.

Formatos obrigatórios:

* PDF;
* CSV;
* XLSX;
* DOCX;
* impressão direta pelo navegador.

---

# 2. Controle de Acesso

Somente usuários cujo perfil possuir permissão explícita para acessar o módulo de Relatórios poderão abrir a tela.

Criar permissão funcional equivalente a:

`RELATORIOS_ACESSAR`

O controle deve existir no backend e não apenas no menu.

Usuários sem permissão:

* não visualizam o item Relatórios;
* não acessam diretamente as rotas;
* recebem resposta de acesso negado quando tentarem acessar por URL.

---

# 3. Perfis com Poder de Criação

Os seguintes perfis poderão criar e customizar relatórios:

* Administrador;
* Diretoria;
* Administrativo_Gestor.

Criar permissão específica equivalente a:

`RELATORIOS_CRIAR`

Não depender somente do nome textual do perfil.

Utilizar o sistema de permissões atual.

Outros perfis poderão futuramente possuir:

`RELATORIOS_VISUALIZAR`

permitindo executar relatórios previamente disponibilizados sem modificar sua definição.

---

# 4. Princípio de Segurança

O construtor de relatórios NÃO deve permitir SQL livre digitado pelo usuário.

Não criar campo:

`Digite sua consulta SQL`

A aplicação deverá trabalhar com **fontes de dados previamente cadastradas e autorizadas**.

Isso evita:

* SQL Injection;
* exposição de dados sensíveis;
* consultas destrutivas;
* acesso indevido entre departamentos;
* travamento do banco por queries arbitrárias.

---

# 5. Conceito de Fonte de Dados

Criar conceito:

`Fonte de Relatório`

Exemplos:

* Clientes;
* Contratos;
* Inadimplências;
* Faturamentos;
* Leads;
* Eventos;
* Participantes de Eventos;
* Contatos;
* Oportunidades;
* Propostas;
* Parceiros;
* Implantações;
* Ambientes;
* Recursos;
* Licenças;
* Demandas Administrativas;
* Comissões;
* Histórico de Sincronizações.

Cada fonte deverá disponibilizar somente campos explicitamente autorizados.

---

# 6. Catálogo de Campos

Cada fonte deverá possuir definição de campos disponíveis.

Exemplo conceitual:

Fonte:

`Contratos`

Campos:

* número;
* cliente;
* origem;
* status;
* início da vigência;
* fim da vigência;
* valor mensal;
* dia de faturamento;
* vendedor;
* projeto.

Cada campo deverá possuir metadados:

* código interno;
* nome exibido;
* tipo;
* se pode ser filtrado;
* se pode ser agrupado;
* se pode ser ordenado;
* se pode receber agregação;
* formato de saída;
* nível de sensibilidade.

Tipos previstos:

* TEXTO;
* INTEIRO;
* DECIMAL;
* MOEDA;
* DATA;
* DATETIME;
* BOOLEAN;
* STATUS;
* PERCENTUAL.

---

# 7. Construtor de Relatório

Criar tela:

`Relatórios → Novo Relatório`

Fluxo:

1. Usuário informa nome do relatório.
2. Seleciona uma fonte de dados.
3. Sistema apresenta campos disponíveis.
4. Usuário seleciona os campos desejados.
5. Define a ordem das colunas.
6. Configura filtros.
7. Configura ordenação.
8. Configura agrupamentos, quando aplicável.
9. Configura cálculos.
10. Visualiza uma prévia.
11. Executa.
12. Opcionalmente salva como modelo.

---

# 8. Seleção de Campos

A interface deverá permitir adicionar e remover campos.

Preferencialmente utilizar:

* seleção múltipla; ou
* lista de campos disponíveis versus selecionados;
* drag-and-drop apenas se já houver infraestrutura JS segura no projeto.

Não tornar drag-and-drop obrigatório para a primeira versão.

Exemplo:

Disponíveis:

* Cliente
* Contrato
* Status
* Valor mensal
* Início
* Fim
* Origem

Selecionados:

1. Cliente
2. Contrato
3. Status
4. Valor mensal

---

# 9. Filtros

Suportar filtros de acordo com o tipo do campo.

## Texto

* igual;
* diferente;
* contém;
* começa com.

## Número / Moeda

* igual;
* maior que;
* maior ou igual;
* menor que;
* menor ou igual;
* entre.

## Data

* igual;
* antes;
* depois;
* entre.

## Status / Enum

* igual;
* diferente;
* em uma lista.

## Boolean

* sim;
* não.

---

# 10. Filtro por Período

Para campos DATA e DATETIME permitir:

`Data inicial`

`Data final`

Exemplo:

01/07/2026 a 31/07/2026

O usuário deve poder escolher qual campo de data será utilizado quando a fonte possuir mais de uma data.

Exemplo:

Contratos:

* início da vigência;
* fim da vigência;
* data de criação;
* última sincronização.

---

# 11. Cálculos

Para campos numéricos permitir cálculos.

Agregações previstas:

* SOMA;
* MÉDIA;
* MÍNIMO;
* MÁXIMO;
* CONTAGEM;
* CONTAGEM DISTINTA.

Exemplo:

Relatório de contratos:

Campo:

`valor_mensal`

Agregação:

`SOMA`

Resultado:

`Total mensal: R$ 185.320,00`

---

# 12. Agrupamentos

Permitir agrupamento por campos compatíveis.

Exemplos:

## Comercial

Agrupar oportunidades por:

* executivo;
* status;
* parceiro;
* mês.

Depois calcular:

* total de oportunidades;
* valor estimado;
* valor médio;
* taxa de ganho.

## Financeiro

Agrupar contratos por:

* cliente;
* status;
* vendedor;
* mês;
* origem.

Calcular:

* quantidade;
* soma do valor mensal;
* média.

---

# 13. Campos Calculados

Na primeira versão NÃO permitir fórmulas arbitrárias escritas pelo usuário.

Permitir apenas cálculos predefinidos e seguros.

No futuro poderá existir recurso de:

`Campo calculado`

mas deve ser implementado com parser seguro e nunca com execução direta de Python, SQL ou JavaScript.

---

# 14. Relatórios Salvos

Permitir salvar uma configuração como modelo.

Exemplo:

`Contratos Ativos por Cliente`

Salvar:

* fonte;
* campos;
* filtros;
* agrupamentos;
* ordenação;
* agregações;
* nome;
* descrição;
* criador.

Posteriormente o usuário poderá:

* executar;
* duplicar;
* editar;
* excluir, conforme permissão.

---

# 15. Visibilidade dos Modelos

Cada relatório salvo deverá possuir visibilidade:

* PRIVADO;
* PERFIL;
* GLOBAL.

## PRIVADO

Somente o criador.

## PERFIL

Disponível para perfis autorizados escolhidos.

## GLOBAL

Disponível para usuários que tenham permissão de visualizar relatórios.

Somente Administrador, Diretoria e Administrativo_Gestor poderão publicar modelos GLOBAL.

---

# 16. Exportação

Todos os relatórios gerados ou exibidos devem possuir cabeçalho padrão com o logo da O3Cloud no topo.

Usar preferencialmente o ativo existente:

`app/static/img/logo.png`

O cabeçalho deve aparecer em:

* prévia/resultado HTML;
* impressão direta;
* PDF;
* DOCX;
* XLSX, quando tecnicamente suportado pela biblioteca;
* capa ou primeira linha identificadora nos formatos em que imagem não for adequada.

Na tela do resultado disponibilizar:

`Exportar`

Opções:

* PDF;
* CSV;
* XLSX;
* DOCX;
* Imprimir.

---

# 17. CSV

Gerar arquivo:

* UTF-8;
* cabeçalho textual com identificação `O3Cloud Manager`, já que CSV não suporta imagem de logo de forma nativa;
* cabeçalho de colunas;
* dados já filtrados;
* somente colunas selecionadas.

Evitar conversões desnecessárias.

---

# 18. XLSX

Utilizar biblioteca Python compatível com a arquitetura atual.

Preferencialmente:

`openpyxl`

Gerar planilha profissional contendo:

* logo da O3Cloud no cabeçalho;
* título;
* data de geração;
* usuário;
* filtros aplicados;
* cabeçalhos;
* dados;
* totais;
* formatação de datas;
* formatação monetária;
* auto filtro;
* congelamento do cabeçalho quando aplicável.

Não utilizar LibreOffice como mecanismo principal para XLSX.

---

# 18.1. Dependências de Exportação

Dependências esperadas para implementação:

* `openpyxl` para XLSX;
* `python-docx` para DOCX;
* `reportlab` para PDF.

As dependências confirmadas devem permanecer registradas em `requirements.txt`.

---

# 19. PDF

O PDF deve possuir:

* logo da O3Cloud no cabeçalho;
* nome do relatório;
* data/hora da geração;
* usuário que gerou;
* período/filtros;
* tabela;
* totais;
* paginação;
* rodapé.

Para relatórios muito largos:

* utilizar orientação paisagem;
* ajustar largura das colunas;
* se necessário informar que determinado conjunto de colunas é mais adequado para XLSX.

---

# 20. DOCX

Gerar documento contendo:

* logo da O3Cloud no cabeçalho;
* título;
* data de geração;
* filtros;
* tabela;
* totalizadores;
* rodapé.

Utilizar biblioteca Python apropriada, preferencialmente:

`python-docx`

---

# 21. Impressão Direta

Criar versão HTML específica para impressão.

Utilizar:

`window.print()`

com CSS:

`@media print`

Ocultar:

* navbar;
* sidebar;
* botões;
* filtros;
* elementos de navegação.

Manter:

* logo da O3Cloud no cabeçalho;
* título;
* filtros;
* dados;
* totais;
* data da geração.

---

# 22. Paginação

Na tela:

utilizar paginação.

Não carregar centenas de milhares de registros no browser.

Exemplo:

50 ou 100 registros por página.

Exportações deverão executar a consulta completa filtrada, respeitando limite máximo de segurança.

---

# 23. Limite de Exportação

Criar configuração:

`RELATORIOS_MAX_EXPORT_ROWS`

Exemplo inicial:

50000

Se ultrapassar:

* impedir exportação síncrona;
* informar ao usuário;
* futuramente permitir geração assíncrona.

Não permitir que uma consulta gigantesca trave a aplicação.

---

# 24. Timeout

Consultas de relatórios deverão possuir limite operacional.

Registrar:

* tempo de execução;
* quantidade de registros;
* usuário;
* fonte.

Relatórios muito pesados deverão ser identificáveis para futura otimização.

---

# 25. Auditoria

Registrar toda geração de relatório.

Criar tabela conceitual:

`relatorios_execucoes`

Campos:

* id;
* uuid;
* relatorio_id, se salvo;
* usuario_id;
* fonte;
* filtros_snapshot;
* colunas_snapshot;
* formato;
* registros;
* iniciado_em;
* finalizado_em;
* duracao_ms;
* status;
* erro.

Não armazenar necessariamente todos os dados retornados.

Guardar configuração utilizada.

---

# 26. Modelagem Sugerida

Criar tabelas:

## relatorios

* id;
* uuid;
* nome;
* descricao;
* fonte_codigo;
* configuracao_json;
* visibilidade;
* criado_por;
* ativo;
* created_at;
* updated_at.

## relatorios_perfis

* id;
* relatorio_id;
* perfil_id.

## relatorios_execucoes

* id;
* uuid;
* relatorio_id;
* usuario_id;
* fonte_codigo;
* formato;
* filtros_json;
* campos_json;
* registros;
* duracao_ms;
* status;
* mensagem_erro;
* created_at;
* finalizado_em.

Os nomes devem ser adaptados ao padrão real do banco.

---

# 27. Configuração JSON

A definição do relatório pode ser armazenada em JSON.

Exemplo conceitual:

```json
{
  "fonte": "contratos",
  "campos": [
    "cliente",
    "numero",
    "status",
    "valor_mensal"
  ],
  "filtros": [
    {
      "campo": "status",
      "operador": "IGUAL",
      "valor": "ATIVO"
    }
  ],
  "ordenacao": [
    {
      "campo": "cliente",
      "direcao": "ASC"
    }
  ],
  "agrupamentos": [],
  "agregacoes": [
    {
      "campo": "valor_mensal",
      "funcao": "SOMA"
    }
  ]
}
```

Nunca converter esse JSON diretamente em SQL sem validação.

---

# 28. Engine de Relatórios

Criar camada central:

`ReportEngine`

Responsabilidades:

* carregar fonte autorizada;
* validar campos;
* validar filtros;
* validar operadores;
* gerar SQL seguro;
* construir parâmetros;
* executar consulta;
* montar agregações;
* aplicar paginação;
* retornar resultado estruturado.

Nunca concatenar valores fornecidos pelo usuário diretamente no SQL.

Todos os valores devem utilizar parâmetros `%s`.

Campos e nomes de tabelas somente podem vir de catálogo interno previamente cadastrado.

---

# 29. Fontes como Código

Na primeira versão, recomendo definir fontes no backend, e não permitir cadastro livre pela interface.

Exemplo conceitual:

```python
REPORT_SOURCES = {
    "contratos": {
        "nome": "Contratos",
        "from": "...",
        "campos": {...}
    }
}
```

ou classes:

```python
ContratoReportSource
ClienteReportSource
OportunidadeReportSource
```

Isso torna a solução muito mais segura.

No futuro, o catálogo poderá migrar para banco se houver necessidade.

---

# 30. Arquitetura Python

Sugestão:

```text
app/relatorios/
├── __init__.py
├── routes.py
├── service.py
├── repository.py
├── engine.py
├── permissions.py
├── sources/
│   ├── __init__.py
│   ├── clientes.py
│   ├── contratos.py
│   ├── financeiro.py
│   ├── comercial.py
│   └── administrativo.py
└── exporters/
    ├── __init__.py
    ├── csv_exporter.py
    ├── xlsx_exporter.py
    ├── pdf_exporter.py
    └── docx_exporter.py
```

Templates:

```text
templates/relatorios/
├── index.html
├── builder.html
├── resultado.html
├── view.html
└── print.html
```

---

# 31. Separação de Responsabilidades

Routes:

* receber request;
* validar permissão;
* chamar Service;
* renderizar.

Service:

* regras de negócio;
* salvar modelos;
* validar visibilidade;
* chamar Engine;
* exportar.

Engine:

* consulta dinâmica segura.

Repository:

* persistência de relatórios e histórico.

Exporters:

* transformação do resultado nos formatos solicitados.

---

# 32. Permissões por Fonte

A permissão Relatórios não deverá automaticamente conceder acesso a todos os dados.

Exemplo:

Um usuário pode ter:

`RELATORIOS_ACESSAR`

mas não possuir:

`FINANCEIRO_VISUALIZAR`

Nesse caso:

a fonte Financeiro NÃO deve aparecer.

A disponibilidade das fontes deve considerar as permissões funcionais dos módulos.

Exemplo:

* Financeiro → exige permissão financeira;
* CRM → exige permissão comercial;
* Administrativo → exige permissão administrativa.

Administrador e Diretoria podem seguir regras específicas conforme sistema atual.

---

# 33. Dados Sensíveis

Campos sensíveis não devem ficar automaticamente disponíveis.

Exemplos possíveis:

* dados bancários;
* credenciais;
* tokens;
* API Keys;
* senhas;
* documentos sigilosos.

Nunca disponibilizar segredos em fonte de relatório.

---

# 34. Cálculos Comerciais

Fontes do CRM poderão disponibilizar métricas como:

* quantidade de leads;
* oportunidades por executivo;
* oportunidades ganhas;
* oportunidades perdidas;
* valor estimado;
* valor ganho;
* ticket médio;
* taxa de conversão.

Essas métricas deverão utilizar regras centrais previamente definidas.

---

# 35. Cálculos Financeiros

Fontes Financeiras poderão disponibilizar:

* soma de contratos;
* receita mensal;
* quantidade de contratos;
* inadimplências;
* valores por cliente;
* valores por período.

Não reinventar cálculos já existentes nos Services do módulo Financeiro quando houver regra de negócio específica.

---

# 36. Exemplos de Relatórios

## Diretoria

`Receita mensal por cliente`

Campos:

* Cliente;
* Contratos;
* Valor Mensal.

Agrupar:

Cliente.

Calcular:

SOMA(valor_mensal).

---

## Comercial

`Oportunidades por Executivo`

Campos:

* Executivo;
* Status;
* Valor;
* Probabilidade.

Período:

01/07/2026 → 31/07/2026.

Agrupar:

Executivo.

Calcular:

CONTAGEM;

SOMA(valor).

---

## Administrativo

`Demandas administrativas por colaborador`

Campos:

* Colaborador;
* Tipo;
* Data;
* Status;
* Prazo.

Filtrar:

Status = PENDENTE.

---

## Financeiro

`Contratos inadimplentes`

Campos:

* Cliente;
* Contrato;
* Data da pendência;
* Status;
* Tipo de regularização.

---

# 37. UX do Builder

Organizar a tela em etapas:

1. Fonte
2. Campos
3. Filtros
4. Agrupamento e cálculos
5. Ordenação
6. Prévia
7. Salvar / Exportar

Não apresentar todas as configurações ao mesmo tempo se isso tornar a interface confusa.

---

# 38. Prévia

Antes de executar relatório completo:

permitir `Pré-visualizar`.

Limitar a prévia, por exemplo:

100 registros.

A prévia deve mostrar:

* colunas;
* filtros;
* agregações;
* amostra dos dados.

---

# 39. Tratamento de Erros

Mensagens funcionais:

* fonte não autorizada;
* campo inválido;
* filtro inválido;
* período inválido;
* nenhum resultado;
* limite de exportação excedido;
* erro de geração;
* consulta excedeu tempo permitido.

Nunca exibir SQL bruto ao usuário.

---

# 40. Testes Obrigatórios

Testar:

1. usuário sem RELATORIOS_ACESSAR;
2. usuário autorizado;
3. Administrador criando relatório;
4. Diretoria criando relatório;
5. Administrativo_Gestor criando relatório;
6. perfil somente visualização;
7. fonte sem permissão;
8. seleção de campos;
9. filtros texto;
10. filtros numéricos;
11. filtros data;
12. múltiplos filtros;
13. agrupamento;
14. soma;
15. média;
16. contagem;
17. ordenação;
18. paginação;
19. relatório sem resultados;
20. salvar;
21. editar;
22. duplicar;
23. excluir;
24. visibilidade privada;
25. visibilidade por perfil;
26. global;
27. CSV;
28. XLSX;
29. PDF;
30. DOCX;
31. impressão;
32. caracteres especiais/acentuação;
33. valores monetários;
34. datas brasileiras;
35. tentativa de manipular nome de campo;
36. tentativa de SQL Injection;
37. tentativa de acessar fonte sem permissão;
38. limite máximo de exportação;
39. registro de auditoria;
40. regressão dos módulos existentes.

---

# 41. Critérios de Aceite

A Sprint será considerada concluída quando:

* somente usuários autorizados acessarem Relatórios;
* Administrador, Diretoria e Administrativo_Gestor puderem criar modelos;
* fontes forem disponibilizadas conforme permissão;
* usuário puder selecionar campos;
* aplicar filtros;
* selecionar período;
* ordenar;
* agrupar;
* realizar cálculos numéricos;
* visualizar prévia;
* salvar modelo;
* executar modelo salvo;
* exportar CSV;
* exportar XLSX;
* exportar PDF;
* exportar DOCX;
* imprimir;
* cabeçalho dos relatórios exibir o logo da O3Cloud;
* auditoria registrar execução;
* nenhuma query arbitrária for permitida;
* SQL usar parâmetros;
* dados sensíveis não forem expostos;
* nenhum módulo existente for quebrado;
* documentação e CHANGELOG forem atualizados.

---

# 42. Fora do Escopo da Primeira Versão

Não implementar agora:

* BI visual completo;
* dashboards drag-and-drop;
* gráficos customizáveis complexos;
* linguagem própria de fórmulas;
* SQL livre;
* relatórios agendados por e-mail;
* execução assíncrona de milhões de registros;
* integração direta com Power BI;
* criação de views pelo usuário;
* pivot table avançada.

Essas funcionalidades podem ser evoluções futuras.

---

# 43. Evoluções Futuras

A arquitetura deve permitir posteriormente:

* gráficos;
* dashboards;
* relatórios favoritos;
* agendamento;
* envio por e-mail;
* relatórios recorrentes;
* exportação assíncrona;
* compartilhamento por link interno;
* API de relatórios;
* integração com BI;
* comparativos de períodos;
* indicadores calculados;
* tabelas dinâmicas.

---

# 44. Sequência de Implementação Recomendada

Implementar nesta ordem:

### Etapa 1

Permissões e módulo base.

### Etapa 2

Catálogo de fontes e campos.

### Etapa 3

Engine de filtros e consulta segura.

### Etapa 4

Builder.

### Etapa 5

Resultados, paginação e cálculos.

### Etapa 6

Salvar modelos.

### Etapa 7

CSV e XLSX.

### Etapa 8

PDF, DOCX e impressão.

### Etapa 9

Auditoria.

### Etapa 10

Testes e documentação.

Não iniciar exportadores antes de a Engine estar homologada.

---

# 45. Regra de Desenvolvimento

Antes de implementar:

1. Ler arquitetura atual.
2. Ler sistema de usuários, perfis e permissões.
3. Identificar todas as permissões já existentes.
4. Mapear módulos disponíveis.
5. Identificar Services/Repositories que já oferecem consultas úteis.
6. Mapear convenções de UUID, soft delete, auditoria e paginação.
7. Apresentar proposta de migration.
8. Implementar um arquivo por vez.
9. Executar testes a cada etapa.
10. Não refatorar módulos existentes sem necessidade.

O módulo de Relatórios deve se integrar à arquitetura atual, e não exigir reestruturação do ERP.

___________________________________________________________________________________________________

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

---

# 46. Fechamento Tecnico - 10/08/2026

Status: Concluida tecnicamente.

Documento de fechamento: `docs/37-FECHAMENTO-SPRINT-20.md`.

Resumo:

* modulo Relatorios implementado com catalogo de fontes autorizadas;
* builder sem SQL livre;
* modelos salvos com visibilidade PRIVADO, PERFIL e GLOBAL;
* exportacoes CSV, XLSX, DOCX, PDF e impressao HTML;
* fila de jobs para geracao de relatorios;
* retencao de cache e sincronismos agendados em Configuracoes;
* DER, modelo fisico, visao geral e CHANGELOG atualizados.

A homologacao operacional permanece pendente de validacao assistida com usuarios, perfis e dados reais controlados.
