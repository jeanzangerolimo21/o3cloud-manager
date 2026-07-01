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

✅ Editar Cliente

✅ Editar Implantação

✅ Salvar Implantação

✅ Histórico de Alterações

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

Sprint 5
──────────────

✅ 5.1 Clientes

✅ 5.2 Contratos

✅ 5.3 Itens dos Contratos

🟡 5.4 Consolidação
    • Revisão dos Repositories
    • Revisão dos Services
    • Atualização da documentação
    • Migrações finais
    • Testes completos

🟡 5.5 Release Sprint 5
    • Git Tag
    • Changelog
    • Banco consolidado


# O3Cloud Manager V2

# Arquitetura do Domínio - Sprint 6

**Versão:** 1.0
**Status:** Em elaboração
**Objetivo:** Definir a arquitetura funcional e o modelo de domínio que integrará os módulos Financeiro e Infraestrutura do O3Cloud Manager.

---

# 1. Objetivo

O Sprint 6 tem como objetivo integrar os recursos de infraestrutura (Proxmox, PBS, NetBox e futuramente Zabbix) ao módulo Financeiro (OMIE), criando uma visão única do cliente.

O foco deixa de ser apenas sincronizar informações e passa a representar corretamente o modelo de negócio da O3Cloud.


Sprint 6.1 - Módulo Parceiros

Objetivo: Criar um cadastro mestre para identificar a origem comercial dos projetos.

Funcionalidades
✅ Listar parceiros
✅ Pesquisar
✅ Novo parceiro
✅ Visualizar
✅ Editar
✅ Excluir (somente se não estiver sendo utilizado)
✅ Ativar/Inativar


Parceiros

├── Repository
├── Service
├── Routes
├── Index
├── Form
├── View
├── Novo
├── Editar
├── Excluir
├── Pesquisa
└── Paginação

---

# 2. Princípios da Arquitetura

A arquitetura da V2 será baseada nos seguintes princípios:

* Uma única fonte de verdade para cada informação.
* Separação clara entre domínio Financeiro e Infraestrutura.
* Sincronizações totalmente automáticas sempre que possível.
* Mínima intervenção manual.
* Preparação para múltiplos clusters e futuras integrações.

---

# 3. Domínios do Sistema

## Financeiro

Responsável pelas informações comerciais.

Entidades:

* Clientes
* Contratos
* Itens de Contrato
* Licenciamento

Origem:

OMIE

---

## Infraestrutura

Responsável pelos recursos técnicos.

Entidades futuras:

* Clusters
* Nodes
* Máquinas Virtuais
* Containers
* Storages
* PBS
* Redes
* Templates

Origem:

Proxmox

---

# 4. O Conceito Central da V2

Na versão anterior o relacionamento era baseado em Máquinas Virtuais.

Na V2 o conceito central passa a ser:

## Ambiente

Um Ambiente representa toda a infraestrutura entregue para um cliente.

Um Ambiente pode conter:

* Máquinas Virtuais
* Containers
* Storage
* PBS
* Firewall
* Redes
* Recursos futuros

A Máquina Virtual deixa de representar a unidade de negócio.

---

# 5. Relacionamentos

Cliente

↓

Ambiente

↓

Recursos

e

Contrato

↓

Ambiente

Os contratos deixam de apontar diretamente para recursos.

Os recursos deixam de apontar diretamente para contratos.

O Ambiente torna-se a entidade responsável por integrar os dois domínios.

---

# 6. Tipos de Ambiente

Os tipos de ambiente serão identificados automaticamente pelas Tags do Proxmox.

Tags suportadas:

* prod
* implan
* teste
* template

Mapeamento:

prod → Produção

implan → Implantação

teste → Teste

template → Template

Templates não serão vinculados automaticamente a clientes.

---

# 7. Identificação Automática

Cada Ambiente possuirá um Identificador Técnico.

Exemplo:

CMP

NAVARRO

REDEMAIS

Esse identificador será utilizado para localizar automaticamente os recursos sincronizados do Proxmox.

Fluxo:

Nome VM

↓

Identificador Técnico

↓

Cliente

↓

Ambiente

↓

Vinculação automática

---

# 8. Casos de Uso

## Caso 1

Um Ambiente atendendo vários contratos.

Exemplo:

Cliente:

CompreMais

Ambiente:

Produção

Contratos:

Loja 1

Loja 2

Loja 3

Loja 4

Todos compartilham o mesmo ambiente.

---

## Caso 2

Um Contrato atendendo vários ambientes.

Exemplo:

Parceiro

↓

Contrato único

↓

Ambiente Cliente A

Ambiente Cliente B

Ambiente Cliente C

---

# 9. Modelo Conceitual

Cliente

↓

Ambiente

↓

Recursos

↓

VM

Container

Storage

PBS

Enquanto:

Contrato

↓

Ambiente

↓

Itens Comerciais

---

# 10. Benefícios

Esta arquitetura permite:

* Ambientes compartilhados.
* Contratos compartilhados.
* Rateio de custos.
* Rentabilidade por contrato.
* Rentabilidade por ambiente.
* Rentabilidade por cliente.
* Evolução futura para NetBox.
* Evolução futura para Zabbix.
* Evolução futura para Kubernetes.

---

# 11. Próximas Etapas

Sprint 6.1

* Modelagem física do banco de dados.

Sprint 6.2

* Sincronização do Proxmox.

Sprint 6.3

* Vínculo automático dos Ambientes.

Sprint 6.4

* Tela Cliente 360°.

Sprint 6.5

* Dashboard Executivo.

---

# 12. Objetivo Final

Ao término do Sprint 6, o O3Cloud Manager será capaz de apresentar, em uma única tela:

Cliente

↓

Contrato

↓

Escopo Comercial

↓

Ambientes

↓

Máquinas Virtuais

↓

Containers

↓

Backups

↓

Recursos Consumidos

↓

Custos

↓

Rentabilidade

Conectando as áreas Comercial, Financeira, Implantação e Operações em uma única plataforma.



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
