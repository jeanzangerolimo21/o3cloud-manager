#!/usr/bin/env bash
set -uo pipefail

APP_DIR="${APP_DIR:-/opt/o3cloud-manager}"
PUBLIC_URL="${PUBLIC_BASE_URL:-https://o3manager.o3cloud.com.br}"
ENV_FILE="$APP_DIR/.env"

section() { printf '\n========== %s ==========\n' "$1"; }
ok() { printf '[OK] %s\n' "$1"; }
warn() { printf '[ATENCAO] %s\n' "$1"; }
info() { printf '[INFO] %s\n' "$1"; }

env_value() {
  local key="$1"
  [ -r "$ENV_FILE" ] || return 0
  sed -n "s/^${key}=//p" "$ENV_FILE" | tail -n 1
}

section "IDENTIFICACAO"
date -Is
hostnamectl 2>/dev/null || hostname
uname -a
uptime

section "APLICACAO"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" describe --tags --always 2>/dev/null || true
  git -C "$APP_DIR" status --short 2>/dev/null || true
else
  warn "Repositorio Git nao encontrado em $APP_DIR."
fi
systemctl is-active o3cloud-manager.service 2>/dev/null && ok "Servico da aplicacao ativo." || warn "Servico da aplicacao inativo."
systemctl is-enabled o3cloud-manager.service 2>/dev/null || true

section "SEGREDOS E PERMISSOES"
if [ -f "$ENV_FILE" ]; then
  stat -c '%a %U:%G %n' "$ENV_FILE"
  mode="$(stat -c '%a' "$ENV_FILE")"
  [ "$mode" = "600" ] || [ "$mode" = "640" ] && ok ".env com permissao restrita." || warn "Revise a permissao do .env; recomendado 600 ou 640."
  secret="$(env_value SECRET_KEY)"
  if [ -z "$secret" ] || [ "$secret" = "o3cloud-dev" ] || [ "${#secret}" -lt 32 ]; then
    warn "SECRET_KEY ausente, padrao ou curta; use pelo menos 32 caracteres aleatorios."
  else
    ok "SECRET_KEY configurada com comprimento adequado (valor oculto)."
  fi
  cofre_key="$(env_value COFRE_SENHAS_KEY)"
  [ -n "$cofre_key" ] && ok "COFRE_SENHAS_KEY configurada (valor oculto)." || warn "COFRE_SENHAS_KEY ausente."
  [ "$(env_value SESSION_COOKIE_SECURE)" != "0" ] && ok "Cookie de sessao seguro habilitado." || warn "SESSION_COOKIE_SECURE=0; use 1 em producao."
  [ "$(env_value TRUST_PROXY)" != "0" ] && ok "Proxy confiavel habilitado para identificar o IP real." || warn "TRUST_PROXY=0/ausente; valide a configuracao quando houver proxy reverso."
else
  warn ".env nao encontrado."
fi
for path in "$APP_DIR/storage" "$APP_DIR/logs" "$APP_DIR/backups"; do
  [ -e "$path" ] && stat -c '%a %U:%G %n' "$path" || warn "$path nao encontrado."
done

section "REDE E FIREWALL"
ss -lntup 2>/dev/null || ss -lnt 2>/dev/null || true
if ss -lntH 2>/dev/null | awk '{print $4}' | grep -Eq '(^|\])0\.0\.0\.0:5000$|^\*:5000$|^\[::\]:5000$'; then
  warn "Gunicorn exposto em todas as interfaces na porta 5000."
elif ss -lntH 2>/dev/null | awk '{print $4}' | grep -q '127.0.0.1:5000$'; then
  ok "Gunicorn restrito ao loopback na porta 5000."
fi
if command -v ufw >/dev/null 2>&1; then
  ufw status verbose 2>/dev/null || warn "Nao foi possivel consultar UFW sem privilegios."
elif command -v nft >/dev/null 2>&1; then
  nft list ruleset 2>/dev/null | sed -n '1,160p' || warn "Nao foi possivel consultar nftables."
else
  warn "Nenhum gerenciador UFW/nftables identificado."
fi

section "HTTPS E CABECALHOS"
headers="$(mktemp)"
trap 'rm -f "$headers"' EXIT
if curl -fsS -D "$headers" -o /dev/null --max-time 20 "$PUBLIC_URL/login"; then
  for header in strict-transport-security content-security-policy x-frame-options x-content-type-options referrer-policy permissions-policy; do
    grep -qi "^${header}:" "$headers" && ok "$header presente." || warn "$header ausente."
  done
  csp_count="$(grep -ci '^content-security-policy:' "$headers" || true)"
  if [ "$csp_count" -gt 1 ]; then
    warn "$csp_count cabecalhos CSP recebidos; remova a politica generica duplicada do proxy externo."
  elif grep -qi '^content-security-policy:.*unsafe-eval' "$headers"; then
    warn "A unica CSP recebida permite unsafe-eval."
  else
    ok "CSP unica e sem unsafe-eval."
  fi
else
  warn "Nao foi possivel consultar $PUBLIC_URL/login."
fi
curl -fsS --max-time 20 "$PUBLIC_URL/.well-known/security.txt" 2>/dev/null || warn "security.txt indisponivel."

section "TLS"
tls_host="${PUBLIC_URL#*://}"
tls_host="${tls_host%%/*}"
if command -v openssl >/dev/null 2>&1; then
  echo | openssl s_client -connect "$tls_host:443" -servername "$tls_host" 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null || warn "Falha ao ler certificado TLS."
  for proto in tls1 tls1_1; do
    if echo | openssl s_client -connect "$tls_host:443" -servername "$tls_host" "-$proto" >/dev/null 2>&1; then
      warn "$proto ainda aceito."
    else
      ok "$proto recusado."
    fi
  done
fi

section "ATUALIZACOES DO SISTEMA"
if command -v apt-get >/dev/null 2>&1; then
  apt-get -s upgrade 2>/dev/null | awk '/^[0-9]+ upgraded/{print}' || true
  command -v unattended-upgrade >/dev/null 2>&1 && ok "unattended-upgrades instalado." || warn "unattended-upgrades nao identificado."
fi

section "DEPENDENCIAS PYTHON"
if [ -x "$APP_DIR/venv/bin/pip-audit" ]; then
  "$APP_DIR/venv/bin/pip-audit" || warn "pip-audit encontrou vulnerabilidades ou retornou erro."
else
  warn "pip-audit nao instalado; instale para auditoria de CVEs Python."
fi
if [ -x "$APP_DIR/venv/bin/pip" ]; then
  "$APP_DIR/venv/bin/pip" list --outdated --format=columns 2>/dev/null || true
fi

section "BACKUPS E LOCKS"
find "$APP_DIR/backups" -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM %s %p\n' 2>/dev/null | sort -r | head -n 10 || true
if [ -d /tmp/o3cloud-manager-update.lock ]; then
  lock_pid="$(sed -n '1p' /tmp/o3cloud-manager-update.lock/pid 2>/dev/null || true)"
  if [[ "$lock_pid" =~ ^[0-9]+$ ]] && kill -0 "$lock_pid" 2>/dev/null; then
    info "Lock de atualizacao ativo pelo PID $lock_pid."
  else
    warn "Lock de atualizacao orfao encontrado."
  fi
else
  ok "Nenhum lock de atualizacao presente."
fi

section "CONCLUSAO"
info "Diagnostico somente leitura concluido. Revise todas as linhas [ATENCAO]."
