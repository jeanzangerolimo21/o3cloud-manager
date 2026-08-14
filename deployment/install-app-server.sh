#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/o3cloud-manager}"
APP_USER="${APP_USER:-o3cloud}"
REPO_URL="${REPO_URL:-https://github.com/jeanzangerolimo21/o3cloud-manager.git}"
BRANCH="${BRANCH:-beta}"
DB_HOST="${DB_HOST:-}"
DB_PORT="${DB_PORT:-3306}"
DB_NAME="${DB_NAME:-o3cloud_manager}"
DB_USER="${DB_USER:-o3manager}"
DB_PASSWORD="${DB_PASSWORD:-}"
SECRET_KEY="${SECRET_KEY:-}"
PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-http://$(hostname -I | awk '{print $1}')}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-3}"
APPLY_MIGRATIONS="${APPLY_MIGRATIONS:-0}"
INSTALL_NGINX="${INSTALL_NGINX:-1}"

log() { printf '[app-install] %s\n' "$*"; }
fail() { printf '[app-install] ERRO: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" = "0" ] || fail "Execute como root."
[ -n "$DB_HOST" ] || fail "Defina DB_HOST com o IP/hostname do servidor de banco."
[ -n "$DB_PASSWORD" ] || fail "Defina DB_PASSWORD com a senha do usuario do banco."
if [ -z "$SECRET_KEY" ]; then
  SECRET_KEY="$(openssl rand -hex 32)"
fi

export DEBIAN_FRONTEND=noninteractive
log "Atualizando pacotes e instalando dependencias do servidor de aplicacao."
apt-get update
apt-get install -y git python3 python3-venv python3-pip python3-dev build-essential pkg-config default-libmysqlclient-dev mariadb-client curl ca-certificates ufw cron nginx

if ! id "$APP_USER" >/dev/null 2>&1; then
  log "Criando usuario $APP_USER."
  useradd --system --create-home --home-dir /home/$APP_USER --shell /bin/bash "$APP_USER"
fi

if [ ! -d "$APP_DIR/.git" ]; then
  log "Clonando $REPO_URL branch $BRANCH em $APP_DIR."
  mkdir -p "$(dirname "$APP_DIR")"
  git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
else
  log "Repositorio ja existe em $APP_DIR; atualizando branch $BRANCH."
  git -C "$APP_DIR" fetch origin "$BRANCH"
  git -C "$APP_DIR" checkout "$BRANCH"
  git -C "$APP_DIR" pull --ff-only origin "$BRANCH"
fi

cd "$APP_DIR"
mkdir -p storage logs backups
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod 0750 logs storage backups

log "Criando venv e instalando requirements."
python3 -m venv venv
venv/bin/pip install --upgrade pip wheel setuptools
venv/bin/pip install -r requirements.txt
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

log "Gerando .env de producao apontando para banco remoto."
cat >.env <<EOF
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
MYSQLDUMP_PATH=/usr/bin/mysqldump
OMIE_APP_KEY=${OMIE_APP_KEY:-}
OMIE_APP_SECRET=${OMIE_APP_SECRET:-}
PROXMOX_VERIFY_SSL=False
GITHUB_TOKEN=${GITHUB_TOKEN:-}
LOG_LEVEL=INFO
PUBLIC_BASE_URL=${PUBLIC_BASE_URL}
EMAIL_MARKETING_LOGO_URL=${EMAIL_MARKETING_LOGO_URL:-https://o3cloud.com.br/wp-content/uploads/2025/04/Ativo-3.png}
EMAIL_MARKETING_PUBLIC_BASE_URL=${EMAIL_MARKETING_PUBLIC_BASE_URL:-$PUBLIC_BASE_URL}
TRUST_PROXY=1
PROXY_FIX_HOPS=1
COFRE_COMPARTILHAMENTO_TTL_MINUTOS=5
EOF
chown "$APP_USER:$APP_USER" .env
chmod 0640 .env

log "Instalando servico systemd."
sed "s/--workers 3/--workers ${GUNICORN_WORKERS}/" deployment/o3cloud-manager.service >/etc/systemd/system/o3cloud-manager.service
systemctl daemon-reload
systemctl enable o3cloud-manager.service

log "Instalando cron operacional."
install -o root -g root -m 0644 deployment/o3cloud-manager.cron /etc/cron.d/o3cloud-manager
systemctl enable cron
systemctl restart cron

if [ "$INSTALL_NGINX" = "1" ]; then
  log "Configurando Nginx como proxy reverso."
  cat >/etc/nginx/sites-available/o3cloud-manager <<'EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 50m;

    location /static/ {
        alias /opt/o3cloud-manager/app/static/;
        expires 7d;
        access_log off;
    }

    location /storage/ {
        proxy_pass http://127.0.0.1:5000/storage/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }
}
EOF
  ln -sfn /etc/nginx/sites-available/o3cloud-manager /etc/nginx/sites-enabled/o3cloud-manager
  rm -f /etc/nginx/sites-enabled/default
  nginx -t
  systemctl enable nginx
  systemctl reload nginx
fi

log "Validando conexao com banco remoto."
export MYSQL_PWD="$DB_PASSWORD"
mysql --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" --database "$DB_NAME" --execute "SELECT 1" >/dev/null

if [ "$APPLY_MIGRATIONS" = "1" ]; then
  log "Aplicando migrations."
  APP_DIR="$APP_DIR" deployment/apply-migrations.sh
fi

chown -R "$APP_USER:$APP_USER" storage logs backups
systemctl restart o3cloud-manager.service

ufw allow OpenSSH >/dev/null || true
ufw allow 80/tcp >/dev/null || true
ufw allow 443/tcp >/dev/null || true

log "Instalacao da aplicacao concluida."
log "Teste local: curl -I http://127.0.0.1:5000/login"
log "Teste via Nginx: curl -I ${PUBLIC_BASE_URL}/login"
