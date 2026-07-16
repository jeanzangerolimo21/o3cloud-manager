# O3Cloud Manager v3.0

# 03 - ARQUITETURA

Versão: 3.0 Alpha

Última atualização: Julho/2026

Status: Oficial

---

# Objetivo

Este documento define a arquitetura oficial do O3Cloud Manager.

Toda implementação deverá obrigatoriamente seguir os padrões aqui definidos.

Nenhum módulo poderá desrespeitar esta arquitetura sem aprovação explícita.

---

# Filosofia

O projeto foi desenvolvido seguindo os seguintes princípios:

- Simplicidade
- Baixo acoplamento
- Alta coesão
- Código reutilizável
- Componentização
- Facilidade de manutenção
- Evolução incremental

A arquitetura prioriza previsibilidade.

Todo módulo deve possuir exatamente a mesma estrutura.

---

# Arquitetura Geral

Todo módulo segue obrigatoriamente:

```
Browser

↓

Routes

↓

Service

↓

Repository

↓

MariaDB
```

Cada camada possui uma única responsabilidade.

---

# Camadas

## Routes

Responsável por:

- Receber Requests
- Ler parâmetros
- Chamar Services
- Flash Messages
- Redirects
- Renderizar Templates

Nunca deve:

- Fazer SQL
- Conter regra de negócio
- Validar dados complexos

Toda regra pertence ao Service.

---

## Service

Responsável por:

- Regras de negócio
- Validações
- Normalizações
- Consistência
- Orquestração

O Service nunca conhece:

- Flask
- Request
- HTML
- Banco de Dados

Toda persistência é realizada pelo Repository.

---

## Repository

Responsável exclusivamente por acesso ao banco.

Pode executar:

SELECT

INSERT

UPDATE

Soft Delete

Nunca deve:

- Fazer validações
- Conhecer Flask
- Conhecer HTML
- Possuir regra de negócio

Todo Repository herda obrigatoriamente:

BaseRepository

---

## Banco de Dados

Banco oficial:

MariaDB

Princípios:

- SQL puro
- Sem ORM
- Prepared Statements
- UUID obrigatório
- Soft Delete
- Timestamp automático

---

# BaseRepository

Todos os repositories herdam de:

BaseRepository

Funcionalidades disponíveis:

- connection()
- close()
- generate_uuid()
- bool_to_int()

Nenhum Repository deverá duplicar estas funções.

---

# Organização dos Módulos

Todo módulo segue obrigatoriamente:

```
modulo/

repository.py

service.py

routes.py

templates/

index.html

form.html

view.html
```

Nunca alterar esta estrutura.

---

# Fluxo de Desenvolvimento

Toda implementação segue exatamente:

Repository

↓

Service

↓

Routes

↓

Templates

↓

Testes

↓

Homologação

↓

Git Commit

↓

Próxima tarefa

Nunca desenvolver várias etapas simultaneamente.

---

# Componentização

Todo HTML deve reutilizar componentes compartilhados.

Componentes homologados:

```
components/

alert.html

crud_actions.html

filter_bar.html

page_header.html
```

Templates base:

```
crud/

index_base.html

form_base.html

view_base.html
```

Não criar HTML duplicado.

---

# Reutilização

Sempre reutilizar código existente.

Antes de criar:

- Repository
- Service
- Template

verificar se já existe implementação semelhante.

Produtos reutilizam Categorias.

Modelos reutilizam Produtos.

Faixas reutilizam Modelos.

Servidores reutilizam Faixas.

---

# CRUD Padrão

Todo CRUD deve possuir:

Repository

Service

Routes

Templates

index.html

form.html

view.html

Funcionalidades mínimas:

- Listar
- Buscar
- Inserir
- Atualizar
- Visualizar
- Desativar
- Reativar

---

# Exclusão

DELETE físico é proibido.

Sempre utilizar:

```
UPDATE tabela
SET ativo = 0
```

---

# UUID

Todo cadastro deve possuir UUID.

Nunca utilizar apenas ID numérico.

Relacionamentos externos utilizarão UUID quando necessário.

---

# Estrutura dos Templates

Todo CRUD utiliza:

index_base.html

↓

page_header.html

↓

filter_bar.html

↓

crud_actions.html

↓

alert.html

Nenhum CRUD deve criar layout próprio.

---

# Banco de Dados

Toda tabela deverá seguir o padrão:

id

uuid

ativo

created_at

updated_at

created_by

updated_by

Sempre que aplicável.

---

# Tratamento de Erros

Repository

Lança exceções técnicas.

Service

Converte para regras de negócio.

Routes

Exibe Flash Messages.

Templates

Nunca tratam exceções.

---

# Integrações

As integrações nunca devem conter regra de negócio.

Exemplo:

OMIE

↓

ClienteRepository

↓

ClienteService

Nunca:

OMIE

↓

Routes

---

# Estrutura Atual

```
app/

administracao/

ambientes/

catalogo/

clientes/

contratos/

financeiro/

negocios/

core/

repositories/

templates/
```

---

# Catálogo Técnico

Ordem oficial:

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

↓

Precificação

---

# CRM Comercial

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

Catálogo

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

O sistema possui integração com:

OMIE

Proxmox

ClickSign

Base44

PBS (Planejado)

NetBox (Planejado)

Cada integração possui módulo próprio.

---

# Escalabilidade

Toda nova funcionalidade deverá:

Reutilizar componentes.

Reutilizar Repository.

Reutilizar Service.

Seguir os padrões existentes.

Nunca criar arquitetura paralela.

---

# Compatibilidade

Nenhuma alteração poderá quebrar:

Componentes homologados.

Architecture Freeze.

Roadmap.

Padrões.

Banco homologado.

---

# Objetivo Final

Todo desenvolvedor (humano ou IA) deve ser capaz de compreender a arquitetura do projeto apenas lendo este documento.

Toda implementação futura deverá seguir integralmente esta arquitetura.

Este documento é considerado a Constituição Arquitetural do O3Cloud Manager.
