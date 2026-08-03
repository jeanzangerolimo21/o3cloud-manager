# O3Cloud Manager v3.0

# 17 - SPRINTS

Versão: 3.0 Alpha

Última atualização: 03/08/2026

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


# Sprint Atual

## Sprint 16

Governanca, Acessos e Operacao Assistida

Inicio registrado em 03/08/2026.

Documento de abertura:

- `docs/27-ABERTURA-SPRINT-16.md`

Objetivos iniciais:

- Definir controle de acesso e perfis por area operacional.
- Mapear telas administrativas e integracoes tecnicas para restricao por permissao.
- Priorizar auditoria operacional para acoes sensiveis.
- Criar roteiro de validacao assistida da Beta por area.
- Enderecar refinamentos operacionais priorizados pela equipe.

Status:

Aberta em 03/08/2026

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
