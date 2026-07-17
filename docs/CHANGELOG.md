# Changelog

## v2.0.0-alpha

Data:
Junho/2026

### Arquitetura

- Novo modelo por domínios
- Separação Repository / Service
- Estrutura modular

### Banco

- Novo domínio Financeiro
- Produtos
- Contratos
- Faturamentos
- Licenciamento
- Configurações
- Controle de Migrations

### Infraestrutura

- Ubuntu Server 24.04
- MariaDB
- GitHub
- Branch Develop

### Próxima versão

- Dashboard
- Flask
- Bootstrap 5
- Integração OMIE
- Integração Proxmox

# O3Cloud Manager v3.0

# CHANGELOG

Todas as mudanças importantes deste projeto serão registradas neste documento.

O formato é baseado no Keep a Changelog e adaptado às necessidades do O3Cloud Manager.

---

# [3.0 Alpha] - Julho/2026

## Situação

🚧 Desenvolvimento Ativo

---

## Adicionado

### Arquitetura

- Definição oficial da arquitetura Repository → Service → Routes → Templates.
- Criação do BaseRepository.
- Padronização do acesso ao banco utilizando SQL puro.
- Implementação de UUID automático.
- Implementação de Soft Delete.
- Padronização do fluxo de desenvolvimento.

---

### Componentes Compartilhados

Criados:

- page_header.html
- filter_bar.html
- crud_actions.html
- alert.html

Templates Base:

- index_base.html
- form_base.html
- view_base.html

Todos homologados.

---

### Módulo Ambientes

Concluído:

- CRUD completo.
- Repository.
- Service.
- Routes.
- Templates.

---

### Módulo Clientes

Concluído:

- CRUD completo.
- Integração OMIE.
- Sincronização.
- Controle de origem.
- Bloqueio de edição para clientes sincronizados.
- Serviço de implantação.

---

### Módulo Contratos

Concluído:

- CRUD.
- Integração OMIE.
- Estrutura de contratos.
- Itens de contrato.
- Repository.
- Service.
- Routes.

---

### Catálogo Técnico

#### Categorias

Concluído:

- CRUD completo.
- Repository.
- Service.
- Routes.
- Templates.

#### Produtos

Concluído:

- CRUD completo.
- Repository.
- Service.
- Routes.
- Templates.

#### Modelos

Concluído:

- CRUD completo.
- Repository.
- Service.
- Routes.
- Templates.
- Acesso direto pela home do Catálogo Comercial.

#### Faixas

Concluído:

- CRUD completo.
- Repository.
- Service.
- Routes.
- Templates.
- Atalho de gestão e criação pela home do Catálogo Comercial.

---

### BaseRepository

Adicionado:

- generate_uuid()
- bool_to_int()

Padronização dos repositories.

---

### Documentação

Criados:

- PROJETO.md
- ROADMAP.md
- 03-ARQUITETURA.md
- 04-PADROES.md
- 05-SPRINT-ATUAL.md
- ENGINEERING_PRINCIPLES.md
- AGENTS.md
- PROJECT_CONTEXT.md
- DOMAIN_RULES.md
- AI_WORKFLOW.md
- 15-CHECKLIST.md
- 16-DEFINITION-OF-DONE.md
- README.md

---

## Alterado

### Arquitetura

Padronização completa da estrutura dos módulos.

Todos os CRUDs passam a seguir:

Repository

↓

Service

↓

Routes

↓

Templates

---

### Desenvolvimento

Definida metodologia oficial:

- Um arquivo por vez.
- Arquivo completo.
- Testes.
- Homologação.
- Atualização da documentação.
- Commit.
- Próxima tarefa.

---

### Inteligência Artificial

Documentação estruturada para suportar:

- OpenAI Codex
- ChatGPT
- Claude Code
- Gemini CLI
- Cursor AI
- GitHub Copilot

---

## Corrigido

### Categorias

- Ajustes nas validações.
- Melhorias no fluxo de ativação e desativação.
- Padronização das mensagens.
- Padronização do Repository.

---

### Produtos

- Padronização do Repository.
- Padronização do Service.
- Ajustes nas rotas.
- Adequação à arquitetura oficial.

### Catálogo Comercial

- Ajustada a home do catálogo para remover duplicação de navegação.
- Adicionados atalhos diretos para Modelos e Faixas.
- Corrigida a contabilização de Categorias, Modelos e Faixas na visão geral.

### Importação do Catálogo

- A tela `Importar Catálogo` passou a exibir um modelo visual de CSV com exemplos de licenciamento e recursos de servidor.
- A interface deixou de referenciar exclusivamente o Base44 e passou a orientar a importação de qualquer arquivo CSV aderente ao formato esperado.
- O fluxo ficou mais claro para validação do cabeçalho e preenchimento dos campos antes da importação.

### CRM Comercial

- O sidebar passou a exibir um separador exclusivo para o módulo `CRM Comercial`.
- O módulo `Leads` foi iniciado com listagem, cadastro, edição, visualização e exclusão.
- O módulo `Contatos` foi iniciado com CRUD base e vínculos opcionais com lead, parceiro e executivo.
- O módulo `Oportunidades` foi iniciado com negociações ativas, estimativa financeira e probabilidade de fechamento.
- O `Pipeline Comercial` foi iniciado com uma visão visual do funil baseada nos status das oportunidades.
- O módulo `Propostas` foi iniciado com versionamento por oportunidade, validade, valor total e anexo opcional.
- A migration `010_create_crm_leads.sql` foi criada e aplicada no banco com vínculos opcionais para parceiros e executivos.
- A migration `011_create_crm_contatos.sql` foi criada para suportar a agenda comercial do CRM.
- A migration `012_create_crm_oportunidades.sql` foi criada para suportar a etapa de negociação ativa do funil comercial.
- A home passou a destacar visualmente o início do CRM com atalho direto para Leads.

---

## Segurança

Implementado:

- Soft Delete.
- UUID obrigatório.
- Prepared Statements.
- Separação entre Repository, Service e Routes.

---

## Próxima Versão

### Sprint 7

Em desenvolvimento.

Objetivos:

- CRM Comercial
- Leads
- Contatos
- Oportunidades
- Pipeline Comercial
- ClickSign

---

## Roadmap Futuro

Sprint 7

- CRM Comercial
- Leads
- Oportunidades
- Pipeline
- ClickSign

Sprint 8

- Propostas
- Precificação
- Versionamento
- PDF

Sprint 9

- Implantação
- Workflow
- Provisionamento

Sprint 10

- Dashboard Executivo

Sprint 11

- Integrações Avançadas
- NetBox
- PBS

---

## Observações

Este projeto segue a documentação oficial localizada em:

/docs

Toda implementação deverá obedecer:

- AGENTS.md
- PROJECT_CONTEXT.md
- DOMAIN_RULES.md
- AI_WORKFLOW.md
- 03-ARQUITETURA.md
- 04-PADROES.md
- ROADMAP.md
- 05-SPRINT-ATUAL.md
- ENGINEERING_PRINCIPLES.md
- 15-CHECKLIST.md
- 16-DEFINITION-OF-DONE.md

---

## Status Atual

Versão:

3.0 Alpha

Sprint:

6.4

Situação:

🚧 Desenvolvimento Ativo

Próxima Implementação:

Homologação de Servidores e consolidação da base de Dimensionamento.
