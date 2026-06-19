# Arquitetura

## Visão Geral

O O3Cloud Manager utiliza arquitetura modular baseada em Flask Blueprints e separação em camadas.

Cada módulo possui responsabilidades bem definidas.

---

# Camadas


Interface Web

↓

Blueprints (Routes)

↓

Services

↓

Repositories

↓

Banco de Dados


---

# Estrutura da Aplicação


app.py

↓

Routes

↓

Services

↓

Repositories

↓

MariaDB


---

# Arquitetura Funcional


                    O3Cloud Manager

                           │

        ┌──────────────────┼──────────────────┐

        │                  │                  │

   Financeiro         Infraestrutura      Administração

        │                  │                  │

 Clientes         Clusters Proxmox       Usuários

 Contratos        Hosts                  Permissões

 Receitas         Máquinas Virtuais      Auditoria

 Rateios          Containers LXC         Configurações

 Custos           PBS

 Rentabilidade    NetBox

 Dashboards       Zabbix

 Relatórios


---

# Arquitetura das Integrações


                OMIE
                  │
                  ▼

Clientes ---- Contratos

                  │

                  ▼

           O3Cloud Manager

                  │

   ┌──────────────┼──────────────┐

   ▼              ▼              ▼

Financeiro   Infraestrutura   Dashboards

                  ▲

                  │

      NetBox  Proxmox  PBS  Zabbix
```

---

# Princípios

* Separação entre interface e regras de negócio.
* Serviços especializados por domínio.
* Banco de dados centralizado.
* Integrações desacopladas.
* Toda integração sincroniza primeiro para o banco local.
* Dashboards consultam apenas o banco local.
* Nenhuma tela consulta APIs externas diretamente.

