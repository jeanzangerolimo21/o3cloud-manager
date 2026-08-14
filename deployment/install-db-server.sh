#!/usr/bin/env bash
if [ -z "${BASH_VERSION:-}" ]; then
  exec bash "$0" "$@"
fi
set -euo pipefail

DB_NAME="${DB_NAME:-o3cloud_manager}"
DB_USER="${DB_USER:-o3manager}"
DB_PASSWORD="${DB_PASSWORD:-}"
APP_SERVER_CIDR="${APP_SERVER_CIDR:-}"
DB_BIND_ADDRESS="${DB_BIND_ADDRESS:-0.0.0.0}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_INNODB_BUFFER_POOL_SIZE="${MYSQL_INNODB_BUFFER_POOL_SIZE:-2G}"

log() { printf '[db-install] %s\n' "$*"; }
fail() { printf '[db-install] ERRO: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" = "0" ] || fail "Execute como root."
[ -n "$DB_PASSWORD" ] || fail "Defina DB_PASSWORD. Exemplo: DB_PASSWORD='senha-forte' APP_SERVER_CIDR='10.0.0.20' $0"
[ -n "$APP_SERVER_CIDR" ] || fail "Defina APP_SERVER_CIDR com o IP/CIDR do servidor de aplicacao. Exemplo: 10.0.0.20 ou 10.0.0.%"
[[ "$DB_NAME" =~ ^[A-Za-z0-9_]+$ ]] || fail "DB_NAME deve conter apenas letras, numeros e underscore."
[[ "$DB_USER" =~ ^[A-Za-z0-9_]+$ ]] || fail "DB_USER deve conter apenas letras, numeros e underscore."
case "$DB_PASSWORD$APP_SERVER_CIDR" in *"'"*) fail "DB_PASSWORD e APP_SERVER_CIDR nao podem conter aspas simples." ;; esac

export DEBIAN_FRONTEND=noninteractive
log "Atualizando pacotes e instalando MariaDB."
apt-get update
apt-get install -y mariadb-server mariadb-client ufw ca-certificates curl gnupg lsb-release

log "Configurando MariaDB para aceitar conexoes do servidor de aplicacao."
cat >/etc/mysql/mariadb.conf.d/60-o3cloud-server.cnf <<EOF
[mysqld]
bind-address = ${DB_BIND_ADDRESS}
port = ${MYSQL_PORT}
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
max_connections = 150
innodb_buffer_pool_size = ${MYSQL_INNODB_BUFFER_POOL_SIZE}
innodb_log_file_size = 256M
slow_query_log = 1
slow_query_log_file = /var/log/mysql/o3cloud-slow.log
long_query_time = 2
EOF

systemctl enable mariadb
systemctl restart mariadb

log "Criando banco, usuario da aplicacao e removendo defaults inseguros."
mysql <<SQL
DELETE FROM mysql.user WHERE User='';
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'${APP_SERVER_CIDR}' IDENTIFIED BY '${DB_PASSWORD}';
ALTER USER '${DB_USER}'@'${APP_SERVER_CIDR}' IDENTIFIED BY '${DB_PASSWORD}';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP, REFERENCES, CREATE TEMPORARY TABLES, LOCK TABLES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'${APP_SERVER_CIDR}';
FLUSH PRIVILEGES;
SQL

log "Configurando firewall local, se UFW estiver ativo/disponivel."
ufw allow OpenSSH >/dev/null || true
ufw allow from "$APP_SERVER_CIDR" to any port "$MYSQL_PORT" proto tcp >/dev/null || true

cat >/root/o3cloud-db.env <<EOF
DB_HOST=$(hostname -I | awk '{print $1}')
DB_PORT=${MYSQL_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
APP_SERVER_CIDR=${APP_SERVER_CIDR}
EOF
chmod 0600 /root/o3cloud-db.env

log "Instalacao do banco concluida. Credenciais salvas em /root/o3cloud-db.env."
log "Use DB_HOST=$(hostname -I | awk '{print $1}') no servidor de aplicacao."
