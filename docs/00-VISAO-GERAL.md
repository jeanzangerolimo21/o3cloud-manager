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

Sprint 12 foi concluida em 29/07/2026.

Entregas principais:

- Proposta opcional no fluxo operacional.
- Contratos diretos/parceiros como origem valida para implantacao.
- Separacao entre Integracoes de Negocio e Integracoes Tecnicas.
- OMIE e ClickSign exibidos a partir do ambiente com segredos mascarados.
- Anexos em comentarios de implantacao.

Sprint 13 foi concluida em 29/07/2026.

Decisao principal da Sprint 13:

- Dados reais oficiais serao carregados apenas na fase Beta com a equipe.
- Comercial e areas envolvidas deverao completar cadastros antes das validacoes oficiais.
- Custos, faturamentos e parametros financeiros permanecem preparados, mas sem carga real prematura.

Sprint 14 foi concluida em 30/07/2026.

Entregas principais da Sprint 14:

- Diagnosticos pre-Beta consolidados para clientes, contratos, implantacao, financeiro e integracoes.
- Integracoes tecnicas preparadas para Proxmox, PBS, Zabbix, FreeIPA e TrueNAS em modo seguro.
- Menu de Infraestrutura recebeu Backups PBS, Monitoramento Zabbix e Backup NAS.
- Cadastros finais e revisao assistida foram encaminhados para a fase Beta com a equipe.

Sprint atual: Sprint 15 - Infraestrutura Operacional e Sincronismo Read-Only.

Inicio registrado:

- 30/07/2026

Focos principais da Sprint 15:

- Implementar sincronismo Proxmox VE em modo somente leitura.
- Evoluir telas operacionais de Clusters, Nodes, Maquinas Virtuais e Containers.
- Evoluir consultas de Backups PBS, Monitoramento Zabbix e Backup NAS/TrueNAS.
- Manter automacoes destrutivas fora do escopo ate aprovacao especifica.
- Preparar base tecnica para validacao Beta assistida sem carga real prematura.

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

