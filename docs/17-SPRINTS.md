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

Concluida tecnicamente em 06/08/2026

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
