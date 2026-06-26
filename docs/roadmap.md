O3Cloud Manager
Roadmap Oficial - Versão 1.0

Última atualização: 24/06/2026

Objetivo do Projeto

Criar uma plataforma única para gerenciamento operacional, financeiro e técnico da O3Cloud, centralizando clientes, contratos, infraestrutura, implantação e rentabilidade em uma única aplicação.

Stack Tecnológica
Item	Tecnologia
Backend	Python 3.12
Framework	Flask
Banco	MariaDB
Frontend	Bootstrap 5
ORM	SQL puro (Repositories)
API	REST
Hospedagem	Ubuntu Server
Arquitetura
app/

clientes/
contratos/
financeiro/
infraestrutura/
implantacao/
auditoria/
usuarios/
dashboard/

repositories/
services/
templates/
core/

Arquitetura baseada em:

Repository Pattern
Service Layer
Blueprints Flask
Templates separados por módulo
Integrações
Omie

Status:

✅ Funcionando

Objetivo:

Clientes
Contratos
Produtos

Regra importante:

✔ Apenas contratos com Status = Ativo entram nos cálculos financeiros.

Ignorar:

Em elaboração
Cancelado
Proxmox

Status:

✅ Funcionando

Objetivo:

Hosts
Clusters
VMs
Containers
Recursos
PBS

Status:

✅ Funcionando

Objetivo:

Backups
Histórico
Status
Zabbix

Status:

✅ Funcionando

Objetivo:

Monitoramento
Disponibilidade
Inventário
NetBox

Status:

Em evolução

Objetivo:

Inventário
Documentação
Sincronização
Banco de Dados

Principais tabelas

clientes

clientes_implantacao

contratos

produtos

servidores

vm_metrics

custos_cloud

usuarios

auditoria
Sprint 1
Infraestrutura

✅ Estrutura Flask

✅ MariaDB

✅ Repository Pattern

✅ Layout

Sprint 2
Integrações

✅ Omie

✅ Proxmox

✅ PBS

✅ Zabbix

Sprint 3
Financeiro

✅ Dashboard inicial

✅ Custos Cloud

✅ Rentabilidade inicial

Sprint 4
Clientes

Status:

95%

Concluído

✅ Listagem

✅ Pesquisa

✅ Paginação

✅ Cadastro Manual

✅ Exclusão Manual

✅ Visualização

✅ Origem Manual

✅ Origem OMIE

✅ CNPJ

✅ Pesquisa por CNPJ

✅ Implantação (estrutura)

✅ Observações Técnicas

✅ Cards dos próximos módulos

Pendente

⬜ Editar Cliente

⬜ Editar Implantação

⬜ Salvar Implantação

⬜ Histórico de Alterações

Sprint 5
Contratos

Objetivo

Sincronizar contratos ativos do Omie.

Funcionalidades

⬜ CRUD

⬜ Visualização

⬜ Produtos do contrato

⬜ Valor mensal

⬜ Data renovação

⬜ Histórico

⬜ Cliente x Contrato

⬜ Contratos ativos

⬜ Desconsiderar contratos cancelados

Financeiro

⬜ Receita Mensal

⬜ Custos

⬜ Impostos

⬜ Comissão

⬜ Mão de obra

⬜ Rentabilidade

⬜ EBITDA

⬜ Margem

Sprint 6
Infraestrutura

Objetivo

Integrar totalmente o ambiente Proxmox.

Funcionalidades

⬜ Hosts

⬜ Clusters

⬜ Storage

⬜ Recursos

⬜ Capacidade

⬜ Oversubscription

⬜ Health Score

⬜ Capacity Planning

Sprint 7
Implantação

Objetivo

Transformar implantação em módulo operacional.

Board Kanban

Inspirado em

Trello
Jira

Colunas

Novo

Planejamento

Preparação

Implantação

Homologação

Produção

Concluído

Cada card terá

Cliente
Contrato
Responsável
Prioridade
Data prevista
Servidor
Cluster
Checklist
Observações

Drag & Drop

✅ Sim

Sprint 8
Escolha Inteligente de Servidor

Grande diferencial do sistema.

Entrada

Cliente

Contrato

CPU

RAM

Disco

Datacenter

O sistema analisará

✔ CPU

✔ RAM

✔ Disco

✔ Storage

✔ Oversubscription

✔ Custo

✔ Rentabilidade

✔ Cluster

✔ Datacenter

Resultado

Servidor recomendado

Score

98%

Motivos
Sprint 9
Auditoria

Registrar tudo.

Quem alterou

Quando

Valor anterior

Valor novo

IP

Data

Sprint 10
Usuários

Perfis

Administrador

Financeiro

Implantação

Suporte

Comercial

Diretoria

Permissões por módulo.

Sprint 11
Dashboards

Executivo

Financeiro

Infraestrutura

Implantação

Comercial

Operacional

Sprint 12
Automações

Quando um contrato novo aparecer no Omie

↓

Criar Cliente

↓

Criar Projeto de Implantação

↓

Entrar automaticamente no Board

↓

Sugerir Servidor

↓

Gerar Checklist

↓

Acompanhar Implantação

Objetivo Final

O O3Cloud Manager deixará de ser apenas um sistema financeiro e se tornará uma plataforma completa para gestão operacional de provedores de Cloud.

Fluxo completo:

Contrato Ativo (Omie)
        │
        ▼
Cliente
        │
        ▼
Projeto de Implantação
        │
        ▼
Board Kanban
        │
        ▼
Escolha Inteligente do Servidor
        │
        ▼
Provisionamento
        │
        ▼
Monitoramento
        │
        ▼
Backup
        │
        ▼
Produção
        │
        ▼
Financeiro
        │
        ▼
Rentabilidade
        │
        ▼
Auditoria
