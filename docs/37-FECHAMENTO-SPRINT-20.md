# O3Cloud Manager v3.0

# Fechamento Sprint 20

Modulo de Relatorios Customizaveis

Data de fechamento tecnico: 10/08/2026

Status: Concluida tecnicamente

---

# Entregas Consolidadas

- Modulo `Relatorios` criado com fontes autorizadas e catalogo de campos.
- Builder sem SQL livre, com selecao de campos, filtros, periodo, ordenacao, agrupamentos e agregacoes.
- Modelos salvos com visibilidade PRIVADO, PERFIL e GLOBAL.
- Execucoes registradas em `relatorios_execucoes`.
- Exportacoes CSV, XLSX, DOCX e PDF, alem de impressao HTML.
- Cabecalho/identificacao O3Cloud aplicado nos formatos suportados.
- Protecoes de carga com previa limitada, exportacao controlada e exigencia de periodo para fontes grandes.
- Fila de relatorios em segundo plano por `relatorios_jobs`, com arquivos em `storage/relatorios`.
- Comando CLI `flask relatorios-processar-jobs`.
- Fontes de infraestrutura adicionadas a partir de caches locais: Zabbix, PBS, TrueNAS, Proxmox VMs/Containers e Proxmox Nodes.
- Tela Configuracoes > Retencao de Cache com politicas, limpeza e historico.
- Tela Configuracoes > Automacoes de Sincronismo com agendamentos para Omie, Zabbix, Proxmox, ClickSign, PBS e TrueNAS.
- Comando CLI `flask sincronismos-processar-agendados`.
- Cadastro manual de participantes de eventos liberado por permissao especifica para ADMIN.

---

# Migrations

- `077_create_relatorios_customizaveis.sql`
- `078_create_relatorios_jobs.sql`
- `079_create_config_cache_retencao.sql`
- `080_create_config_sincronismos_agendados.sql`
- `081_permissao_eventos_participante_manual.sql`

Todas foram registradas como aplicadas no banco local em 10/08/2026 conforme CHANGELOG.

---

# Documentacao Atualizada

- `docs/00-VISAO-GERAL.md`
- `docs/05-SPRINT_ATUAL`
- `docs/12-DER.md`
- `docs/13-MODELO-FISICO-DADOS.md`
- `docs/17-SPRINTS.md`
- `docs/CHANGELOG.md`

---

# Pendencias para Homologacao

- Validar acessos de Administrador, Diretoria e Administrativo_Gestor.
- Validar usuario sem permissao tentando acessar rotas diretas de Relatorios.
- Validar filtros por texto, numero, moeda, data, status e booleano.
- Validar agrupamentos e agregacoes em fontes financeiras, comerciais e administrativas.
- Validar exportacoes CSV, XLSX, DOCX, PDF e impressao com dados reais controlados.
- Validar processamento de jobs fora da request HTTP.
- Validar envio de e-mail de conclusao quando SMTP estiver homologado.
- Validar retencao de cache e sincronismos agendados com janela operacional aprovada.

---

# Decisao de Fechamento

O Sprint 20 esta concluido tecnicamente em 10/08/2026.

A entrega atende ao escopo funcional planejado para a primeira versao de Relatorios Customizaveis e fica encaminhada para homologacao operacional na release Beta. SQL livre, BI visual completo, dashboards drag-and-drop, pivot table avancado e automacoes destrutivas permanecem fora do escopo.
