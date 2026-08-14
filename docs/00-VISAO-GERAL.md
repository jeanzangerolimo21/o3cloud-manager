# Visão Geral

## Objetivo

Missão do O3Cloud Manager

Transformar dados operacionais, financeiros e de infraestrutura em informações gerenciais para apoiar a tomada de decisão da Diretoria da O3Cloud.---

---

# Objetivos

* Eliminar controles manuais.
* Automatizar integrações.
* Consolidar custos.
* Calcular rentabilidade.
* Facilitar tomada de decisão.
* Gerar indicadores executivos.
* Integrar infraestrutura e financeiro.

---


---

# Status Atual do Desenvolvimento

Ultima sprint encerrada: Sprint 17 - Comissoes, Premiacoes, ASO, Receita por Servidor e Seguranca de Autenticacao.

Proxima etapa: Sprint Final - Homologacao Beta e fechamento da versao.

Data de fechamento tecnico da Sprint 21: 12/08/2026.

Data de retomada do Sprint 17: 12/08/2026.

Data de fechamento tecnico do Sprint 17: 14/08/2026.

Status atual:

- Sprint 18 concluida tecnicamente em 06/08/2026, com validacao assistida encaminhada para a release Beta.
- Sprint 19 implementada em 10/08/2026 com controle de inadimplencia financeira e bloqueios operacionais.
- Sprint 20 concluida tecnicamente em 10/08/2026 com Relatorios Customizaveis, exportacoes, jobs, retencao de cache e sincronismos agendados.
- Sprint 21 concluida tecnicamente em 12/08/2026 com arquitetura Beta, backups, restore, servico systemd, versionamento e atualizacoes controladas.
- Sprint 17 concluida tecnicamente em 14/08/2026 com Comissoes/Premiacoes, recebimentos OMIE, ASO, Receita por Servidor, 2FA por e-mail, TOTP e alertas operacionais por e-mail.
- Validacao funcional assistida das 8 etapas do Sprint 17 concluida pelo usuario em 14/08/2026.
- Visao Geral operacional atualizada em 10/08/2026 com indices consolidados de contratos, propostas, inadimplencia, administrativo, ClickSign, Zabbix, Proxmox, PBS, TrueNAS e Kanban de Implantacao.
- Sprint Final passa a ser a proxima etapa, focada em homologacao Beta, evidencias, commit/tag/release e rollback; migrations pendentes do Sprint 17 foram aplicadas/conferidas em 14/08/2026.

Documentos de referencia:

- `docs/35-FECHAMENTO-SPRINT-18.md`
- `docs/36-LOGS-BACKEND.md`
- `docs/37-FECHAMENTO-SPRINT-20.md`
- `docs/43-FECHAMENTO-SPRINT-21.md`
- `docs/39-SPRINT-21-RELEASE-BETA.md`
- `docs/40-ARQUITETURA-BETA.md`
- `docs/41-BACKUP-RESTORE.md`
- `docs/42-ATUALIZACOES-SISTEMA.md`
- `docs/17-SPRINTS.md`
- `docs/12-DER.md`
- `docs/13-MODELO-FISICO-DADOS.md`
- `docs/CHANGELOG.md`

Entregas consolidadas recentes:

- Relatorios Customizaveis com fontes autorizadas, campos selecionaveis, filtros, periodo, ordenacao, agrupamentos, agregacoes e modelos salvos.
- Exportacoes CSV, XLSX, DOCX, PDF e impressao HTML com identificacao O3Cloud.
- Fila de relatorios em segundo plano com armazenamento em `storage/relatorios` e processamento via CLI.
- Catalogo de relatorios cobrindo clientes, contratos, financeiro, CRM, administrativo e caches de infraestrutura.
- Configuracoes administrativas para Retencao de Cache e Automacoes de Sincronismo.
- Controle de inadimplencias financeiras por contrato, com historico, bloqueio de novas propostas/implantacoes e notificacoes.
- Painel principal com top 5 contratos, inadimplentes, demandas administrativas, propostas, assinaturas ClickSign, alertas de infraestrutura, backups pendentes e filas/movimentacoes do Kanban.
- Planejamento da release Beta com arquitetura, backup/restore, destinos externos, GitHub Releases e atualizacao controlada por Administrador.
- `Financeiro > Receitas por Servidor` cruza nodes Proxmox sincronizados, ambientes e contratos ativos para apresentar receita recorrente mensal por servidor.
- 2FA por e-mail, TOTP e dispositivo confiavel por 30 dias para usuarios locais.
- Alertas operacionais por e-mail para Zabbix critico, PBS fora do prazo e TrueNAS sem modificacao ha mais de 5 dias.

---

# Fontes Oficiais dos Dados

| Informação        | Sistema Oficial        |
| ----------------- | ---------------------- |
| Clientes          | OMIE / Cadastro Manual |
| Contratos         | OMIE                   |
| Recursos          | NetBox                 |
| Clusters          | Proxmox                |
| Hosts             | Proxmox                |
| Backups           | PBS                    |
| Monitoramento     | Zabbix                 |
| Custos            | O3Cloud Manager        |
| Grupos Econômicos | O3Cloud Manager        |
| Rateios           | O3Cloud Manager        |

---

# Público-alvo

* Diretoria
* Financeiro
* Comercial
* Operações
* Engenharia
* Suporte

---

# Filosofia do Projeto

O sistema foi desenvolvido para transformar informações técnicas em indicadores de negócio.

O objetivo principal não é inventariar ativos, mas gerar inteligência operacional para apoiar decisões estratégicas.

| Sistema             | Responsabilidade                                                                               |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| **OMIE**            | ERP Financeiro, Fiscal, Contábil, DRE, Contas a Pagar, Contas a Receber, Comissão, Faturamento |
| **NetBox**          | CMDB e Inventário da Infraestrutura                                                            |
| **Proxmox**         | Virtualização                                                                                  |
| **PBS**             | Backup                                                                                         |
| **Zabbix**          | Monitoramento                                                                                  |
| **O3Cloud Manager** | Inteligência Operacional e Gerencial                                                           |

