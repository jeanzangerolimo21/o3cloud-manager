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

## 2026-07-28 - Vinculos Omie no Catalogo

### Sprint 11

- Criado seed idempotente `database/seed/004_catalogo_vinculos_omie_sprint11.sql` para cadastrar/vincular 7 codigos de servico Omie ao catalogo.
- Corrigido o join de produtos no dashboard para converter apenas codigos numericos, evitando vinculos falsos com codigo Omie `0`.
- Cobertura de catalogo validada em 256 de 257 itens; custos continuam pendentes porque ainda nao ha fonte oficial validada para `valor_custo`.

---

## 2026-07-28 - Fila de Saneamento de Catalogo e Custos

### Sprint 11

- Dashboard Produtos por Cliente passou a listar os principais itens Omie sem vinculo com catalogo.
- Adicionada lista de produtos ja vinculados a contratos, mas ainda sem custo preenchido.
- Proxima acao operacional ficou direcionada para cadastrar codigos Omie e completar custos antes da rentabilidade.

---

## 2026-07-28 - Inicio da Sprint 11 com Produtos por Cliente

### Sprint 11

- Criada tela `/dashboard/produtos-clientes` para mapear cliente -> contrato -> item contratado.
- Diagnostico inicial usa itens sincronizados de contratos Omie e evidencia lacunas de proposta, catalogo e custo.
- Visao Geral passou a destacar Produtos por Cliente como primeira entrega operacional da Sprint 11.

---

## 2026-07-28 - Visao Geral Atualizada para Sprint 11

### Dashboard

- Visao Geral passou a indicar Sprint 11 como etapa atual de integracoes e melhorias operacionais.
- Dashboard Executivo passou a indicar Sprint 10 como concluida e base de diagnostico para a Sprint 11.

---

## 2026-07-28 - Fechamento da Sprint 10

### Documentacao

- Sprint 10 marcada como concluida oficialmente em 28/07/2026.
- Criado documento `docs/20-FECHAMENTO-SPRINT-10.md` consolidando entregas, regras, validacoes, diagnosticos e pendencias.
- Documento `docs/05-SPRINT_ATUAL` preparado para a Sprint 11 - Integracoes e Melhorias Operacionais.
- Roadmap e historico de sprints atualizados para refletir Dashboard Executivo como Base Alpha concluida.

---

## 2026-07-28 - Rastreabilidade Executiva no Dashboard

### Dashboard Executivo

- Adicionada visao de rastreabilidade proposta -> contrato -> implantacao.
- Dashboard passou a exibir cobertura ponta a ponta, contratos sem proposta e contratos sem implantacao.
- Fluxos operacionais exibem links diretos para proposta, contrato e implantacao quando houver vinculo.

---

## 2026-07-28 - Carga por Responsavel no Dashboard Executivo

### Dashboard Executivo

- Adicionada visao de carga por responsavel/implantador com projetos totais, andamento, atrasos e vencimentos em 7 dias.
- Carga operacional passou a exibir checklist medio e receita mensal vinculada aos contratos de implantacao.
- Visao respeita os filtros executivos aplicados no Dashboard Executivo.

---

## 2026-07-28 - Base Inicial de Rentabilidade e Custos

### Dashboard Executivo

- Adicionada seção de base para rentabilidade com receita recorrente, setup/projeto e cobertura de rastreabilidade.
- Dashboard passou a mapear prontidão das fontes de dados: contratos, faturamentos, produtos/custos, parâmetros financeiros e infraestrutura.
- Adicionada lista de contratos candidatos para cálculo futuro de rentabilidade, sem cálculo definitivo de margem enquanto custos não estiverem validados.

---

## 2026-07-28 - Evolucao Mensal no Dashboard Executivo

### Dashboard Executivo

- Adicionado comparativo mensal para propostas, receita mensal ativa e volume operacional.
- Evolucao mensal passou a respeitar filtros executivos de periodo, parceiro, executivo e status.
- Periodo padrao exibe os ultimos 6 meses; intervalos maiores ficam limitados aos ultimos 12 meses para manter leitura gerencial.

---

## 2026-07-28 - Drill-down Filtrado no Dashboard Executivo

### Dashboard Executivo

- Links do Dashboard Executivo passaram a preservar filtros compatíveis ao abrir Propostas, Contratos e Implantação.
- Atalhos de pendências críticas, contratos a iniciar e assinaturas pendentes passaram a apontar para listagens operacionais já filtradas.
- Corrigido endpoint do link de contratos a iniciar para usar a rota real `contratos.view`.

---

## 2026-07-27 - Filtros Executivos do Dashboard

### Dashboard Executivo

- Adicionados filtros executivos em `/dashboard/executivo` por período, parceiro, executivo, status comercial, status de contrato e status de implantação.
- Consultas agregadas do Dashboard Executivo passaram a aplicar os filtros nos blocos de propostas, contratos e implantação.
- Rankings por executivo/parceiro e listas de atenção passaram a respeitar os recortes selecionados.
- Selects de parceiro e executivo são carregados a partir dos registros ativos da base local.

---

## 2026-07-27 - Dashboard Executivo Dedicado

### Dashboard Executivo

- Criada rota `/dashboard/executivo` para concentrar a visão gerencial de diretoria.
- Home `/` passou a ser uma visão geral resumida com cards principais, status da Sprint 10 e atalhos.
- Menu lateral passou a separar `Visão Geral` e `Dashboard Executivo`.
- Tela executiva mantém indicadores comerciais, contratos, implantação, rankings e listas de atenção.

---

## 2026-07-27 - Início da Sprint 10

### Dashboard Executivo

- Sprint 10 marcada como iniciada para evoluir o Dashboard Executivo.
- Home `/` convertida em painel executivo com dados reais de propostas, contratos e implantação.
- Adicionados cards de receita mensal negociada, receita mensal ativa, implantações em andamento e pendências críticas.
- Adicionados agrupamentos por status comercial, status de contratos, status de implantação, executivo e parceiro.
- Adicionadas listas de atenção para implantações críticas, contratos a iniciar e assinaturas pendentes.
- Atalhos de drill-down conectam o dashboard aos módulos de Propostas, Contratos, Implantação e Kanban.

---

## 2026-07-27 - Fechamento da Sprint 9

### Documentação

- Sprint 9 marcada como concluída oficialmente em 27/07/2026.
- Criado documento `docs/19-FECHAMENTO-SPRINT-9.md` consolidando objetivo, entregas, migrations, regras, validações e pendências encaminhadas.
- Documento `docs/05-SPRINT_ATUAL` preparado para a Sprint 10 - Dashboard Executivo.
- Roadmap e histórico de sprints atualizados para refletir Implantação como Base Alpha concluída e Dashboard Executivo como próxima frente.

---

## 2026-07-27 - Navegação por Pastas no Cofre de Senhas

### Implantação e Provisionamento

- Tela principal do Cofre de Senhas reorganizada em navegação visual por parceiro e pastas de clientes.
- Seleção de parceiro passou a exibir apenas as pastas de clientes vinculadas a ele; credenciais aparecem somente após abrir a pasta do cliente.
- Formulário de pasta de cliente passou a exigir e gravar parceiro, evitando pastas fora da navegação hierárquica.
- Ações de revelar, copiar, editar e inativar credenciais foram preservadas dentro da pasta selecionada.

---

## 2026-07-27 - Base de Integrações Técnicas

### Implantação e Provisionamento

- Adicionada migration 031 para configuração base de integrações Proxmox, PBS e Zabbix.
- Criada tela /implantacao/integracoes para cadastrar, editar, inativar e validar configurações técnicas.
- Tokens e senhas das integrações passaram a ser armazenados criptografados usando a política do cofre.
- Validação desta etapa é estrutural e não executa chamadas externas ou ações destrutivas.
- Adicionado atalho Integrações Técnicas no menu Operações.

---

## 2026-07-27 - Colunas Administrativas do Kanban

### Implantação e Provisionamento

- Adicionada migration 030 para configurar colunas do Kanban de Implantação.
- Criada tela administrativa /implantacao/kanban/colunas para criar, ordenar, renomear, ativar e inativar colunas.
- Kanban, formulário de implantação e notificações passaram a usar as colunas configuradas na base.
- Colunas essenciais FILA, FINALIZADO e CANCELADOS ficam protegidas contra inativação.
- Colunas com cards ativos não podem ser inativadas para evitar perda visual de implantações em andamento.

---

## 2026-07-27 - Rastreabilidade Comercial para Implantação

### Implantação e Provisionamento

- Criada visão compartilhada de rastreabilidade proposta -> contrato -> implantação.
- Telas de Proposta, Contrato e Implantação passaram a exibir atalhos e status do fluxo ponta a ponta.
- Rastreabilidade exibe ClickSign, contrato Omie/manual, etapa Kanban, responsável, prazo e progresso do checklist quando disponíveis.
- Consulta tolera vínculos incompletos, mantendo visibilidade de propostas sem contrato e contratos sem implantação.

---

## 2026-07-27 - Checklist de Implantação Evoluído

### Implantação e Provisionamento

- Checklist de Implantação passou a permitir inclusão manual de itens por projeto.
- Adicionados modelos operacionais de checklist para implantação padrão, Licenças O3Web e Infraestrutura/VPN.
- Aplicação de modelo evita duplicar itens já existentes na implantação.
- Itens do checklist podem ser removidos, com recálculo automático do percentual de conclusão.

---

## 2026-07-27 - Dashboard de Implantação Refinado

### Implantação e Provisionamento

- Dashboard de Implantação passou a aplicar filtros reais por status, responsável, prazo e situação.
- Adicionados indicadores de projetos atrasados, vencendo em 7 dias, vencendo em 30 dias e sem prazo.
- Adicionadas visões resumidas por status e por responsável, respeitando os filtros aplicados.
- Listagem passou a sinalizar prazo atrasado, vencimento próximo e ausência de prazo.

---

## 2026-07-22 - Dashboard Principal da Sprint 9

### Implantação e Provisionamento

- Dashboard Executivo passou a informar que a Sprint 9 está em implantação.
- Adicionado resumo das entregas recentes de Implantação e das pendências principais da Sprint 9.
- Atalho do card principal passa a direcionar para o módulo de Implantação.

---

## 2026-07-22 - Ação Direta Contrato para Implantação

### Implantação e Provisionamento

- Adicionada ação direta em Contratos para iniciar implantação quando o contrato está `ENCAMINHADO_PROJETO`.
- Contratos que já possuem implantação ativa passam a exibir atalho para abrir a implantação existente, sem criar duplicidade.

---

## 2026-07-22 - Cofre de Senhas de Implantação

### Implantação e Provisionamento

- Adicionada migration `028_create_implantacao_cofre_senhas.sql` para armazenar credenciais criptografadas e auditoria de ações.
- Criada tela `Cofre de Senhas` em Implantação com listagem, filtros, cadastro, edição, inativação e revelação controlada de senha.
- Credenciais passaram a vincular cliente, faixa de rede e opcionalmente licença O3Web, com campos futuros para Proxmox, PBS e Zabbix.
- Revelação de senha é feita sob demanda pela interface e registrada em auditoria com usuário e IP de origem quando disponíveis.
- Adicionados botões para copiar senha, usuário, URL e Host/IP na tela do Cofre de Senhas.
- Adicionado gerador local de senha complexa no formulário do Cofre, com política padrão preparada para futura tela de Configurações.
- Formulário do Cofre passa a importar a URL salva em Licenças O3Web quando uma licença é vinculada, deixando o campo editável quando não há vínculo.
- Adicionada migration `029_create_implantacao_cofre_pastas.sql` com pastas do cofre por parceiro, cliente ou usuário logado.
- Tela principal do Cofre passou a permitir criação, edição, seleção e filtro por pastas, com metadados de dono e compartilhamento preparados para futura política de acesso.

---

## 2026-07-22 - Gerenciamento de Faixas de Rede

### Implantação e Provisionamento

- Adicionada migration `026_create_implantacao_faixas_rede.sql` para controle de faixas de rede por cliente.
- Criada tela `Faixas de Rede` em Implantação com listagem, filtros, cadastro, edição, inativação e vínculo com cliente sincronizado do Omie.
- Adicionado cálculo da próxima faixa disponível dentro de uma rede base, escolhendo máscara `/29`, `/28` ou `/27` conforme a quantidade de servidores.
- Cadastro de faixa registra `Rede`, `FW - WAN`, `FW - LAN`, `Cliente`, `VPN`, range de `Portas`, `PVE` e `Observações`.
- Adicionada migration `027_add_port_range_implantacao_faixas_rede.sql` para estruturar `porta_inicio` e `porta_fim`.
- Cadastro de Faixas de Rede bloqueia conflito de range de portas quando o `FW - WAN` é o mesmo em outro cadastro ativo.

---

## 2026-07-22 - Vínculo de Licenças O3Web com Clientes

### Implantação e Provisionamento

- Adicionada migration `025_add_cliente_vinculo_o3web_licencas.sql` com vínculo opcional entre licenças O3Web e clientes cadastrados.
- Cadastro manual de Licenças O3Web passou a selecionar cliente ativo da base de clientes e preencher CNPJ automaticamente.
- Listagem de Licenças O3Web passou a exibir o CNPJ vinculado ao cliente quando disponível.
- Tela de Licenças O3Web passou a exibir paginação quando houver mais de 50 registros, preservando filtros aplicados.
- Adicionado filtro de validade para listar licenças O3Web vencidas ou vigentes.
- Adicionado alerta na tela de Licenças O3Web quando houver licenças vencidas ativas, com atalho para a listagem filtrada.
- Importação CSV permanece compatível com cliente em texto e passa a aceitar CNPJ quando presente.

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
