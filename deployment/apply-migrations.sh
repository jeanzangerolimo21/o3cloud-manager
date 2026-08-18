#!/usr/bin/env bash
if [ -z "${BASH_VERSION:-}" ]; then
  exec bash "$0" "$@"
fi
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/o3cloud-manager}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-$APP_DIR/database/migrations}"

log() { printf '[migrations] %s\n' "$*"; }
fail() { printf '[migrations] ERRO: %s\n' "$*" >&2; exit 1; }

[ -d "$APP_DIR" ] || fail "APP_DIR invalido: $APP_DIR"
[ -d "$MIGRATIONS_DIR" ] || fail "Diretorio de migrations nao encontrado: $MIGRATIONS_DIR"
cd "$APP_DIR"

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

: "${DB_HOST:?DB_HOST ausente}"
: "${DB_PORT:?DB_PORT ausente}"
: "${DB_NAME:?DB_NAME ausente}"
: "${DB_USER:?DB_USER ausente}"
: "${DB_PASSWORD:?DB_PASSWORD ausente}"

MYSQL_BIN="${MYSQL_PATH:-}"
if [ -z "$MYSQL_BIN" ] || [ ! -x "$MYSQL_BIN" ]; then
  MYSQL_BIN="$(command -v mysql || true)"
fi
[ -n "$MYSQL_BIN" ] || fail "mysql nao encontrado. Instale mariadb-client/mysql-client."

export MYSQL_PWD="$DB_PASSWORD"
MYSQL=("$MYSQL_BIN" --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" --database "$DB_NAME" --default-character-set=utf8mb4)

log "Validando conexao com $DB_NAME em $DB_HOST:$DB_PORT."
"${MYSQL[@]}" --execute "SELECT 1" >/dev/null

log "Garantindo tabela schema_migrations."
"${MYSQL[@]}" --execute "CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(255) NOT NULL PRIMARY KEY, applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"

version_col="$(${MYSQL[@]} --batch --skip-column-names --execute "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='schema_migrations' AND column_name='version';")"
if [ "$version_col" != "1" ]; then
  legacy_col=""
  for candidate in migration name filename; do
    found="$(${MYSQL[@]} --batch --skip-column-names --execute "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='schema_migrations' AND column_name='${candidate}';")"
    if [ "$found" = "1" ]; then
      legacy_col="$candidate"
      break
    fi
  done
  if [ -n "$legacy_col" ]; then
    log "Normalizando schema_migrations: coluna $legacy_col -> version."
    "${MYSQL[@]}" --execute "ALTER TABLE schema_migrations CHANGE COLUMN \`$legacy_col\` version VARCHAR(255) NOT NULL;"
  else
    total_schema_migrations="$(${MYSQL[@]} --batch --skip-column-names --execute "SELECT COUNT(*) FROM schema_migrations;")"
    if [ "$total_schema_migrations" = "0" ]; then
      log "Recriando schema_migrations vazia com layout atual."
      "${MYSQL[@]}" --execute "DROP TABLE schema_migrations; CREATE TABLE schema_migrations (version VARCHAR(255) NOT NULL PRIMARY KEY, applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
    else
      fail "schema_migrations existe sem coluna version e com dados. Rode DESCRIBE schema_migrations e ajuste a coluna legada para version."
    fi
  fi
fi

applied_at_col="$(${MYSQL[@]} --batch --skip-column-names --execute "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='schema_migrations' AND column_name='applied_at';")"
if [ "$applied_at_col" != "1" ]; then
  log "Adicionando coluna applied_at em schema_migrations."
  "${MYSQL[@]}" --execute "ALTER TABLE schema_migrations ADD COLUMN applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;"
fi

aplicadas=0
ignoradas=0
while IFS= read -r migration; do
  version="$(basename "$migration")"
  version_sem_ext="${version%.sql}"
  exists="$("${MYSQL[@]}" --batch --skip-column-names --execute "SELECT COUNT(*) FROM schema_migrations WHERE version IN ('${version}', '${version_sem_ext}');")"
  if [ "$exists" != "0" ]; then
    "${MYSQL[@]}" --execute "INSERT INTO schema_migrations (version) VALUES ('${version}') ON DUPLICATE KEY UPDATE version=VALUES(version);"
    ignoradas=$((ignoradas + 1))
    continue
  fi
  log "Aplicando $version."
  "${MYSQL[@]}" < "$migration"
  "${MYSQL[@]}" --execute "INSERT INTO schema_migrations (version) VALUES ('${version}') ON DUPLICATE KEY UPDATE version=VALUES(version);"
  aplicadas=$((aplicadas + 1))
done < <(find "$MIGRATIONS_DIR" -maxdepth 1 -type f -name '*.sql' | sort)

log "Concluido: $aplicadas aplicada(s), $ignoradas ja registradas."
