# O3Cloud Manager v3.0

# ROADMAP

Versão: 3.0 Alpha

Última atualização: Julho/2026

Status: Oficial

---

# Visão Geral

O O3Cloud Manager é o ERP interno da O3 Cloud.

Seu objetivo é centralizar toda a operação da empresa, desde o processo comercial até a operação técnica da infraestrutura em nuvem.

O desenvolvimento segue uma metodologia incremental baseada em Sprints, preservando a arquitetura oficial e a documentação do projeto.

---

# Status Geral do Projeto

| Área | Status |
|-------|--------|
| Arquitetura | ✅ Concluído |
| Estrutura Base | ✅ Concluído |
| Banco de Dados | ✅ Concluído |
| Componentes Compartilhados | ✅ Concluído |
| Módulo Ambientes | ✅ Concluído |
| Módulo Clientes | ✅ Concluído |
| Módulo Contratos | ✅ Concluído |
| Catálogo Técnico | 🚧 Em Desenvolvimento |
| CRM Comercial | ✅ Base Alpha concluída |
| Propostas | ✅ Base Alpha concluída |
| Implantação | ✅ Base Alpha concluída |
| Dashboard Executivo | ✅ Base Alpha concluída |

---

# Infraestrutura de Engenharia

## Documentação Oficial

### Arquitetura

- ✅ 03-ARQUITETURA.md
- ✅ 04-PADROES.md
- ✅ ENGINEERING_PRINCIPLES.md

### Processo

- ✅ 15-CHECKLIST.md
- ✅ 16-DEFINITION-OF-DONE.md
- ✅ AI_WORKFLOW.md

### Inteligência Artificial

- ✅ AGENTS.md
- ✅ PROJECT_CONTEXT.md
- ✅ DOMAIN_RULES.md

### Organização

- ✅ README.md

---

# Sprints Concluídas

## Sprint 1

- Estrutura inicial do projeto
- Flask
- MariaDB
- Layout Base

Status:

✅ Concluído

---

## Sprint 2

Módulo Ambientes

- CRUD completo
- Repository
- Service
- Routes
- Templates

Status:

✅ Concluído

---

## Sprint 3

Estrutura administrativa e evolução da arquitetura.

Status:

✅ Concluído

---

## Sprint 4

Clientes

- CRUD
- Integração OMIE
- Sincronização
- Bloqueios de edição
- Implantação

Status:

✅ Concluído

---

## Sprint 5

Contratos

- CRUD
- Integração OMIE
- Contratos
- Itens de Contrato

Status:

✅ Concluído

---

## Sprint 6.1

Catálogo Técnico

Fundação do módulo.

Status:

✅ Concluído

---

## Sprint 6.2

Estrutura do Catálogo.

Status:

✅ Concluído

---

## Sprint 6.3

Produtos

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

# Última Sprint Concluída

## Sprint 7

Status:

✅ Concluída

Objetivo:

Consolidar o CRM Comercial Alpha com propostas, contratos pós-assinatura e integração ClickSign.

Escopo entregue:

- ✅ Separação do bloco `CRM Comercial` no sidebar
- ✅ CRUD base de Leads, Contatos, Oportunidades e Propostas
- ✅ Pipeline Comercial inicial
- ✅ Contratos pós-assinatura com dashboard e vínculos comerciais
- ✅ Geração de contrato por modelo DOCX editável
- ✅ Envio real para ClickSign API v3
- ✅ Sincronização manual em lote de envelopes ClickSign
- ✅ Download do PDF assinado para `storage/contratos`

---

# Última Sprint Concluída

## Sprint 8

Consolidação Comercial e Pós-Assinatura

Status:

✅ Concluída na primeira entrega

Objetivos:

- Dashboard executivo/comercial
- Indicadores por parceiro e executivo
- Rastreabilidade proposta -> ClickSign -> contrato -> Omie
- Regras de acompanhamento pós-assinatura
- Evolução de permissões e auditoria

Primeira entrega concluída:

- ✅ Dashboard Comercial inicial em `/propostas/dashboard`

---

# Última Sprint Concluída

## Sprint 9

Implantação e Provisionamento

Status:

✅ Concluída em 27/07/2026

Objetivo:

Criar a fundação operacional do módulo de Implantação, conectando contratos encaminhados para projeto ao fluxo técnico de entrega, checklist, acompanhamento, rastreabilidade e preparação para provisionamento controlado.

Escopo entregue:

- Módulo próprio de Implantação com listagem, Kanban, visualização, edição e dashboard.
- Geração ou abertura de implantação a partir de contrato encaminhado para projeto.
- Workflow técnico com checklist, histórico, responsáveis, prazos e evidências.
- Kanban operacional com colunas administráveis e notificações tolerantes a SMTP ausente.
- Licenças O3Web, Faixas de Rede e Cofre de Senhas como bases operacionais.
- Cofre de Senhas com criptografia, auditoria e navegação por parceiro -> cliente -> credenciais.
- Rastreabilidade proposta -> contrato -> implantação.
- Base de configuração para Proxmox, PBS e Zabbix, sem automação destrutiva.

Documento de fechamento:

- `docs/19-FECHAMENTO-SPRINT-9.md`

---

# Última Sprint Encerrada

## Sprint 11

Integracoes e Melhorias Operacionais

Status:

⚠️ Parcialmente concluida em 29/07/2026

Objetivos entregues:

- Menu Financeiro e telas de preparacao para rentabilidade
- Produtos por Cliente
- Fluxos CSV para custos de produtos e faturamentos
- Pendencias documentadas para versao final

Documento de fechamento:

- `docs/21-FECHAMENTO-SPRINT-11.md`

---

## Sprint 12

Pendencias Operacionais e Preparacao da Versao Final

Status:

✅ Concluida em 29/07/2026

Entregas:

- Proposta opcional no fluxo operacional
- Contrato direto/parceiro como origem valida para implantacao
- Separacao de Integracoes de Negocio e Integracoes Tecnicas
- OMIE e ClickSign exibidos a partir do ambiente com segredos mascarados
- Anexos em comentarios de implantacao

Documento de fechamento:

- `docs/22-FECHAMENTO-SPRINT-12.md`

---

## Sprint 13

Decisao, Preparacao Operacional e Validacoes Nao Destrutivas

Status:

✅ Concluida em 29/07/2026

Entregas:

- Dados reais oficiais adiados para a fase Beta com a equipe, sem carga prematura na Sprint 13
- Cargas de custos, faturamentos e parametros financeiros condicionadas ao saneamento dos cadastros
- Preparacao pre-Beta priorizada antes de cargas reais ou configuracoes sistemicas definitivas

Documento de fechamento:

- `docs/23-FECHAMENTO-SPRINT-13.md`

---

# Sprint Atual

## Sprint 14

Consolidacao Pre-Beta e Preparacao de Validacao com a Equipe

Status:

🚧 Em planejamento

Objetivos:

- Cadastros e campos pendentes para Beta
- Diagnosticos de dados incompletos sem bloquear fluxos validos
- Checklist de validacao Beta por area
- Indicadores pre-Beta sem carga real oficial

---

## Sprint futura — Identidade e Controle de Acesso com FreeIPA

**Objetivo:** integrar o O3Cloud Manager ao FreeIPA para autenticação centralizada, sincronização de usuários e grupos, gerenciamento de hosts Linux, políticas HBAC, regras sudo e automação de acessos durante o provisionamento Proxmox.

### Fases previstas

1. Laboratório e arquitetura FreeIPA.
2. Login do O3Cloud Manager via FreeIPA.
3. Sincronização de usuários e grupos.
4. Interface administrativa de identidade.
5. Integração de hosts Linux.
6. Gerenciamento de HBAC e sudo.
7. Integração com provisionamento Proxmox e cloud-init.
8. Alta disponibilidade, backup e Disaster Recovery.

### Regras de arquitetura

- O FreeIPA será executado separadamente.
- O O3Cloud Manager não armazenará senhas do FreeIPA.
- Os grupos FreeIPA serão mapeados para perfis internos configuráveis.
- Todas as ações deverão gerar auditoria.
- As tabelas somente serão criadas após aprovação do diagrama funcional.
- O módulo deverá respeitar o Architecture Freeze.

# Objetivos Estratégicos

Ao final do desenvolvimento o O3Cloud Manager deverá controlar:

- CRM
- Comercial
- Clientes
- Contratos
- Catálogo Técnico
- Dimensionamento
- Precificação
- Propostas
- ClickSign
- Implantação
- Infraestrutura
- Monitoramento
- Financeiro
- Dashboards
- Indicadores Executivos
- Gerenciamento de acessos e usuarios integrados com FreeIPA

---

# Diretrizes do Projeto

Todo desenvolvimento deverá seguir obrigatoriamente:

- Architecture Freeze
- AGENTS.md
- PROJECT_CONTEXT.md
- DOMAIN_RULES.md
- AI_WORKFLOW.md
- 03-ARQUITETURA.md
- 04-PADROES.md
- 15-CHECKLIST.md
- 16-DEFINITION-OF-DONE.md

---

# Situação Atual

Versão:

3.0 Alpha

Sprint:

10 em andamento

Status Geral:

🚧 Desenvolvimento Ativo

Próxima Entrega:

Dashboard Executivo com filtros executivos por período, parceiro, executivo e status.



