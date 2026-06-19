# Banco de Dados

## O3Cloud Manager V2

---

# Objetivo

O banco de dados do O3Cloud Manager foi projetado para centralizar informações provenientes de diferentes sistemas da infraestrutura da O3Cloud.

Ao contrário da versão anterior (V1), onde diversas regras de negócio eram implementadas diretamente nas telas e consultas SQL, a V2 passa a tratar o banco de dados como o núcleo da aplicação.

Toda regra de negócio parte da modelagem dos dados.

---

# Filosofia

O O3Cloud Manager não substitui os sistemas já existentes.

Cada plataforma continua sendo responsável pelo seu domínio.

O banco do O3Cloud Manager mantém uma cópia sincronizada dessas informações para permitir processamento financeiro, geração de indicadores e relatórios gerenciais.

---

# Fontes Oficiais

| Informação        | Sistema Oficial        |
| ----------------- | ---------------------- |
| Clientes          | OMIE / Cadastro Manual |
| Contratos         | OMIE                   |
| Recursos (VM/LXC) | NetBox                 |
| Clusters          | Proxmox                |
| Hosts             | Proxmox                |
| Backups           | PBS                    |
| Monitoramento     | Zabbix                 |
| Custos            | O3Cloud Manager        |
| Grupos Econômicos | O3Cloud Manager        |
| Rateios           | O3Cloud Manager        |
| Relatórios        | O3Cloud Manager        |

---

# Objetivos da Modelagem

A modelagem da V2 foi criada para atender aos seguintes objetivos:

* Eliminar dependência de nomes e prefixos.
* Utilizar identificadores únicos em todos os relacionamentos.
* Suportar múltiplos clusters Proxmox.
* Suportar clientes distribuídos em diversos datacenters.
* Permitir grupos econômicos.
* Permitir rateios financeiros.
* Possibilitar histórico financeiro.
* Facilitar auditoria.
* Reduzir chamadas às APIs externas.
* Permitir expansão futura.

---

# Modelo Conceitual

A estrutura principal do banco foi projetada seguindo o fluxo natural do negócio.

```text
DATACENTER

↓

CLUSTER

↓

HOST

↓

RECURSO (VM / LXC)

↓

CLIENTE

↓

GRUPO ECONÔMICO

↓

CONTRATOS

↓

RECEITAS

↓

RATEIOS

↓

RENTABILIDADE
```

Todo relacionamento do sistema deverá seguir esta estrutura.

---

# Entidades Principais

## Datacenter

Representa a localização física onde os clusters estão hospedados.

Exemplos:

* EVEO
* O3Cloud
* Equinix
* Kener
* AWS (futuro)

---

## Cluster

Representa um cluster Proxmox.

Relacionamentos:

* Datacenter
* Hosts
* Recursos

---

## Host

Representa um servidor físico pertencente a um cluster.

Relacionamentos:

* Cluster
* Recursos

---

## Recursos

Representa qualquer recurso computacional faturável.

Tipos suportados:

* Máquina Virtual
* Container LXC
* Storage (futuro)
* Kubernetes (futuro)

Cada recurso pertence obrigatoriamente a um Host.

---

## Clientes

Representa uma empresa atendida pela O3Cloud.

Origem:

* OMIE
* Cadastro Manual

Relacionamentos:

* Contratos
* Recursos
* Grupos Econômicos
* Receitas
* Rateios

---

## Grupos Econômicos

Agrupam clientes pertencentes ao mesmo grupo empresarial.

Exemplos:

Shopping do Real

├── Shopping do Real

├── Doce Lar

└── Utilitex

---

## Contratos

Representam contratos comerciais provenientes do OMIE.

Cada contrato pertence inicialmente a um cliente.

Posteriormente poderá sofrer rateios.

---

## Receitas

Representam toda entrada financeira.

Tipos:

* OMIE
* Manual
* Rateio
* Ajuste

---

## Rateios

Responsáveis pela divisão financeira de contratos.

Permitem dividir uma receita entre diversos clientes.

Exemplo:

Contrato A

↓

50%

Cliente A

↓

30%

Cliente B

↓

20%

Cliente C

---

## Custos

Representam custos operacionais.

Tipos:

* CPU
* Memória
* Disco
* Licenças
* Servidores
* Links
* Energia (futuro)

---

## Rentabilidade

Tabela responsável por consolidar:

Receita

↓

Custo

↓

Lucro

↓

Margem

por:

* Cliente
* Grupo Econômico
* Host
* Cluster
* Datacenter

---

# Relacionamentos

## Cliente → Grupo Econômico

N:N

Um cliente pode participar de um grupo econômico.

Um grupo econômico possui vários clientes.

---

## Cliente → Recursos

1:N

Um cliente pode possuir diversos recursos.

Cada recurso pertence a apenas um cliente.

---

## Cluster → Hosts

1:N

Um cluster possui diversos hosts.

---

## Host → Recursos

1:N

Um host possui diversas VMs e Containers.

---

## Cliente → Contratos

1:N

Um cliente pode possuir diversos contratos.

---

## Contrato → Rateios

1:N

Um contrato pode possuir diversos rateios.

---

## Cliente → Receitas

1:N

Um cliente pode possuir diversas receitas.

---

# Novas Tabelas da V2

A V2 introduz novas tabelas para eliminar limitações existentes na V1.

## cliente_recursos

Responsável por vincular recursos diretamente aos clientes.

Campos previstos:

* id
* cliente_id
* cluster_id
* host_id
* recurso_id
* ativo
* criado_em

---

## contrato_rateios

Responsável por dividir contratos entre clientes.

Campos previstos:

* id
* contrato_id
* cliente_id
* percentual
* valor
* observacoes

---

## sincronizacoes

Controla todas as integrações externas.

Campos previstos:

* sistema
* ultima_execucao
* status
* registros_processados
* tempo_execucao
* mensagem

---

## auditoria

Registro de alterações realizadas pelos usuários.

Campos previstos:

* usuário
* ação
* tabela
* registro
* data
* ip

---

# Estratégia de Sincronização

Nenhuma tela deverá consultar diretamente sistemas externos.

Fluxo oficial:

```text
OMIE

↓

Banco Local

↓

Dashboard
```

```text
Proxmox

↓

Banco Local

↓

Infraestrutura
```

```text
NetBox

↓

Banco Local

↓

Inventário
```

O banco de dados passa a ser o ponto central de todas as consultas.

---

# Regras de Negócio

* Todo recurso pertence a um cliente.
* Todo cliente pode possuir diversos contratos.
* Todo contrato pode ser rateado.
* Todo cliente pode participar de um grupo econômico.
* Todo custo deve ser rastreável.
* Toda receita deve possuir origem.
* Nenhum relacionamento será baseado em nomes.
* Todos os relacionamentos utilizarão identificadores únicos.

---

# Evoluções Futuras

Planejamento para versões posteriores:

* Histórico mensal de custos.
* Histórico mensal de rentabilidade.
* Snapshots financeiros.
* API REST.
* Auditoria completa.
* Controle de permissões por módulo.
* Integração com sistema de chamados.
* Portal do Cliente.
* Aplicativo Mobile.

---

# Considerações Finais

A modelagem da V2 foi desenvolvida priorizando escalabilidade, rastreabilidade e independência entre sistemas.

O banco de dados passa a representar o modelo de negócio da O3Cloud, permitindo que novas funcionalidades sejam adicionadas sem necessidade de remodelagens estruturais.

