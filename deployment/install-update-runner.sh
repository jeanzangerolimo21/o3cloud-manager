#!/usr/bin/env bash
if [ -z "${BASH_VERSION:-}" ]; then
  exec bash "$0" "$@"
fi
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/o3cloud-manager}"
APP_USER="${APP_USER:-o3cloud}"
RUNNER_PATH="${RUNNER_PATH:-/usr/local/sbin/o3cloud-update-system}"
SUDOERS_PATH="${SUDOERS_PATH:-/etc/sudoers.d/o3cloud-update-system}"

log() { printf '[update-runner] %s\n' "$*"; }
fail() { printf '[update-runner] ERRO: %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" = "0" ] || fail "Execute como root."
[ -f "$APP_DIR/deployment/update-beta.sh" ] || fail "Script $APP_DIR/deployment/update-beta.sh nao encontrado."
id "$APP_USER" >/dev/null 2>&1 || fail "Usuario $APP_USER nao existe."

cat >"$RUNNER_PATH" <<EOF
#!/usr/bin/env bash
set -euo pipefail
UPDATE_SCRIPT="$APP_DIR/deployment/update-beta.sh"
[ -f "\$UPDATE_SCRIPT" ] || { echo "[update-runner] ERRO: \$UPDATE_SCRIPT nao encontrado." >&2; exit 1; }
TEMP_SCRIPT="\$(mktemp -t o3cloud-update-runner-XXXXXX.sh)"
cleanup() { rm -f "\$TEMP_SCRIPT"; }
trap cleanup EXIT
cp "\$UPDATE_SCRIPT" "\$TEMP_SCRIPT"
chmod 0700 "\$TEMP_SCRIPT"
bash "\$TEMP_SCRIPT" "\$@"
EOF
chown root:root "$RUNNER_PATH"
chmod 0750 "$RUNNER_PATH"
cat >"$SUDOERS_PATH" <<EOF
Defaults:$APP_USER !requiretty
$APP_USER ALL=(root) NOPASSWD: $RUNNER_PATH
EOF
chmod 0440 "$SUDOERS_PATH"
visudo -cf "$SUDOERS_PATH" >/dev/null
log "Runner dinamico instalado em $RUNNER_PATH."
log "Sudoers instalado em $SUDOERS_PATH."
