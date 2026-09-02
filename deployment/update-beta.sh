#!/usr/bin/env bash
if [ -z "${BASH_VERSION:-}" ]; then
  exec bash "$0" "$@"
fi
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/o3cloud-manager}"
APP_USER="${APP_USER:-o3cloud}"
BRANCH="${UPDATE_BRANCH:-${BRANCH:-beta}}"
REMOTE="${UPDATE_REMOTE:-origin}"
SERVICE_NAME="${SERVICE_NAME:-o3cloud-manager.service}"
BACKUP_DIR="${BACKUP_DIR:-$APP_DIR/backups}"
LOG_DIR="${LOG_DIR:-$APP_DIR/logs}"
LOCK_DIR="${LOCK_DIR:-/tmp/o3cloud-manager-update.lock}"
SKIP_BACKUP="${SKIP_BACKUP:-0}"

log() { printf '[update-beta] %s\n' "$*"; }
fail() { printf '[update-beta] ERRO: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" = "0" ] || fail "Execute como root. Pela tela, instale o runner sudoers com deployment/install-update-runner.sh."
[ -d "$APP_DIR/.git" ] || fail "Repositorio Git nao encontrado em $APP_DIR."
[ -d "$APP_DIR/venv" ] || fail "venv nao encontrado em $APP_DIR/venv."

mkdir -p "$LOG_DIR" "$BACKUP_DIR"
chown -R "$APP_USER:$APP_USER" "$LOG_DIR" "$BACKUP_DIR"
LOG_FILE="$LOG_DIR/update-beta-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  fail "Ja existe uma atualizacao em andamento ($LOCK_DIR)."
fi
cleanup() { rmdir "$LOCK_DIR" 2>/dev/null || true; }
trap cleanup EXIT

cd "$APP_DIR"
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

run_app() {
  runuser -u "$APP_USER" -- env HOME="/home/$APP_USER" "$@"
}

git_app() {
  run_app git -C "$APP_DIR" "$@"
}

log "Iniciando atualizacao da branch $BRANCH em $APP_DIR. Log: $LOG_FILE"

alteracoes="$(git_app status --short)"
if [ -n "$alteracoes" ]; then
  printf '%s\n' "$alteracoes"
  fail "Worktree com alteracoes locais. Commit/stash antes de atualizar."
fi

log "Consultando remoto $REMOTE/$BRANCH."
git_app fetch "$REMOTE" "$BRANCH" --tags
commit_atual="$(git_app rev-parse HEAD)"
commit_alvo="$(git_app rev-parse "$REMOTE/$BRANCH")"
log "Commit atual: $commit_atual"
log "Commit alvo:  $commit_alvo"

if [ "$SKIP_BACKUP" != "1" ]; then
  : "${DB_HOST:?DB_HOST ausente}"
  : "${DB_PORT:?DB_PORT ausente}"
  : "${DB_NAME:?DB_NAME ausente}"
  : "${DB_USER:?DB_USER ausente}"
  : "${DB_PASSWORD:?DB_PASSWORD ausente}"
  MYSQLDUMP_BIN="${MYSQLDUMP_PATH:-$(command -v mysqldump || true)}"
  [ -n "$MYSQLDUMP_BIN" ] || fail "mysqldump nao encontrado."

  tmpdir="$(mktemp -d -t o3update-backup-XXXXXX)"
  backup_file="$BACKUP_DIR/o3cloud-pre-update-$(date +%Y%m%d-%H%M%S).tar.gz"
  log "Gerando backup pre-update em $backup_file."
  export MYSQL_PWD="$DB_PASSWORD"
  "$MYSQLDUMP_BIN" --single-transaction --routines --triggers --events --default-character-set=utf8mb4 \
    --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" "$DB_NAME" | gzip > "$tmpdir/database.sql.gz"
  gzip -t "$tmpdir/database.sql.gz"
  if [ -d "$APP_DIR/storage" ]; then
    tar -czf "$tmpdir/storage.tar.gz" -C "$APP_DIR/storage" --exclude=backups .
  fi
  cat >"$tmpdir/manifest.json" <<EOF
{"tipo":"PRE_UPDATE","branch":"$BRANCH","commit_atual":"$commit_atual","commit_alvo":"$commit_alvo","gerado_em":"$(date -Iseconds)"}
EOF
  tar -czf "$backup_file" -C "$tmpdir" .
  rm -rf "$tmpdir"
  chown "$APP_USER:$APP_USER" "$backup_file"
fi

if [ "$commit_atual" != "$commit_alvo" ]; then
  log "Atualizando codigo com fast-forward."
  git_app checkout "$BRANCH"
  git_app pull --ff-only "$REMOTE" "$BRANCH"
else
  log "Codigo ja esta no commit alvo."
fi

log "Instalando dependencias Python."
run_app "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

log "Aplicando migrations."
APP_DIR="$APP_DIR" bash "$APP_DIR/deployment/apply-migrations.sh"

log "Atualizando cron operacional."
install -o root -g root -m 0644 "$APP_DIR/deployment/o3cloud-manager.cron" /etc/cron.d/o3cloud-manager
systemctl reload cron 2>/dev/null || systemctl restart cron 2>/dev/null || true

log "Ajustando permissoes operacionais."
mkdir -p "$APP_DIR/storage" "$APP_DIR/logs" "$APP_DIR/backups"
chown -R "$APP_USER:$APP_USER" "$APP_DIR/storage" "$APP_DIR/logs" "$APP_DIR/backups"
chmod 0750 "$APP_DIR/storage" "$APP_DIR/logs" "$APP_DIR/backups"

log "Reiniciando $SERVICE_NAME."
systemctl restart "$SERVICE_NAME"

log "Executando healthcheck."
"$APP_DIR/deployment/healthcheck.sh"

log "Atualizacao concluida com sucesso."
