from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from app.configuracoes.email_service import EmailConfigService


configuracoes_bp = Blueprint("configuracoes", __name__, url_prefix="/configuracoes")


def _email_usuario_logado():
    return session.get("usuario_email") or session.get("email") or "sistema"


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
