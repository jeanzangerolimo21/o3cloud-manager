# Abertura Sprint 16

Versao: 3.0 Alpha

Data de abertura: 03/08/2026

Status: Aberta

---

# Nome da Sprint

Sprint 16 - Governanca, Acessos e Operacao Assistida

---

# Contexto

A Sprint 15 foi concluida em 03/08/2026 com foco em infraestrutura operacional read-only.

Antes da abertura da Sprint 16, foi registrado o pacote `docs/26-MELHORIAS-PRE-SPRINT-16.md`, consolidando refinamentos de propostas, ClickSign, cofre de senhas, pipeline, rastreabilidade, configuracoes, e-mail e sidebar.

A Sprint 16 inicia com foco em organizar os proximos passos para uso assistido da plataforma, especialmente controle de acesso, auditoria, validacoes operacionais e refinamentos priorizados pela equipe.

---

# Objetivo Inicial

Preparar a plataforma para uso mais controlado na fase Beta assistida, evoluindo governanca, acesso, auditoria e validacoes operacionais sem comprometer a estabilidade das entregas ja homologadas.

---

# Escopo Inicial Candidato

## 1. Controle de Acesso e Perfis

Status: em planejamento

Objetivo:

- Definir perfis de usuario por area operacional.
- Restringir telas administrativas e integracoes tecnicas a usuarios autorizados.
- Preparar base para auditoria de acoes sensiveis.

## 2. Auditoria Operacional

Status: em planejamento

Objetivo:

- Registrar acoes relevantes executadas no sistema.
- Priorizar eventos de integracoes, configuracoes, cofre de senhas, contratos, propostas e implantacao.
- Evitar exposicao de segredos, tokens ou senhas em logs e historicos.

## 3. Validacao Assistida da Beta

Status: em planejamento

Objetivo:

- Criar roteiro de validacao por area: Comercial, Operacoes, Financeiro e Engenharia.
- Registrar pendencias encontradas durante uso assistido.
- Separar ajustes rapidos de itens que exigem sprint propria.

## 4. Refinamentos Operacionais Priorizados

Status: em planejamento

Objetivo:

- Enderecar ajustes de usabilidade identificados pela equipe.
- Priorizar correcoes que reduzam retrabalho operacional.
- Preservar estabilidade das rotas e fluxos ja validados.

---

# Fora do Escopo Inicial

- Automacoes destrutivas em infraestrutura.
- Alteracoes de producao em Proxmox, PBS, Zabbix ou TrueNAS sem aprovacao especifica.
- Refatoracoes amplas sem relacao direta com a Beta assistida.
- Carga financeira definitiva sem validacao oficial da equipe.

---

# Criterios de Aceite Iniciais

- Escopo final da Sprint 16 validado pela equipe.
- Telas administrativas sensiveis mapeadas para controle de acesso.
- Eventos auditaveis priorizados e documentados.
- Roteiro de validacao assistida definido.
- Qualquer implementacao seguir padrao Repository / Service / Routes / Templates.
- Validacoes tecnicas devem incluir `AST OK`, rotas principais via Flask test client e `git diff --check`.

---

# Documentos Relacionados

- `docs/25-FECHAMENTO-SPRINT-15.md`
- `docs/26-MELHORIAS-PRE-SPRINT-16.md`
- `docs/05-SPRINT_ATUAL`
- `docs/17-SPRINTS.md`
- `docs/ROADMAP.md`

---

# Encaminhamento

A Sprint 16 esta aberta em 03/08/2026.

O proximo passo e a equipe confirmar a prioridade entre controle de acesso/perfis, auditoria operacional, roteiro de validacao Beta ou novos refinamentos assistidos.
