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

## 2026-07-21 - Licenças O3Web

### Implantação e Provisionamento

- Adicionada migration `024_create_o3web_licencas.sql` para gestão operacional de licenças O3Web.
- Criada tela `/implantacao/licencas-o3web` com dashboard, filtros, cadastro manual, edição e inativação de licenças.
- Criado importador CSV para campos atuais da planilha de licenças, incluindo chave de ativação, ID licença, tipo, backup, dias, usuários, edição, datas, cliente, URLs, comments e observação.
- Importação atualiza registros por `ID Licença` quando disponível e preserva datas originais quando o formato não puder ser normalizado.

---

## 2026-07-21 - Histórico de Implantação

### Implantação e Provisionamento

- Adicionada migration `023_add_implantacao_historico_emails.sql` com histórico de implantação e e-mails adicionais.
- Edição da implantação passou a permitir alteração direta da etapa do Kanban.
- Visualização da implantação passou a exibir histórico com data/hora, autor, comentário e status de envio de e-mail.
- Comentários do histórico passaram a ter ações de editar e excluir, mantendo mudanças de etapa como auditoria somente leitura.
- Comentários podem ser registrados e opcionalmente enviados por e-mail aos envolvidos do projeto.
- E-mails adicionais podem ser cadastrados na implantação para compor as notificações do projeto.

---

## 2026-07-21 - Kanban de Implantação

### Implantação e Provisionamento

- Adicionada migration `022_add_kanban_implantacao.sql` com etapa Kanban e dados de implantador.
- Criada tela `/implantacao/kanban` com colunas operacionais de projeto e movimentação por arrastar e soltar.
- Contratos `ENCAMINHADO_PROJETO` passaram a cair automaticamente na coluna `Fila` como implantação editável.
- Movimentação de coluna passou a notificar implantador, executivo, parceiro e contatos envolvidos quando SMTP estiver configurado.
- Formulário de implantação passou a salvar implantador e e-mail do implantador.
- Implantação criada a partir do Kanban passou a preencher início previsto em 7 dias corridos e entrega prevista 30 dias depois.

---

## 2026-07-21 - Início Sprint 9

### Implantação e Provisionamento

- Sprint 9 iniciada com a fundação do módulo próprio de Implantação.
- Adicionada migration `021_create_implantacao_workflow.sql` com tabelas `implantacoes` e `implantacao_checklist`.
- Adicionados repository, service, routes e templates para listagem, criação, visualização, edição e dashboard inicial de implantações.
- Criação de implantação passou a exigir contrato encaminhado para projeto e gerar checklist técnico padrão.
- Tela de Nova Implantação passou a preencher título e contexto operacional ao selecionar contrato, sem exibir valores de negociação.
- Adicionada visualização operacional do contrato para implantação, omitindo valores comerciais/financeiros.
- Provisionamento foi registrado como etapa planejada/rastreável, sem integração Proxmox automática nesta primeira entrega.

---

## 2026-07-21 - Revisão Sprint 9

### Implantação e Provisionamento

- Sprint 9 revisada para início com foco em módulo próprio de Implantação.
- Escopo definido para workflow pós-contrato encaminhado para projeto, checklist técnico, acompanhamento e preparação de provisionamento.
- Integração Proxmox posicionada como etapa controlada e auditável, sem automação destrutiva na primeira entrega.

---

## 2026-07-21 - Início Sprint 8

### Dashboard Comercial

- Sprint 8 iniciada com foco em consolidação comercial e pós-assinatura.
- Adicionado Dashboard Comercial em `/propostas/dashboard`.
- Dashboard passou a exibir totais de propostas, receita mensal negociada, implantação, propostas em assinatura, assinadas e concluídas.
- Adicionados agrupamentos por executivo, parceiro, status comercial e status ClickSign.
- Adicionados atalhos para o Dashboard Comercial no menu lateral e na listagem de Propostas.

---

## 2026-07-20 - Fechamento Sprint 7

### CRM, Propostas e Contratos

- Sprint 7 concluída com CRM Comercial Alpha, Propostas, Contratos pós-assinatura e integração ClickSign.
- Propostas passaram a gerar contrato a partir de modelo DOCX editável e visualizar PDF antes do envio.
- Contratos passaram a aceitar vínculos com contato, proposta, parceiro e executivo, com edição restrita para contratos Omie.
- Dashboard de Contratos passou a somar valores conforme filtro de status selecionado e agrupar por executivo/parceiro.
- Quantidade de usuários deixou de ser obrigatória em contratos manuais.
- Contratos manuais podem ser excluídos logicamente.

### ClickSign

- Adicionado client real da API ClickSign v3.
- Envio real de contratos para ClickSign com contato do cliente, representante O3 Cloud e executivo como testemunha.
- Adicionado botão `Sincronizar ClickSign` na tela principal de Propostas para sincronização manual em lote.
- Sincronização interpreta `running` como `Aguardando Assinaturas` e `closed` como `Assinado`.
- PDF assinado é baixado da ClickSign e salvo em `storage/contratos`.

### Banco de Dados

- Adicionadas migrations `017`, `018`, `019` e `020` para ClickSign, contratos pós-assinatura, vínculos comerciais e CPF opcional de contatos.

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
- Menu próprio de Contratos.
- Dashboard pós-assinatura com totais por recorrência, setup, usuários, executivo e parceiro.
- Formulário de novo contrato vinculado ao CNPJ do cliente.
- Bloqueio de edição para contratos sincronizados do Omie.
- Upload e download de contrato PDF assinado em `storage/contratos`.

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
