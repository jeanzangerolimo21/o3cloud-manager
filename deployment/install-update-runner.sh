#!/usr/bin/env bash
if [ -z "${BASH_VERSION:-}" ]; then
  exec bash "$0" "$@"
fi
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/o3cloud-manager}"
APP_USER="${APP_USER:-o3cloud}"
RUNNER_PATH="${RUNNER_PATH:-/usr/local/sbin/o3cloud-update-beta}"
SUDOERS_PATH="${SUDOERS_PATH:-/etc/sudoers.d/o3cloud-update-beta}"

log() { printf '[update-runner] %s\n' "$*"; }
fail() { printf '[update-runner] ERRO: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" = "0" ] || fail "Execute como root."
[ -f "$APP_DIR/deployment/update-beta.sh" ] || fail "Script $APP_DIR/deployment/update-beta.sh nao encontrado."
id "$APP_USER" >/dev/null 2>&1 || fail "Usuario $APP_USER nao existe."

install -o root -g root -m 0750 "$APP_DIR/deployment/update-beta.sh" "$RUNNER_PATH"
cat >"$SUDOERS_PATH" <<EOF
Defaults:$APP_USER !requiretty
$APP_USER ALL=(root) NOPASSWD: $RUNNER_PATH
EOF
chmod 0440 "$SUDOERS_PATH"
visudo -cf "$SUDOERS_PATH" >/dev/null
log "Runner instalado em $RUNNER_PATH."
log "Sudoers instalado em $SUDOERS_PATH."
