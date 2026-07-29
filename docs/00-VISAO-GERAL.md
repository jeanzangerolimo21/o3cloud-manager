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

Proxima sprint registrada: Sprint 14 - Consolidacao Pre-Beta e Preparacao de Validacao com a Equipe.

Inicio previsto:

- 30/07/2026

Pendencias principais da Sprint 14:

- Mapear cadastros e campos pendentes para preenchimento pela equipe.
- Preparar diagnosticos de dados incompletos sem bloquear fluxos validos.
- Criar checklist de validacao Beta por area.
- Refinar indicadores pre-Beta sem carga real oficial.
- Manter validacoes tecnicas em modo nao destrutivo.

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

