import json
from datetime import date
from datetime import datetime
from decimal import Decimal

from flask import has_request_context
from flask import request
from flask import session

from app.repositories.auth_repository import AuthRepository

_CHAVES_SENSIVEIS = (
    "senha", "password", "token", "segredo", "secret", "app_key", "app_secret",
    "access_token", "bind_password", "chave_ativacao", "cpf", "cnpj",
)


def registrar_evento(acao, entidade, entidade_id=None, detalhes=None, usuario_email=None):
    try:
        AuthRepository.registrar_auditoria(
            usuario_email or _usuario_email(),
            acao,
            entidade,
            entidade_id,
            _detalhes(detalhes),
            _ip_origem(),
            _user_agent(),
        )
    except Exception:
        return False
    return True


def _usuario_email():
    if not has_request_context():
        return "sistema"
    for chave in ("user_email", "email", "usuario_email", "login_email"):
        valor = session.get(chave)
        if valor:
            return valor
    return "sistema"


def _ip_origem():
    if not has_request_context():
        return None
    encaminhado = request.headers.get("X-Forwarded-For")
    if encaminhado:
        return encaminhado.split(",", 1)[0].strip()[:45]
    return (request.remote_addr or "")[:45] or None


def _user_agent():
    if not has_request_context():
        return None
    return (request.headers.get("User-Agent") or "")[:255] or None


def _detalhes(valor):
    if valor is None or isinstance(valor, str):
        return valor
    try:
        return json.dumps(_sanitizar(valor), ensure_ascii=False, default=_json_default)[:2000]
    except Exception:
        return str(valor)[:2000]


def _sanitizar(valor):
    if isinstance(valor, dict):
        return {str(chave): ("***" if _sensivel(chave) else _sanitizar(item)) for chave, item in valor.items()}
    if isinstance(valor, (list, tuple, set)):
        return [_sanitizar(item) for item in valor]
    return valor


def _sensivel(chave):
    texto = str(chave or "").lower()
    return any(item in texto for item in _CHAVES_SENSIVEIS)


def _json_default(valor):
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return str(valor)
    return str(valor)
