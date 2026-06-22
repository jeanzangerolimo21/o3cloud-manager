# Modelo Canônico

## O3Cloud Manager V2

Versão: 2.0

---

# Objetivo

O Modelo Canônico define a linguagem oficial utilizada pelo O3Cloud Manager.

Cada sistema integrado possui sua própria nomenclatura e estrutura de dados.

O objetivo deste documento é padronizar todos esses conceitos para que a plataforma trabalhe utilizando uma única linguagem.

O banco de dados, os Services, as APIs e os Dashboards utilizarão exclusivamente o Modelo Canônico.

---

# Sistemas Integrados

O3Cloud Manager integra informações provenientes de:

- OMIE
- Proxmox VE
- NetBox
- Proxmox Backup Server (PBS)
- Zabbix
- TrueNAS

Cada um destes sistemas continua sendo proprietário de seus próprios dados.

O O3Cloud Manager apenas sincroniza e consolida essas informações.

---

# Conceitos Oficiais

__________________________________________________________________________

## Cliente

Representa uma empresa atendida pela O3Cloud.

Origem:

- OMIE
- Manual

Um Cliente poderá possuir:

- Contratos
- Recursos
- Licenças
- Observações
- Implantações
- Timeline
- Grupos Econômicos

____________________________________________________________________________

## Grupo Econômico

Representa um conjunto de empresas pertencentes ao mesmo grupo empresarial.

Objetivo:

Consolidar indicadores financeiros e operacionais.

Exemplo

Grupo Shopping do Real

↓

Shopping do Real

↓

Doce Lar

↓

Utilitex

_____________________________________________________________________________

## Contrato

Representa um contrato comercial.

Origem:

OMIE

O O3Cloud Manager apenas complementa informações gerenciais.

Exemplos

Observações

Comissão

Licenciamento

Rateios
_____________________________________________________________________________

## Recurso

Representa qualquer ativo computacional pertencente a um cliente.

Pode representar:

- Máquina Virtual
- Container LXC
- Appliance Virtual
- Servidor Físico (futuro)
- Kubernetes (futuro)

Origem

Proxmox

NetBox

O recurso pertence obrigatoriamente a um Cliente.

_____________________________________________________________________________
## Host

Representa um servidor físico.

Possui:

Recursos

Storages

Interfaces

Monitoramento

Backups

____________________________________________________________________________

## Cluster

Representa um agrupamento de Hosts.

Origem

Proxmox

____________________________________________________________________________

## Datacenter

Representa a localização física da infraestrutura.

Exemplo

São Paulo

Campinas

Ascenty

Equinix

____________________________________________________________________________

## Backup

Representa uma cópia protegida de um Recurso.

Origem

PBS

Cada Backup pertence a um Recurso.

____________________________________________________________________________

## Licença

Representa uma licença operacional administrada pela O3Cloud.

Exemplo

O3Web

Firewall

Windows Server

SQL Server

Linux Comercial

____________________________________________________________________________

## Implantação

Representa o processo de implantação de um cliente.

Possui:

Status

Responsável

Checklist

Documentação

Observações

____________________________________________________________________________

## Timeline

Registro cronológico dos principais eventos.

Exemplos

Cliente criado

Contrato sincronizado

VM criada

Backup habilitado

Licença adicionada

Grupo Econômico alterado

Implantação concluída

_____________________________________________________________________________

## Rentabilidade

Representa um indicador gerencial.

Nunca substitui DRE.

Pode ser calculada por:

Cliente

Grupo Econômico

Host

Cluster

Datacenter

____________________________________________________________________________

## Usuário

Pessoa autorizada a utilizar o sistema.

Possui:

Perfil

Permissões

Auditoria

____________________________________________________________________________
 _________________________________________________
| Sistema | Nome Original   | O3Cloud Manager    |
| ------- | --------------- | ------------------ |
| Proxmox | VM              | Recurso            |
| Proxmox | LXC             | Recurso            |
| NetBox  | Virtual Machine | Recurso            |
| PBS     | Backup          | Backup             |
| Zabbix  | Host            | Recurso Monitorado |
| OMIE    | Cliente         | Cliente            |
| OMIE    | Contrato        | Contrato           |
|_________|_________________|____________________|
