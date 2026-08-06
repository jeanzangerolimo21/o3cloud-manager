from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from app.configuracoes.auth_service import AuthConfigService
from app.repositories.auth_repository import AuthRepository


autenticacao_bp = Blueprint("autenticacao", __name__)


_DASHBOARD_MENU_KEYS = {item["valor"]: item["menu_key"] for item in AuthConfigService.DASHBOARDS_PRINCIPAIS}

def _dashboard_principal(usuario):
    endpoint = usuario.get("dashboard_principal") or "financeiro.dashboard"
    if endpoint not in _DASHBOARD_MENU_KEYS:
        endpoint = "financeiro.dashboard"
    if usuario.get("perfil_codigo") == "ADMIN":
        return endpoint
    email = usuario.get("email") or usuario.get("login")
    permitidos = {item.get("menu_key") for item in AuthRepository.listar_menu_keys_usuario(email)} if email else set()
    if _DASHBOARD_MENU_KEYS.get(endpoint) in permitidos:
        return endpoint
    for candidato, menu_key in _DASHBOARD_MENU_KEYS.items():
        if menu_key in permitidos:
            return candidato
    return "financeiro.dashboard"


def _ip_origem():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()


def _user_agent():
    return (request.headers.get("User-Agent") or "")[:255]


@autenticacao_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("usuario_email"):
        endpoint = session.get("usuario_dashboard_principal") or "financeiro.dashboard"
        return redirect(request.args.get("next") or url_for(endpoint))
    if request.method == "POST":
        identificador = request.form.get("identificador")
        try:
            usuario = AuthConfigService.autenticar(
                identificador,
                request.form.get("senha"),
                _ip_origem(),
                _user_agent(),
            )
        except ValueError as erro:
            flash(str(erro), "danger")
        else:
            session.clear()
            session["usuario_id"] = usuario.get("id")
            session["usuario_nome"] = usuario.get("nome")
            session["usuario_email"] = usuario.get("email") or usuario.get("login")
            session["usuario_perfil"] = usuario.get("perfil_codigo")
            session["usuario_possui_agenda"] = bool(usuario.get("possui_agenda"))
            endpoint = _dashboard_principal(usuario)
            session["usuario_dashboard_principal"] = endpoint
            session.permanent = True
            return redirect(request.form.get("next") or url_for(endpoint))
    return render_template("autenticacao/login.html", next_url=request.args.get("next") or request.form.get("next") or "")


@autenticacao_bp.route("/logout")
def logout():
    usuario_email = session.get("usuario_email")
    usuario_id = session.get("usuario_id")
    AuthConfigService.registrar_logout(usuario_email, usuario_id, _ip_origem(), _user_agent())
    session.clear()
    flash("Sessão encerrada.", "success")
    return redirect(url_for("autenticacao.login"))

@autenticacao_bp.route("/minha-conta", methods=["GET", "POST"])
def minha_conta():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("autenticacao.login"))
    usuario = AuthConfigService.buscar_usuario(usuario_id)
    if not usuario:
        session.clear()
        flash("Sessão inválida. Faça login novamente.", "warning")
        return redirect(url_for("autenticacao.login"))
    if request.method == "POST":
        acao = request.form.get("acao")
        try:
            if acao == "dados":
                usuario = AuthConfigService.atualizar_minha_conta(usuario_id, request.form, request.files.get("foto"))
                session["usuario_nome"] = usuario.get("nome")
                session["usuario_email"] = usuario.get("email") or usuario.get("login")
                flash("Dados da conta atualizados.", "success")
            elif acao == "senha":
                AuthConfigService.alterar_minha_senha(
                    usuario_id,
                    request.form.get("senha_atual"),
                    request.form.get("nova_senha"),
                    request.form.get("confirmacao_senha"),
                )
                flash("Senha alterada com sucesso.", "success")
            else:
                flash("Ação inválida.", "danger")
        except ValueError as erro:
            flash(str(erro), "danger")
        return redirect(url_for("autenticacao.minha_conta"))
    return render_template("autenticacao/minha_conta.html", usuario=usuario)

