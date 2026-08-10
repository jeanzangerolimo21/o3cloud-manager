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

Ultima sprint encerrada: Sprint 20 - Modulo de Relatorios Customizaveis.

Data de fechamento tecnico: 10/08/2026.

Status atual:

- Sprint 18 concluida tecnicamente em 06/08/2026, com validacao assistida encaminhada para a release Beta.
- Sprint 19 implementada em 10/08/2026 com controle de inadimplencia financeira e bloqueios operacionais.
- Sprint 20 concluida tecnicamente em 10/08/2026 com Relatorios Customizaveis, exportacoes, jobs, retencao de cache e sincronismos agendados.
- Homologacao operacional segue pendente de validacao assistida com usuarios, perfis e dados reais controlados.

Documentos de referencia:

- `docs/35-FECHAMENTO-SPRINT-18.md`
- `docs/36-LOGS-BACKEND.md`
- `docs/37-FECHAMENTO-SPRINT-20.md`
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

