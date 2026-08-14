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

Executar como `root` no servidor de banco em modo interativo:

```bash
sudo bash deployment/install-db-server.sh
```

O script perguntara os campos obrigatorios que nao forem informados, como senha do banco e IP/CIDR do servidor de aplicacao.

Para execucao automatizada:

```bash
sudo env \
  DB_NAME=o3cloud_manager \
  DB_USER=o3manager \
  DB_PASSWORD='trocar-por-senha-forte' \
  APP_SERVER_CIDR='IP_DO_APP01' \
  MYSQL_INNODB_BUFFER_POOL_SIZE=2G \
  bash deployment/install-db-server.sh
```

O script salva as credenciais em:

```text
/root/o3cloud-db.env
```

Usar o `DB_HOST` exibido/salvo para configurar o servidor de aplicacao.

### 2. Servidor app01

Executar como `root` no servidor da aplicacao em modo interativo:

```bash
sudo bash deployment/install-app-server.sh
```

O script perguntara os campos obrigatorios que nao forem informados, como IP/hostname do banco e senha do usuario do banco.

Para execucao automatizada:

```bash
sudo env \
  DB_HOST='IP_DO_DB01' \
  DB_PORT=3306 \
  DB_NAME=o3cloud_manager \
  DB_USER=o3manager \
  DB_PASSWORD='mesma-senha-configurada-no-db01' \
  PUBLIC_BASE_URL='https://beta.seudominio.com.br' \
  BRANCH=beta \
  APPLY_MIGRATIONS=1 \
  bash deployment/install-app-server.sh
```

Se o banco for restaurado de backup ja atualizado, `APPLY_MIGRATIONS=1` pode continuar habilitado: o runner ignora migrations ja registradas.

Observação: executar os scripts com `bash`, não com `sh`. O `sh` do Ubuntu/Debian não suporta `set -o pipefail`.

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

## Restauracao do ambiente atual

Para migrar o ambiente atual para os novos servidores, usar preferencialmente um backup completo gerado em:

```text
Configurações > Backups do Sistema
```

Fluxo recomendado:

1. No ambiente atual, gerar backup completo ou localizar o artefato em `storage/backups/sistema`.
2. Instalar `db01` com `deployment/install-db-server.sh`.
3. Instalar `app01` com `deployment/install-app-server.sh` apontando para o `db01`.
4. Acessar o novo `app01` como Administrador.
5. Abrir `Configurações > Backups do Sistema > Restauração de backup`.
6. Enviar o artefato completo `.tar.gz` ou `.tgz`.
7. Marcar `Banco de dados` e `Storage`.
8. Digitar `RESTAURAR` no campo de confirmação.
9. Executar `deployment/healthcheck.sh` no `app01`.

Observações:

- Arquivos `.sql` e `.sql.gz` restauram somente o banco; nesse caso o storage precisa ser copiado por outro procedimento.
- Ao restaurar storage pela tela, o artefato precisa conter `storage.tar.gz`.
- A tela cria uma cópia local de segurança do storage anterior em `storage/backups/pre-restore`.
- Em servidor novo, o uso de `--skip-service` pelo restore da tela evita interromper o serviço durante a requisição; se houver usuários conectados, usar janela de manutenção.

## Observacoes operacionais

- O storage oficial da aplicacao fica em `/opt/o3cloud-manager/storage` no `app01`.
- Backups devem incluir banco e storage.
- A branch de homologacao Beta publicada no GitHub e `beta`.
- A branch `main` deve continuar reservada para producao final.
- Para HTTPS, instalar certificado no Nginx apos apontar DNS para `app01`.
