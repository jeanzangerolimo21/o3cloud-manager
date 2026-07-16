                                        NEGÓCIOS
                                            │
      ┌─────────────────────────────────────┼─────────────────────────────────────┐
      │                                     │                                     │
      ▼                                     ▼                                     ▼
   Dashboard                            Cadastros                            Operações
      │                                     │                                     │
      │                                     │                                     │
      ▼                                     ▼                                     ▼
 Leads                         Catálogo Técnico                  Oportunidades
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
   Categorias                    Produtos                     Perfis
                                                                │
                                                                ▼
                                                        Faixas de Usuários
                                                                │
                                                                ▼
                                                        Recursos Técnicos
                                                                │
                                                                ▼
                                                         Pacotes Upgrade
                                                                │
                                                                ▼
                                                      Motor Dimensionamento
                                                                │
                                                                ▼
                                                       Motor Precificação
                                                                │
                                                                ▼
                                                            Propostas
                                                                │
                               ┌────────────────────────────────┼──────────────────────┐
                               ▼                                ▼                      ▼
                           PDF / Email                     ClickSign             Aprovação
                               │                                │
                               └────────────────────────────────┘
                                                │
                                                ▼
                                        Contrato Assinado
                                                │
               ┌────────────────────────────────┼────────────────────────────────┐
               ▼                                ▼                                ▼
          Financeiro                     Implantação                    Infraestrutura
               │                                │                                │
               ▼                                ▼                                ▼
            OMIE                         Kanban Projeto                    Proxmox

Excelente. Eu considero esse o **primeiro documento de arquitetura do O3Cloud Manager v3.0**.

E vou propor uma regra daqui para frente:

> **Não criaremos nenhuma tabela sem antes ela existir neste diagrama funcional.**

Foi exatamente assim que conseguimos manter os módulos de Clientes, Contratos, Parceiros e Ambientes organizados. Agora vamos aplicar isso ao módulo **Negócios**.

---

# O3Cloud Manager v3.0

# Módulo Negócios (Arquitetura Funcional)

text
                                        NEGÓCIOS
                                            │
      ┌─────────────────────────────────────┼─────────────────────────────────────┐
      │                                     │                                     │
      ▼                                     ▼                                     ▼
   Dashboard                            Cadastros                            Operações
      │                                     │                                     │
      │                                     │                                     │
      ▼                                     ▼                                     ▼
 Leads                         Catálogo Técnico                  Oportunidades
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
   Categorias                    Produtos                     Perfis
                                                                │
                                                                ▼
                                                        Faixas de Usuários
                                                                │
                                                                ▼
                                                        Recursos Técnicos
                                                                │
                                                                ▼
                                                         Pacotes Upgrade
                                                                │
                                                                ▼
                                                      Motor Dimensionamento
                                                                │
                                                                ▼
                                                       Motor Precificação
                                                                │
                                                                ▼
                                                            Propostas
                                                                │
                               ┌────────────────────────────────┼──────────────────────┐
                               ▼                                ▼                      ▼
                           PDF / Email                     ClickSign             Aprovação
                               │                                │
                               └────────────────────────────────┘
                                                │
                                                ▼
                                        Contrato Assinado
                                                │
               ┌────────────────────────────────┼────────────────────────────────┐
               ▼                                ▼                                ▼
          Financeiro                     Implantação                    Infraestrutura
               │                                │                                │
               ▼                                ▼                                ▼
            OMIE                         Kanban Projeto                    Proxmox


---

# Agora vamos decompor cada bloco

## 1. Leads

É apenas uma oportunidade inicial.

Ainda não existe cliente.

text
Empresa

Contato

Telefone

Email

Origem

Observações

Responsável

Status


Se a negociação evoluir:

↓

vira uma **Oportunidade**.

---

# 2. Oportunidades

Aqui começa o negócio.

text
Cliente

Parceiro

ERP

Quantidade Usuários

Vendedor

Responsável

Comentários

Histórico

Status


Ainda não existe proposta.

---

# 3. Catálogo Técnico Comercial

Aqui mora toda inteligência da empresa.

Não do vendedor.

Do gerente.

text
Categorias

↓

Produtos

↓

Perfis

↓

Faixas

↓

Recursos

↓

Upgrades


Tudo parametrizado.

---

# 4. Motor de Dimensionamento

Recebe

text
ERP

Parceiro

Usuários


Retorna

text
Servidor Banco

Servidor Aplicação

Storage

Backup

Licenças

Produtos


---

# 5. Motor de Precificação

Recebe

text
Produtos

Hardware

Licenças

Setup

Descontos


Retorna

text
Preço Mensal

Preço Setup

Margem

Valor Parceiro


---

# 6. Proposta

A proposta não calcula nada.

Ela apenas recebe o resultado dos motores.

Ela é um "snapshot" da negociação.

Isso é importante.

Se amanhã o gerente alterar um preço.

A proposta continua com os valores originais.

---

# 7. ClickSign

Fluxo automático.

text
Enviar

↓

Aguardando

↓

Assinado

↓

Concluído


---

# 8. Implantação

Recebe

text
Cliente

Produtos

Hardware

Checklist

Escopo


Sem valores.


## O Banco de Dados

Depois desse desenho ficou muito mais claro.

Na minha visão teremos aproximadamente estas tabelas.

text
NEGÓCIOS

negocios_leads

negocios_oportunidades

negocios_propostas

negocios_proposta_itens

negocios_comentarios

negocios_status


---

## Catálogo

text
produtos_categorias

produtos

produto_perfis

produto_faixas

produto_recursos

produto_upgrades


---

## Comercial

text
comercial_precos

comercial_regras

comercial_descontos


---

## Integrações

text
clicksign_documentos

clicksign_assinaturas


---
Quantidade usuários

↓

Motor

↓

Recebe Produtos

↓

Recebe Valores

↓

Gerar Proposta



---

Motor Dimensionamento

↓

Proxmox

↓

Node

↓

Cluster

↓

Provisionamento


app/

clientes/

contratos/

parceiros/

ambientes/


app/

negocios/

    catalogo/

    propostas/

    oportunidades/

    leads/

    dimensionamento/

    precificacao/



repository.py

service.py

routes.py

templates/
