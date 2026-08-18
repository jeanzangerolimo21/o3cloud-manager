#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/o3cloud-manager}"
SERVICE_NAME="${SERVICE_NAME:-o3cloud-manager.service}"
SAFETY_BACKUP_DIR="${SAFETY_BACKUP_DIR:-$APP_DIR/storage/backups/pre-restore}"
TMP_DIR=""
ASSUME_YES=0
SKIP_SERVICE=0
SKIP_SAFETY_BACKUP=0
BACKUP_FILE=""

usage() {
  cat <<USAGE
Uso: $0 <backup.sql|backup.sql.gz|o3cloud-backup-*.tar.gz> [opcoes]

Opcoes:
  --yes                 confirma a restauracao destrutiva
  --skip-service        nao para/inicia o servico systemd
  --skip-safety-backup  nao gera dump de seguranca antes do restore

Variaveis:
  APP_DIR               diretorio da aplicacao (padrao: /opt/o3cloud-manager)
  SERVICE_NAME          unit systemd (padrao: o3cloud-manager.service)
  RESTORE_CONFIRM       deve ser igual ao nome do banco para execucao nao interativa
  MYSQL_PATH            caminho absoluto do cliente mysql, se necessario
  MYSQLDUMP_PATH        caminho absoluto do mysqldump, se necessario
USAGE
}

log() {
  printf '[restore-db] %s\n' "$*"
}

fail() {
  printf '[restore-db] ERRO: %s\n' "$*" >&2
  exit 1
}

cleanup() {
  if [ -n "$TMP_DIR" ] && [ -d "$TMP_DIR" ]; then
    rm -rf "$TMP_DIR"
  fi
}
trap cleanup EXIT

while [ "$#" -gt 0 ]; do
  case "$1" in
    --yes)
      ASSUME_YES=1
      ;;
    --skip-service)
      SKIP_SERVICE=1
      ;;
    --skip-safety-backup)
      SKIP_SAFETY_BACKUP=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      fail "Opcao desconhecida: $1"
      ;;
    *)
      if [ -n "$BACKUP_FILE" ]; then
        fail "Informe apenas um arquivo de backup."
      fi
      BACKUP_FILE="$1"
      ;;
  esac
  shift
done

[ -n "$BACKUP_FILE" ] || { usage; exit 1; }
[ -f "$BACKUP_FILE" ] || fail "Arquivo de backup nao encontrado: $BACKUP_FILE"
BACKUP_FILE="$(readlink -f "$BACKUP_FILE")"
[ -d "$APP_DIR" ] || fail "APP_DIR invalido: $APP_DIR"
cd "$APP_DIR"

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

: "${DB_HOST:?DB_HOST ausente}"
: "${DB_PORT:?DB_PORT ausente}"
: "${DB_USER:?DB_USER ausente}"
: "${DB_PASSWORD:?DB_PASSWORD ausente}"
: "${DB_NAME:?DB_NAME ausente}"

resolve_bin() {
  local configured="$1"
  local name="$2"
  shift 2
  if [ -n "$configured" ] && [ -x "$configured" ]; then
    printf '%s\n' "$configured"
    return 0
  fi
  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
    return 0
  fi
  local candidate
  for candidate in "$@"; do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

MYSQL_BIN="$(resolve_bin "${MYSQL_PATH:-}" mysql /usr/bin/mysql /usr/local/bin/mysql /bin/mysql)" || fail "mysql nao encontrado. Instale o cliente MariaDB/MySQL ou configure MYSQL_PATH."
MYSQLDUMP_BIN="$(resolve_bin "${MYSQLDUMP_PATH:-}" mysqldump /usr/bin/mysqldump /usr/local/bin/mysqldump /bin/mysqldump)" || fail "mysqldump nao encontrado. Instale o cliente MariaDB/MySQL ou configure MYSQLDUMP_PATH."

SQL_FILE="$BACKUP_FILE"
case "$BACKUP_FILE" in
  *.tar.gz|*.tgz)
    TMP_DIR="$(mktemp -d -t o3restore-XXXXXX)"
    tar -xzf "$BACKUP_FILE" -C "$TMP_DIR"
    if [ -f "$TMP_DIR/database.sql.gz" ]; then
      SQL_FILE="$TMP_DIR/database.sql.gz"
    elif [ -f "$TMP_DIR/database.sql" ]; then
      SQL_FILE="$TMP_DIR/database.sql"
    else
      fail "Artefato nao contem database.sql.gz nem database.sql."
    fi
    ;;
esac

case "$SQL_FILE" in
  *.sql|*.sql.gz)
    ;;
  *)
    fail "Formato de dump nao suportado: $SQL_FILE"
    ;;
esac

if [ "$ASSUME_YES" -ne 1 ]; then
  if [ -t 0 ]; then
    printf 'Esta operacao vai restaurar o banco %s em %s:%s. Digite o nome do banco para confirmar: ' "$DB_NAME" "$DB_HOST" "$DB_PORT"
    read -r resposta
    [ "$resposta" = "$DB_NAME" ] || fail "Confirmacao invalida."
  else
    fail "Execucao nao interativa exige --yes e RESTORE_CONFIRM=$DB_NAME."
  fi
elif [ "${RESTORE_CONFIRM:-}" != "$DB_NAME" ]; then
  fail "Para usar --yes, defina RESTORE_CONFIRM=$DB_NAME."
fi

export MYSQL_PWD="$DB_PASSWORD"

log "Validando conexao com o banco $DB_NAME."
"$MYSQL_BIN" --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" --database "$DB_NAME" --execute "SELECT 1" >/dev/null

if [ "$SKIP_SAFETY_BACKUP" -ne 1 ]; then
  mkdir -p "$SAFETY_BACKUP_DIR"
  SAFETY_FILE="$SAFETY_BACKUP_DIR/pre-restore-${DB_NAME}-$(date +%Y%m%d-%H%M%S).sql.gz"
  log "Gerando dump de seguranca em $SAFETY_FILE."
  "$MYSQLDUMP_BIN" --single-transaction --routines --triggers --events --default-character-set=utf8mb4 --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" "$DB_NAME" | gzip > "$SAFETY_FILE"
fi

if [ "$SKIP_SERVICE" -ne 1 ]; then
  log "Parando $SERVICE_NAME."
  systemctl stop "$SERVICE_NAME"
fi

log "Restaurando dump $SQL_FILE."
if gzip -t "$SQL_FILE" >/dev/null 2>&1; then
  gzip -dc "$SQL_FILE" | "$MYSQL_BIN" --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" --database "$DB_NAME"
else
  "$MYSQL_BIN" --binary-mode --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" --database "$DB_NAME" < "$SQL_FILE"
fi

if [ "$SKIP_SERVICE" -ne 1 ]; then
  log "Iniciando $SERVICE_NAME."
  systemctl start "$SERVICE_NAME"
fi

if [ -x "$APP_DIR/deployment/healthcheck.sh" ]; then
  log "Executando healthcheck."
  healthcheck_ok=0
  for tentativa in 1 2 3 4 5; do
    if "$APP_DIR/deployment/healthcheck.sh"; then
      healthcheck_ok=1
      break
    fi
    log "Healthcheck ainda nao respondeu; nova tentativa em 3s ($tentativa/5)."
    sleep 3
  done
  [ "$healthcheck_ok" -eq 1 ] || fail "Healthcheck falhou apos iniciar o servico."
else
  log "Healthcheck nao encontrado; restore SQL concluido."
fi

log "Restore concluido. Revise migrations pendentes antes de liberar o ambiente se o dump for de outra versao."
