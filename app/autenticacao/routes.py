from flask import Blueprint
from flask import flash
from flask import redirect
from flask import make_response
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from app.configuracoes.auth_service import AuthConfigService
from app.core.logging_config import get_logger
from app.repositories.auth_repository import AuthRepository


autenticacao_bp = Blueprint("autenticacao", __name__)
security_logger = get_logger("security")


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


def _abrir_sessao_usuario(usuario):
    session.clear()
    session["usuario_id"] = usuario.get("id")
    session["usuario_nome"] = usuario.get("nome")
    session["usuario_email"] = usuario.get("email") or usuario.get("login")
    session["usuario_perfil"] = usuario.get("perfil_codigo")
    session["usuario_possui_agenda"] = bool(usuario.get("possui_agenda"))
    endpoint = _dashboard_principal(usuario)
    session["usuario_dashboard_principal"] = endpoint
    session.permanent = True
    return endpoint


def _limpar_2fa_pendente():
    for chave in ("mfa_usuario_id", "mfa_email", "mfa_next", "mfa_metodo"):
        session.pop(chave, None)


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
            security_logger.warning("Login failed", extra={"operation": "LOGIN_FALHA"})
            flash(str(erro), "danger")
        else:
            next_url = request.form.get("next") or ""
            token_dispositivo = request.cookies.get(AuthConfigService.MFA_COOKIE_NAME)
            if AuthConfigService.exige_2fa(usuario, token_dispositivo):
                metodo = AuthConfigService.metodo_2fa(usuario)
                session.clear()
                session["mfa_usuario_id"] = usuario.get("id")
                session["mfa_email"] = usuario.get("email") or usuario.get("login")
                session["mfa_next"] = next_url
                session["mfa_metodo"] = metodo
                session.permanent = True
                if metodo == "EMAIL":
                    try:
                        AuthConfigService.iniciar_2fa_email(usuario.get("id"), _ip_origem(), _user_agent())
                    except ValueError as erro:
                        session.clear()
                        flash(str(erro), "danger")
                        return render_template("autenticacao/login.html", next_url=next_url)
                    flash("Enviamos um código de segurança para seu e-mail.", "info")
                return redirect(url_for("autenticacao.login_2fa"))
            AuthConfigService.concluir_login(usuario, _ip_origem(), _user_agent(), "Login realizado")
            security_logger.info("Login succeeded", extra={"operation": "LOGIN_SUCESSO"})
            endpoint = _abrir_sessao_usuario(usuario)
            return redirect(next_url or url_for(endpoint))
    return render_template("autenticacao/login.html", next_url=request.args.get("next") or request.form.get("next") or "")


@autenticacao_bp.route("/login/2fa", methods=["GET", "POST"])
def login_2fa():
    usuario_id = session.get("mfa_usuario_id")
    if not usuario_id:
        return redirect(url_for("autenticacao.login"))
    metodo = session.get("mfa_metodo") or "EMAIL"
    if request.method == "POST":
        try:
            if metodo == "TOTP":
                usuario = AuthConfigService.validar_2fa_totp(usuario_id, request.form.get("codigo"), _ip_origem(), _user_agent())
            else:
                usuario = AuthConfigService.validar_2fa_email(usuario_id, request.form.get("codigo"), _ip_origem(), _user_agent())
        except ValueError as erro:
            flash(str(erro), "danger")
        else:
            next_url = session.get("mfa_next") or ""
            lembrar = request.form.get("lembrar_dispositivo")
            AuthConfigService.concluir_login(usuario, _ip_origem(), _user_agent(), "Login realizado com 2FA")
            endpoint = _abrir_sessao_usuario(usuario)
            resposta = make_response(redirect(next_url or url_for(endpoint)))
            if lembrar:
                dispositivo = AuthConfigService.criar_dispositivo_confiavel(usuario.get("id"), _ip_origem(), _user_agent())
                max_age = int(AuthConfigService.MFA_TRUSTED_DEVICE_DAYS * 24 * 60 * 60)
                resposta.set_cookie(
                    AuthConfigService.MFA_COOKIE_NAME,
                    dispositivo["token"],
                    max_age=max_age,
                    expires=dispositivo["expira_em"],
                    httponly=True,
                    secure=request.is_secure,
                    samesite="Lax",
                )
            _limpar_2fa_pendente()
            security_logger.info("Login 2FA succeeded", extra={"operation": "LOGIN_2FA_SUCESSO"})
            return resposta
    return render_template("autenticacao/2fa_email.html", email=session.get("mfa_email"), metodo=metodo)


@autenticacao_bp.route("/login/2fa/reenviar", methods=["POST"])
def reenviar_2fa():
    usuario_id = session.get("mfa_usuario_id")
    if not usuario_id:
        return redirect(url_for("autenticacao.login"))
    if session.get("mfa_metodo") == "TOTP":
        flash("Reenvio disponível apenas para código por e-mail.", "warning")
        return redirect(url_for("autenticacao.login_2fa"))
    try:
        AuthConfigService.iniciar_2fa_email(usuario_id, _ip_origem(), _user_agent())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Novo código enviado para seu e-mail.", "success")
    return redirect(url_for("autenticacao.login_2fa"))


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
            elif acao == "totp_iniciar":
                totp_setup = AuthConfigService.iniciar_configuracao_totp(usuario_id)
                return render_template("autenticacao/minha_conta.html", usuario=usuario, totp_setup=totp_setup)
            elif acao == "totp_confirmar":
                usuario = AuthConfigService.confirmar_configuracao_totp(
                    usuario_id,
                    request.form.get("totp_secret"),
                    request.form.get("codigo"),
                    session.get("usuario_email"),
                    _ip_origem(),
                    _user_agent(),
                )
                flash("Autenticador TOTP habilitado.", "success")
            elif acao == "totp_desativar":
                usuario = AuthConfigService.desativar_totp(
                    usuario_id,
                    request.form.get("codigo"),
                    session.get("usuario_email"),
                    _ip_origem(),
                    _user_agent(),
                )
                flash("Autenticador TOTP desativado. O segundo fator voltou para e-mail.", "success")
            else:
                flash("Ação inválida.", "danger")
        except ValueError as erro:
            flash(str(erro), "danger")
        return redirect(url_for("autenticacao.minha_conta"))
    return render_template("autenticacao/minha_conta.html", usuario=usuario)

