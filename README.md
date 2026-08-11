# O3Cloud Manager

> Plataforma de Gestão Operacional, Financeira e de Infraestrutura da O3Cloud.

---

## Sobre o projeto

O O3Cloud Manager é um ERP desenvolvido para centralizar a gestão financeira e operacional da infraestrutura da O3Cloud.

Seu principal objetivo é consolidar informações provenientes de diversos sistemas da empresa, transformando dados técnicos em indicadores financeiros e gerenciais.

O sistema integra plataformas como OMIE, Proxmox, Proxmox Backup Server, NetBox, Zabbix e TrueNAS para fornecer uma visão completa da operação.

---

## Principais funcionalidades

### Financeiro

* Gestão de Clientes
* Contratos OMIE
* Clientes Manuais
* Grupos Econômicos
* Rateios Financeiros
* Custos
* Rentabilidade
* Dashboards
* Relatórios

### Infraestrutura

* Clusters Proxmox
* Hosts
* Máquinas Virtuais
* Containers LXC
* Backups PBS
* Inventário NetBox
* Monitoramento Zabbix

### Administração

* Usuários
* Permissões
* Auditoria
* Configurações

---

## Arquitetura

```
OMIE
      │
      ▼
Clientes
Contratos
Receitas
      │
      ▼
O3Cloud Manager
      │
      ▼
Dashboards
Relatórios
Rentabilidade
```

---

## Tecnologias

* Ubuntu Server 24.04 LTS
* Python 3.12
* Flask
* Gunicorn
* Nginx
* MariaDB
* Bootstrap 5

---

## Integrações

* OMIE
* Proxmox VE
* Proxmox Backup Server
* NetBox
* Zabbix
* TrueNAS

---

## Operação como Serviço

Em produção, o Flask deve rodar como daemon `systemd` com `gunicorn`, usando o usuário `o3cloud`, e não por `python app.py` em modo debug.

Arquivos operacionais:

```text
deployment/o3cloud-manager.service
deployment/install-systemd-service.sh
docs/38-SERVICO-SYSTEMD.md
```

Instalação como `root`:

```bash
cd /opt/o3cloud-manager
deployment/install-systemd-service.sh
```

## Documentação

Toda a documentação técnica está disponível na pasta **docs/**.

---

## Roadmap

A evolução do projeto encontra-se em:

```
docs/10-ROADMAP.md
```

---

## Licença

Projeto interno da O3Cloud.

Todos os direitos reservados.

## Status do Projeto

Versão atual:

**v2.0.0-alpha**

### Concluído

- Arquitetura
- Banco de Dados
- Documentação
- Estrutura do Projeto

### Em Desenvolvimento

- Backend Flask
- Dashboard
- Integrações

### Roadmap

- Sprint 4 — Interface Web
- Sprint 5 — Integrações
- Sprint 6 — Indicadores Executivos
