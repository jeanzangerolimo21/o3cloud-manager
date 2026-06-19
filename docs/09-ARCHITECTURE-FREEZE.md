# Architecture Freeze

## Versão 2.0

Este documento registra as decisões arquiteturais aprovadas para a V2.

Alterações deverão ser realizadas apenas mediante nova RFC.

---

## Decisão 001

O O3Cloud Manager não substituirá sistemas especialistas.

---

## Decisão 002

Toda integração sincroniza para banco local.

Nenhuma tela consulta APIs externas.

---

## Decisão 003

Toda informação possui um sistema proprietário.

OMIE

Financeiro

NetBox

Inventário

Proxmox

Virtualização

PBS

Backup

Zabbix

Monitoramento

O3Cloud Manager

Gestão Gerencial

---

## Decisão 004

Relacionamentos utilizarão identificadores únicos.

Nunca nomes ou prefixos.

---

## Decisão 005

Clientes poderão ser:

OMIE

Manual

---

## Decisão 006

Grupos Econômicos consolidam informações.

Nunca duplicam dados.

---

## Decisão 007

Rentabilidade representa indicador gerencial.

Não substitui DRE.

---

## Decisão 008

Toda regra de negócio ficará na camada Services.

---

## Decisão 009

Todo módulo deverá produzir indicadores para tomada de decisão.

---

## Decisão 010

O desenvolvimento seguirá obrigatoriamente:

Documentação

↓

Arquitetura

↓

Banco

↓

Services

↓

Rotas

↓

Templates

↓

Testes

