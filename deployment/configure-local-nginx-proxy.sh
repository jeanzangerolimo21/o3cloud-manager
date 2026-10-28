#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${CONFIG_PATH:-/etc/nginx/sites-available/o3cloud-manager}"

log() { printf '[local-proxy] %s\n' "$*"; }
fail() { printf '[local-proxy] ERRO: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" = "0" ] || fail "Execute como root."
[ -f "$CONFIG_PATH" ] || fail "Configuracao nao encontrada: $CONFIG_PATH"
grep -q 'proxy_pass http://127.0.0.1:5000' "$CONFIG_PATH" || fail "O arquivo nao aponta para o Gunicorn local; nenhuma alteracao realizada."

backup_path="${CONFIG_PATH}.bak-$(date +%Y%m%d-%H%M%S)"
cp -a "$CONFIG_PATH" "$backup_path"

sed -i \
  -e 's/proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;/proxy_set_header X-Forwarded-For \$http_x_forwarded_for;/g' \
  -e 's/proxy_set_header X-Forwarded-Proto \$scheme;/proxy_set_header X-Forwarded-Proto https;/g' \
  "$CONFIG_PATH"

if ! nginx -t; then
  cp -a "$backup_path" "$CONFIG_PATH"
  fail "Configuracao invalida; backup restaurado de $backup_path."
fi

systemctl reload nginx
log "Proxy local atualizado. Backup: $backup_path"
