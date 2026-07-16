# O3Cloud Manager v3.0

Versão: 3.0 Alpha

Status: Em Desenvolvimento

Última atualização: Julho/2026

---

# Objetivo

O O3Cloud Manager é uma plataforma desenvolvida internamente pela O3 Cloud para centralizar toda a operação técnica, comercial e financeira da empresa.

O objetivo é eliminar planilhas, automatizar integrações e concentrar todas as informações da operação em um único sistema.

O projeto foi concebido para ser modular, escalável e de fácil manutenção.

---

# Tecnologias

Backend

- Python 3
- Flask
- MariaDB
- SQL puro

Frontend

- Bootstrap 5
- Jinja2
- Bootstrap Icons

Infraestrutura

- Ubuntu Server
- Apache/Nginx
- Git

---

# Arquitetura

Todo módulo obrigatoriamente utiliza a arquitetura abaixo.

Routes

↓

Service

↓

Repository

↓

MariaDB

Cada camada possui apenas uma responsabilidade.

---

# Repository

Responsável exclusivamente pelo acesso ao banco de dados.

Responsabilidades

- SELECT
- INSERT
- UPDATE
- Soft Delete

Não deve conter:

- Regras de negócio
- Flask
- HTML
- Request
- Flash Messages

Todos os repositories herdam obrigatoriamente de:

BaseRepository

---

# Service

Responsável pelas regras de negócio.

Responsabilidades

- validações
- normalizações
- verificações
- tratamento dos dados

O Service nunca conhece Flask.

Nunca acessa request.

Nunca renderiza templates.

Nunca faz SQL.

Toda persistência é realizada pelo Repository.

---

# Routes

Responsável apenas por:

- receber requisição
- chamar Service
- renderizar template
- redirect
- flash messages

Não deve possuir regras de negócio.

---

# Templates

Todo frontend utiliza componentes compartilhados.

Não duplicar código HTML.

Sempre reutilizar componentes.

---

# Componentes Homologados

Framework Visual

components/

- alert.html
- crud_actions.html
- filter_bar.html
- page_header.html

crud/

- form_base.html
- index_base.html
- view_base.html

Esses componentes estão congelados (Architecture Freeze).

Não alterar estrutura.

Apenas correções de bugs aprovadas.

---

# Banco de Dados

Banco

MariaDB

Princípios

- SQL puro
- Sem ORM
- UUID em todos os cadastros
- Soft Delete
- Timestamp automático

Campos padrão

id

uuid

ativo

created_at

updated_at

created_by

updated_by

Sempre utilizar BaseRepository para acesso ao banco.

---

# Convenções

Nunca utilizar DELETE físico.

Sempre utilizar:

UPDATE tabela
SET ativo = 0

Todo cadastro possui:

- listar
- buscar
- inserir
- atualizar
- desativar
- reativar

---

# Estrutura dos Módulos

Cada módulo deve seguir exatamente este padrão.

modulo/

repository.py

service.py

routes.py

templates/

index.html

form.html

view.html

---

# Fluxo de Desenvolvimento

Toda implementação segue obrigatoriamente esta sequência.

1.
Repository

↓

2.
Service

↓

3.
Routes

↓

4.
Templates

↓

5.
Homologação

↓

6.
Próximo CRUD

Nunca iniciar outro CRUD antes da homologação do anterior.

---

# Estrutura Atual

app/

administracao/

catalogo/

clientes/

contratos/

core/

financeiro/

integracoes/

repositories/

templates/

---

# Catálogo Técnico

O Catálogo Técnico será responsável por toda a estrutura comercial da empresa.

Módulos

Categorias

Produtos

Modelos

Faixas

Servidores

Dimensionamento

Precificação

Propostas

---

# CRM Comercial

Sprint futura.

Módulos

Leads

Oportunidades

Dimensionamento

Precificação

Propostas

Workflow Comercial

---

# Dashboard Executivo

Sprint futura.

Indicadores

Financeiro

Custos

Rentabilidade

Consumo

Infraestrutura

---

# Integrações

OMIE

Proxmox

PBS

NetBox

Base44

Cada integração deverá possuir seu próprio módulo.

Nunca misturar regras de negócio das integrações com Services do sistema.

---

# Filosofia do Projeto

O projeto deve permanecer simples.

Código limpo.

Baixo acoplamento.

Alta reutilização.

Arquitetura previsível.

Componentes compartilhados.

Sem duplicação de código.

Toda nova funcionalidade deve seguir os padrões definidos nesta documentação.

---

# Objetivo Final

O O3Cloud Manager será a plataforma única de gestão da O3 Cloud.

Ele centralizará:

Infraestrutura

Financeiro

Clientes

Contratos

CRM

Dimensionamento

Custos

Rentabilidade

Monitoramento

Integrações

Relatórios

Dashboards

Toda evolução futura deverá respeitar esta arquitetura.
