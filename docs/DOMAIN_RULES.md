# O3Cloud Manager v3.0

# DOMAIN_RULES.md

## Regras Oficiais de Negócio

Versão: 1.0

Status: Oficial

Última atualização: Julho/2026

---

# Objetivo

Este documento define as regras de negócio oficiais da O3 Cloud.

Toda Inteligência Artificial deverá consultar este documento antes de implementar funcionalidades relacionadas ao domínio da aplicação.

Estas regras possuem prioridade sobre decisões técnicas.

A arquitetura define **como** implementar.

Este documento define **o que** deve acontecer.

---

# Princípio Geral

O O3Cloud Manager representa toda a operação da O3 Cloud.

Todo módulo existe para atender um processo real da empresa.

Nenhuma funcionalidade deverá ser criada sem estar vinculada a um processo de negócio.

---

# Cliente

Um cliente representa uma empresa que possui relacionamento comercial com a O3 Cloud.

O cliente poderá possuir origem:

- MANUAL
- OMIE

Clientes sincronizados com a OMIE possuem restrições.

---

## Cliente OMIE

Quando origem = OMIE:

- Código externo é obrigatório.
- Sincronização prevalece sobre alterações locais.
- Campos controlados pela OMIE não deverão ser alterados manualmente.
- A sincronização nunca deverá perder o vínculo entre sistemas.

Sempre preservar:

- codigo_externo
- origem
- synced_at

---

## Cliente Manual

Clientes manuais podem ser editados normalmente.

Futuramente poderão ser sincronizados com a OMIE.

---

# Contratos

Todo contrato pertence obrigatoriamente a um cliente.

Origens permitidas:

- MANUAL
- OMIE
- CLICKSIGN (futuro)

Um contrato representa um serviço ativo contratado pelo cliente.

---

## Situações do Contrato

O contrato poderá estar:

- Ativo
- Suspenso
- Cancelado

Cada mudança de status deverá ser registrada.

---

# Catálogo Técnico

O Catálogo Técnico é a única fonte oficial de produtos.

Nenhum módulo poderá criar produtos fora do Catálogo.

Estrutura oficial:

Categoria

↓

Produto

↓

Modelo

↓

Faixa

↓

Servidor

↓

Dimensionamento

---

# Categoria

Agrupa produtos semelhantes.

Exemplos:

- Cloud
- Backup
- Licenciamento
- Serviços
- Projetos

Categorias não possuem preço.

---

# Produto

Todo produto pertence obrigatoriamente a uma categoria.

Pode possuir:

- valor de venda
- custo
- tipo de recurso
- modelos
- faixas
- servidores

Produtos representam itens comercializáveis.

---

# Modelo

Representa uma variação técnica de um produto.

Exemplos:

Servidor Small

Servidor Medium

Servidor Large

Os modelos serão utilizados pelo dimensionamento.

---

# Faixa

Representa uma regra baseada em quantidade.

Exemplos:

Até 10 usuários

11 a 25 usuários

26 a 50 usuários

Mais de 50 usuários

As faixas influenciam preços e recursos.

---

# Servidores

Representam recursos necessários para determinado modelo.

Podem possuir:

CPU

RAM

Disco

Storage

Backup

Rede

Licenciamento

---

# Dimensionamento

O dimensionamento nunca deverá utilizar valores fixos.

Sempre utilizar:

Produto

↓

Modelo

↓

Faixa

↓

Servidor

↓

Recursos

↓

Preço

---

# Precificação

Toda precificação deverá utilizar:

Custo

↓

Margem

↓

Preço

↓

Desconto

↓

Valor Final

Nunca utilizar preços calculados manualmente quando existir regra automática.

---

# CRM

Fluxo oficial:

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

Negociação

↓

ClickSign

↓

Contrato

↓

Implantação

↓

Cliente Ativo

Nenhuma etapa deverá ser ignorada.

---

# Propostas

Toda proposta deverá:

Possuir versão.

Possuir status.

Possuir validade.

Possuir itens.

Possuir histórico.

Uma proposta aprovada poderá gerar contrato.

---

# ClickSign

Após assinatura:

Criar contrato.

↓

Atualizar status.

↓

Criar implantação.

↓

Iniciar integração financeira.

Nenhuma implantação deverá iniciar antes da assinatura.

---

# Implantação

A implantação representa a entrega técnica do projeto.

Fluxo:

Contrato

↓

Projeto

↓

Checklist

↓

Provisionamento

↓

Validação

↓

Entrega

---

# Provisionamento

Todo provisionamento deverá utilizar:

Catálogo Técnico

Modelos

Recursos

Nunca criar infraestrutura manualmente sem rastreabilidade.

---

# Proxmox

Representa a infraestrutura da empresa.

Toda VM deverá possuir vínculo com:

Cliente

Contrato

Produto

Servidor

Sempre que possível preservar rastreabilidade.

---

# OMIE

Responsável por:

Clientes

Contratos

Financeiro

Faturamento

O O3Cloud Manager complementa a OMIE.

Nunca substituir regras oficiais da OMIE.

---

# Financeiro

Toda cobrança deverá estar vinculada a:

Cliente

Contrato

Itens contratados

Nunca gerar cobrança sem contrato.

---

# Histórico

Toda alteração relevante deverá preservar histórico.

Evitar perda de informações.

Sempre que possível utilizar Soft Delete.

---

# Auditoria

Mudanças importantes deverão registrar:

Data

Usuário

Origem

Responsável

O objetivo é permitir rastreabilidade completa.

---

# Integrações Futuras

O sistema deverá estar preparado para integração com:

- ClickSign
- Base44
- PBS
- NetBox

Toda implementação deve considerar estas futuras integrações.

---

# Decisões de Negócio

Quando existir conflito entre:

Arquitetura

e

Regra de Negócio

A IA deverá interromper a implementação e solicitar orientação ao Product Owner.

Nunca assumir comportamento de negócio.

---

# Objetivo Final

Toda implementação deverá respeitar estas regras de domínio.

O O3Cloud Manager representa processos reais da O3 Cloud.

Portanto, preservar as regras de negócio é tão importante quanto preservar a arquitetura do sistema.
