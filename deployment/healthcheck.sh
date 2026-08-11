#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/o3cloud-manager}"
SERVICE_NAME="${SERVICE_NAME:-o3cloud-manager.service}"
HEALTHCHECK_URL="${HEALTHCHECK_URL:-http://127.0.0.1:5000/login}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-10}"

log() {
  printf '[healthcheck] %s\n' "$*"
}

fail() {
  printf '[healthcheck] ERRO: %s\n' "$*" >&2
  exit 1
}

[ -d "$APP_DIR" ] || fail "APP_DIR invalido: $APP_DIR"
cd "$APP_DIR"

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

if command -v systemctl >/dev/null 2>&1; then
  if ! systemctl is-active --quiet "$SERVICE_NAME"; then
    fail "Servico $SERVICE_NAME nao esta ativo."
  fi
  log "Servico $SERVICE_NAME ativo."
fi

if [ -n "${DB_HOST:-}" ] && [ -n "${DB_PORT:-}" ] && [ -n "${DB_USER:-}" ] && [ -n "${DB_PASSWORD:-}" ] && [ -n "${DB_NAME:-}" ]; then
  MYSQL_BIN="${MYSQL_PATH:-}"
  if [ -z "$MYSQL_BIN" ] || [ ! -x "$MYSQL_BIN" ]; then
    MYSQL_BIN="$(command -v mysql || true)"
  fi
  if [ -z "$MYSQL_BIN" ] && [ -x /usr/bin/mysql ]; then
    MYSQL_BIN=/usr/bin/mysql
  fi
  [ -n "$MYSQL_BIN" ] || fail "mysql nao encontrado para validar banco."
  export MYSQL_PWD="$DB_PASSWORD"
  "$MYSQL_BIN" --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" --database "$DB_NAME" --execute "SELECT 1" >/dev/null
  log "Banco $DB_NAME respondeu."
else
  log "Variaveis DB_* incompletas; validacao de banco ignorada."
fi

HTTP_CODE="$(curl --silent --show-error --location --max-time "$TIMEOUT_SECONDS" --output /dev/null --write-out '%{http_code}' "$HEALTHCHECK_URL")" || fail "Falha HTTP em $HEALTHCHECK_URL."
case "$HTTP_CODE" in
  200|204|301|302)
    log "HTTP $HTTP_CODE em $HEALTHCHECK_URL."
    ;;
  *)
    fail "Resposta HTTP inesperada $HTTP_CODE em $HEALTHCHECK_URL."
    ;;
esac

log "OK"
