# Modelo de Domínio

## O3Cloud Manager V2

---

# Objetivo

Este documento descreve o modelo de domínio do O3Cloud Manager.

Seu objetivo é representar o funcionamento da operação da O3Cloud antes da implementação do banco de dados e do código.

O modelo de domínio é a principal referência para o desenvolvimento da plataforma.

---

# Visão Geral

O O3Cloud Manager é dividido em cinco domínios principais.

```text
Financeiro

Infraestrutura

Operações

Integrações

Administração
```

Cada domínio possui entidades próprias e responsabilidades bem definidas.

---

# Domínio Financeiro

Responsável pela gestão financeira dos clientes.

## Entidades

### Cliente

Representa uma empresa atendida pela O3Cloud.

Origem:

* OMIE
* Manual

Pode possuir:

* Contratos
* Recursos
* Licenças
* Implantações
* Receitas
* Custos
* Rateios

---

### Grupo Econômico

Agrupa empresas pertencentes ao mesmo grupo.

Exemplo:

Shopping do Real

* Shopping do Real
* Doce Lar
* Utilitex

Objetivo:

Consolidar receitas, custos e rentabilidade.

---

### Contrato

Representa um contrato comercial.

Origem:

OMIE

Informações sincronizadas:

* Número
* Valor
* Status
* Datas
* Descrição original

Informações complementadas pelo O3Cloud Manager:

* Observações técnicas
* Escopo operacional
* Rateios
* Licenças vinculadas

---

### Receita

Representa qualquer entrada financeira.

Tipos:

* OMIE
* Manual
* Rateio
* Ajuste

---

### Rateio

Permite dividir contratos entre clientes.

Exemplo:

Contrato A

50% Cliente A

30% Cliente B

20% Cliente C

---

### Custo

Representa os custos operacionais.

Tipos previstos:

* CPU
* Memória
* Disco
* Licenciamento
* Servidor
* Link
* Energia (futuro)

---

### Rentabilidade

Consolida:

Receita

↓

Custos

↓

Lucro

↓

Margem

Pode ser calculada por:

* Cliente
* Grupo Econômico
* Host
* Cluster
* Datacenter

---

# Domínio Infraestrutura

Representa toda infraestrutura monitorada.

## Datacenter

Local físico onde os clusters estão hospedados.

---

## Cluster

Representa um cluster Proxmox.

Possui:

* Hosts
* Recursos

---

## Host

Servidor físico.

Possui:

* Máquinas Virtuais
* Containers
* Recursos

---

## Recurso

Representa qualquer ativo computacional.

Tipos:

* Máquina Virtual
* Container LXC

Origem:

NetBox / Proxmox

Cada recurso pertence obrigatoriamente a um cliente.

---

# Domínio Operações

Centraliza informações operacionais.

## Implantação

Representa o processo de implantação de um cliente.

Pode conter:

* Responsável
* Status
* Checklist
* Observações
* Documentação

---

## Licenças O3Web

Centraliza o controle de licenciamento.

Cada licença possui:

* Número
* Quantidade
* Cliente
* Contrato
* Status
* Observações

---

## Observações Técnicas

Informações operacionais que não existem no OMIE.

Exemplos:

* Escopo do ambiente
* Particularidades
* Procedimentos
* Histórico técnico

---

## Timeline

Registro cronológico dos eventos do cliente.

Exemplos:

* Cliente criado
* Contrato sincronizado
* Implantação iniciada
* VM criada
* Licença cadastrada
* Backup configurado

---

# Domínio Administração

Responsável pela segurança da plataforma.

## Usuários

Acesso ao sistema.

---

## Perfis

Exemplos:

* Administrador
* Financeiro
* Comercial
* Operações
* Implantação
* Diretoria
* Suporte

---

## Permissões

Controlam:

* Visualização
* Inclusão
* Alteração
* Exclusão
* Exportação
* Visualização de valores financeiros

Usuários sem permissão financeira poderão acessar as telas normalmente, porém os valores monetários permanecerão ocultos.

---

## Auditoria

Registra todas as alterações realizadas pelos usuários.

---

# Domínio Integrações

O sistema sincroniza informações provenientes de:

* OMIE
* Proxmox
* NetBox
* PBS
* Zabbix
* TrueNAS

Nenhuma tela consulta diretamente esses sistemas.

Todo processamento ocorre sobre o banco local.

---

# Princípios da V2

* Todo relacionamento utiliza identificadores únicos.
* Não utilizar prefixos como vínculo.
* Não utilizar nomes como chave de relacionamento.
* Todo recurso pertence a um cliente.
* Todo contrato possui origem.
* Toda receita possui origem.
* Toda alteração relevante gera auditoria.
* Toda integração mantém histórico de sincronização.

---

# Objetivo Final

O O3Cloud Manager será a plataforma central de gestão operacional da O3Cloud, consolidando informações financeiras, operacionais e de infraestrutura em um único ambiente.

