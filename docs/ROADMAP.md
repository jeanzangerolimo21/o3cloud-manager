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
| Implantação | 🚧 Em Desenvolvimento |
| Dashboard Executivo | ⏳ Planejado |

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

# Sprint Atual

## Sprint 9

Implantação e Provisionamento

Status:

🚧 Em andamento

Objetivo:

Criar a fundação operacional do módulo de Implantação, conectando contratos encaminhados para projeto ao fluxo técnico de entrega, checklist, acompanhamento e preparação para provisionamento.

Escopo revisado:

- Módulo próprio de Implantação com listagem, Kanban, visualização e edição controlada.
- Geração ou abertura de implantação a partir de contrato encaminhado para projeto, com entrada automática na coluna Fila quando sincronizado do Omie.
- Workflow de implantação: Aguardando início, Em planejamento, Em execução, Em validação, Entregue, Pausada e Cancelada.
- Checklist técnico por implantação, com itens obrigatórios, responsáveis, status e evidências.
- Vínculo com cliente, contrato, proposta, executivo, parceiro e ambiente técnico.
- Visão de acompanhamento por status, responsável, etapa Kanban e prazo.
- Notificação de movimentação de etapa para implantador, executivo, parceiro e contatos envolvidos.
- Preparação para provisionamento rastreável usando catálogo técnico, modelos e recursos.
- Integração Proxmox apenas como etapa controlada, inicialmente preparada por configuração e rastreabilidade, sem automação destrutiva.

Primeira entrega concluída:

- ✅ Fundação do domínio `implantacao`: migration, repository, service, routes, templates, sidebar, listagem, criação, visualização e dashboard inicial.
- ✅ Kanban operacional de implantação com sincronização automática de contratos encaminhados para projeto e notificação de mudança de coluna.

Critérios de aceite:

- Nenhuma implantação pode iniciar sem contrato encaminhado para projeto.
- Toda implantação deve manter vínculo com cliente e contrato.
- Checklist deve ser rastreável e persistido no banco.
- Contrato encaminhado para projeto deve entrar na primeira fila do Kanban de implantação.
- Movimentação de Kanban deve registrar etapa e acionar notificação por e-mail quando SMTP estiver configurado.
- Provisionamento deve registrar intenção/planejamento antes de qualquer integração Proxmox real.

---

## Sprint 10

Dashboard Executivo

Objetivos:

- Indicadores
- Rentabilidade
- Custos
- Comercial
- Infraestrutura

---

## Sprint 11

Integrações

Objetivos:

- NetBox
- PBS
- Automações
- Melhorias Operacionais

---

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

9 em andamento

Status Geral:

🚧 Desenvolvimento Ativo

Próxima Entrega:

Ação direta em Contratos para iniciar implantação e rastreabilidade proposta -> contrato -> implantação.



