from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from app.configuracoes.auth_service import AuthConfigService
from app.configuracoes.email_service import EmailConfigService


configuracoes_bp = Blueprint("configuracoes", __name__, url_prefix="/configuracoes")


def _email_usuario_logado():
    return session.get("usuario_email") or session.get("email") or "sistema"


@configuracoes_bp.route("/usuarios")
def usuarios_index():
    contexto = AuthConfigService.dashboard()
    return render_template(
        "configuracoes/usuarios/index.html",
        **contexto,
        page_title="Usuários e Acessos",
        page_description="Gestão de usuários, convites e provedores de autenticação.",
        page_icon="bi-person-gear",
        page_button_text="Novo Usuário",
        page_button_icon="bi-person-plus",
        page_button_url=url_for("configuracoes.usuarios_novo"),
    )


@configuracoes_bp.route("/usuarios/novo", methods=["GET", "POST"])
def usuarios_novo():
    perfis = AuthConfigService.repository.listar_perfis()
    if request.method == "POST":
        try:
            usuario_id = AuthConfigService.criar_usuario(request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("configuracoes/usuarios/form.html", usuario=request.form, perfis=perfis, modo="novo")
        flash("Usuário cadastrado. Se for local e convidado, o convite foi enviado por e-mail.", "success")
        return redirect(url_for("configuracoes.usuarios_editar", usuario_id=usuario_id))
    return render_template("configuracoes/usuarios/form.html", usuario=AuthConfigService.novo_usuario_payload(), perfis=perfis, modo="novo")


@configuracoes_bp.route("/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
def usuarios_editar(usuario_id):
    usuario = AuthConfigService.buscar_usuario(usuario_id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("configuracoes.usuarios_index"))
    perfis = AuthConfigService.repository.listar_perfis()
    if request.method == "POST":
        try:
            AuthConfigService.atualizar_usuario(usuario_id, request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            usuario = {**usuario, **request.form}
        else:
            flash("Usuário atualizado.", "success")
            return redirect(url_for("configuracoes.usuarios_index"))
    return render_template("configuracoes/usuarios/form.html", usuario=usuario, perfis=perfis, modo="editar")


@configuracoes_bp.route("/usuarios/<int:usuario_id>/convidar", methods=["POST"])
def usuarios_convidar(usuario_id):
    try:
        resultado = AuthConfigService.enviar_convite(usuario_id, _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        envio = resultado.get("email_resultado") or {}
        if envio.get("enviado"):
            flash("Convite enviado para {}.".format(resultado.get("email")), "success")
        else:
            motivo = envio.get("motivo") or "SMTP indisponível"
            flash("Convite gerado, mas o e-mail não foi enviado ({}).".format(motivo), "warning")
    return redirect(request.referrer or url_for("configuracoes.usuarios_index"))


@configuracoes_bp.route("/usuarios/convite/<token>", methods=["GET", "POST"])
def usuarios_aceitar_convite(token):
    convite = AuthConfigService.buscar_convite(token)
    if request.method == "POST":
        try:
            AuthConfigService.aceitar_convite(token, request.form.get("senha"), request.form.get("confirmacao_senha"))
        except ValueError as erro:
            flash(str(erro), "danger")
        else:
            flash("Senha cadastrada. Seu usuário está ativo.", "success")
            return redirect(url_for("configuracoes.usuarios_aceitar_convite", token=token))
    return render_template("configuracoes/usuarios/convite.html", convite=convite)


@configuracoes_bp.route("/usuarios/provedores/novo", methods=["GET", "POST"])
def usuarios_provedor_novo():
    if request.method == "POST":
        try:
            provedor_id = AuthConfigService.criar_provedor(request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("configuracoes/usuarios/provedor_form.html", provedor=request.form, modo="novo")
        flash("Provedor cadastrado.", "success")
        return redirect(url_for("configuracoes.usuarios_provedor_editar", provedor_id=provedor_id))
    return render_template("configuracoes/usuarios/provedor_form.html", provedor=AuthConfigService.novo_provedor_payload(), modo="novo")


@configuracoes_bp.route("/usuarios/provedores/<int:provedor_id>/editar", methods=["GET", "POST"])
def usuarios_provedor_editar(provedor_id):
    provedor = AuthConfigService.buscar_provedor(provedor_id)
    if not provedor:
        flash("Provedor não encontrado.", "danger")
        return redirect(url_for("configuracoes.usuarios_index"))
    if request.method == "POST":
        try:
            AuthConfigService.atualizar_provedor(provedor_id, request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            provedor = {**provedor, **request.form}
        else:
            flash("Provedor atualizado.", "success")
            return redirect(url_for("configuracoes.usuarios_index"))
    return render_template("configuracoes/usuarios/provedor_form.html", provedor=provedor, modo="editar")


@configuracoes_bp.route("/usuarios/provedores/<int:provedor_id>/testar", methods=["POST"])
def usuarios_provedor_testar(provedor_id):
    try:
        resultado = AuthConfigService.testar_provedor(provedor_id, request.form)
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash(resultado.get("mensagem") or "Teste concluído.", "success")
    return redirect(request.referrer or url_for("configuracoes.usuarios_index"))


@configuracoes_bp.route("/email")
def email_index():
    return render_template(
        "configuracoes/email/index.html",
        configuracoes=EmailConfigService.listar(),
        page_title="Serviços de Email",
        page_description="Conta SMTP usada pelos avisos automáticos do sistema.",
        page_icon="bi-envelope-gear-fill",
        page_button_text="Novo Serviço",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("configuracoes.email_novo"),
    )


@configuracoes_bp.route("/email/novo", methods=["GET", "POST"])
def email_novo():
    if request.method == "POST":
        try:
            config_id = EmailConfigService.criar(request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("configuracoes/email/form.html", config=request.form, modo="novo")
        flash("Serviço de e-mail cadastrado.", "success")
        return redirect(url_for("configuracoes.email_editar", config_id=config_id))
    return render_template(
        "configuracoes/email/form.html",
        config={"nome": "SMTP Principal", "smtp_port": 587, "usar_tls": 1, "ativo": 1},
        modo="novo",
    )


@configuracoes_bp.route("/email/<int:config_id>/editar", methods=["GET", "POST"])
def email_editar(config_id):
    config = EmailConfigService.buscar_por_id(config_id)
    if not config:
        flash("Serviço de e-mail não encontrado.", "danger")
        return redirect(url_for("configuracoes.email_index"))
    if request.method == "POST":
        try:
            EmailConfigService.atualizar(config_id, request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            config = {**config, **request.form}
        else:
            flash("Serviço de e-mail atualizado.", "success")
            return redirect(url_for("configuracoes.email_index"))
    return render_template("configuracoes/email/form.html", config=config, modo="editar")


@configuracoes_bp.route("/email/<int:config_id>/testar", methods=["POST"])
def email_testar(config_id):
    try:
        resultado = EmailConfigService.testar(config_id, request.form.get("destinatario"))
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash(f"E-mail de teste enviado para {resultado.get('destinatario')}.", "success")
    return redirect(request.referrer or url_for("configuracoes.email_index"))
