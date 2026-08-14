# 47 - Instalacao Beta em Servidores Separados

Ultima atualizacao: 14/08/2026

## Objetivo

Separar a versao Beta do O3Cloud Manager em dois servidores:

- `db01`: banco MariaDB/MySQL.
- `app01`: aplicacao Flask/Gunicorn/Nginx e storage de arquivos.

## Requisitos recomendados

### db01

- 4 vCPU.
- 8 GB RAM.
- 100 GB SSD/NVMe.
- Ubuntu Server 24.04 LTS ou Debian 12.
- Backup externo habilitado.

### app01

- 4 vCPU.
- 8 GB RAM.
- 60 GB SSD para sistema.
- 100 GB para `/opt/o3cloud-manager/storage`, expansivel.
- Ubuntu Server 24.04 LTS ou Debian 12.

## Scripts criados

- `deployment/install-db-server.sh`: instala MariaDB, cria banco, cria usuario remoto da aplicacao e libera firewall para o servidor de aplicacao.
- `deployment/install-app-server.sh`: instala dependencias da aplicacao, clona a branch `beta`, cria venv, configura `.env`, systemd, cron e Nginx.
- `deployment/apply-migrations.sh`: aplica migrations SQL ainda nao registradas em `schema_migrations`.

## Ordem de instalacao

### 1. Servidor db01

Executar como `root` no servidor de banco:

```bash
export DB_NAME=o3cloud_manager
export DB_USER=o3manager
export DB_PASSWORD='trocar-por-senha-forte'
export APP_SERVER_CIDR='IP_DO_APP01'
export MYSQL_INNODB_BUFFER_POOL_SIZE=2G
deployment/install-db-server.sh
```

O script salva as credenciais em:

```text
/root/o3cloud-db.env
```

Usar o `DB_HOST` exibido/salvo para configurar o servidor de aplicacao.

### 2. Servidor app01

Executar como `root` no servidor da aplicacao:

```bash
export DB_HOST='IP_DO_DB01'
export DB_PORT=3306
export DB_NAME=o3cloud_manager
export DB_USER=o3manager
export DB_PASSWORD='mesma-senha-configurada-no-db01'
export PUBLIC_BASE_URL='https://beta.seudominio.com.br'
export BRANCH=beta
export APPLY_MIGRATIONS=1
deployment/install-app-server.sh
```

Se o banco for restaurado de backup ja atualizado, `APPLY_MIGRATIONS=1` pode continuar habilitado: o runner ignora migrations ja registradas.

## Validacao apos instalacao

No `app01`:

```bash
deployment/healthcheck.sh
systemctl status o3cloud-manager --no-pager
curl -I http://127.0.0.1:5000/login
```

No `db01`:

```bash
systemctl status mariadb --no-pager
mysql -e "SHOW DATABASES LIKE 'o3cloud_manager';"
```

## Observacoes operacionais

- O storage oficial da aplicacao fica em `/opt/o3cloud-manager/storage` no `app01`.
- Backups devem incluir banco e storage.
- A branch de homologacao Beta publicada no GitHub e `beta`.
- A branch `main` deve continuar reservada para producao final.
- Para HTTPS, instalar certificado no Nginx apos apontar DNS para `app01`.
