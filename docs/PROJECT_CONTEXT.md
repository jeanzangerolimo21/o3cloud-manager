# O3Cloud Manager v3.0

# PROJECT_CONTEXT.md

Versão: 1.0

Status: Oficial

Última atualização: Julho/2026

---

# Objetivo

Este documento apresenta o contexto completo do projeto O3Cloud Manager.

Todo agente de Inteligência Artificial deverá compreender este documento antes de implementar qualquer funcionalidade.

Seu objetivo é fornecer uma visão completa do sistema, evitando decisões isoladas e garantindo que cada implementação esteja alinhada com a arquitetura e com os objetivos da empresa.

---

# Sobre o Projeto

Nome:

O3Cloud Manager

Versão:

3.0 Alpha

Empresa:

O3 Cloud

Status:

Em desenvolvimento ativo.

---

# Objetivo Estratégico

O O3Cloud Manager é o ERP oficial da O3 Cloud.

Seu propósito é centralizar toda a operação da empresa em uma única plataforma.

O sistema substituirá processos manuais e integrará informações entre os setores Comercial, Financeiro e Operacional.

---

# Visão de Longo Prazo

O sistema deverá controlar:

- CRM Comercial
- Clientes
- Contratos
- Catálogo Técnico
- Dimensionamento
- Precificação
- Propostas
- Assinatura Eletrônica
- Implantação
- Infraestrutura
- Monitoramento
- Custos
- Rentabilidade
- Dashboards
- Indicadores Executivos

---

# Arquitetura

Arquitetura oficial:

Routes

↓

Service

↓

Repository

↓

MariaDB

Toda persistência utiliza SQL puro.

ORM é proibido.

---

# Tecnologia

Backend

Python 3.12

Flask

MariaDB

Jinja2

Bootstrap 5

Frontend

HTML

CSS

Bootstrap

JavaScript

Banco

MariaDB

Integrações

REST APIs

---

# Estrutura do Projeto

app/

administracao/

ambientes/

catalogo/

clientes/

contratos/

financeiro/

negocios/

parceiros/

core/

repositories/

templates/

---

# Módulos Atuais

Ambientes

Clientes

Contratos

Catálogo Técnico

Financeiro

Parceiros

Negócios (em evolução)

---

# Catálogo Técnico

Estrutura:

Categorias

↓

Produtos

↓

Modelos

↓

Faixas

↓

Servidores

↓

Dimensionamento

---

# CRM

Fluxo:

Lead

↓

Contato

↓

Oportunidade

↓

Levantamento

↓

Dimensionamento

↓

Precificação

↓

Proposta

↓

ClickSign

↓

Contrato

↓

Implantação

↓

Cliente Ativo

---

# Integrações

Atuais

OMIE

Proxmox

Planejadas

ClickSign

Base44

PBS

NetBox

---

# Padrões Arquiteturais

Repository

↓

Service

↓

Routes

↓

Templates

Sempre nesta ordem.

---

# Componentes Homologados

page_header.html

filter_bar.html

crud_actions.html

alert.html

index_base.html

form_base.html

view_base.html

Nunca alterar sem autorização.

---

# Sprint Atual

Sprint 13

Dados Oficiais, Validacoes Tecnicas e Preparacao Operacional

Status:

Em planejamento.

Sprint anterior:

Sprint 12 - Pendencias Operacionais e Preparacao da Versao Final

Status:

Concluida em 29/07/2026.

---

# Objetivos do Projeto

Automatizar processos.

Reduzir trabalho manual.

Centralizar informações.

Integrar sistemas.

Gerar indicadores.

Suportar crescimento da empresa.

---

# Papel da IA

A IA atua como Engenheiro de Software.

Seu objetivo é:

- preservar arquitetura;
- reduzir retrabalho;
- produzir código consistente;
- sugerir melhorias;
- respeitar a documentação oficial.

Nunca tomar decisões que contrariem os documentos oficiais.

---

# Documentos Obrigatórios

Antes de qualquer implementação, consultar:

03-ARQUITETURA.md

04-PADROES.md

05-SPRINT-ATUAL.md

08-ARCHITECTURE-FREEZE.md

15-CHECKLIST.md

16-DEFINITION-OF-DONE.md

AGENTS.md

PROJECT_CONTEXT.md

DOMAIN_RULES.md

AI_WORKFLOW.md

---

# Objetivo Final

Toda IA deverá compreender este documento antes de escrever qualquer linha de código.

O objetivo é garantir que todas as implementações estejam alinhadas com a visão estratégica da O3 Cloud.
