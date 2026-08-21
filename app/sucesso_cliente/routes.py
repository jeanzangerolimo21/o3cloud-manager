from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.core.auditoria import registrar_evento
from app.sucesso_cliente.service import STATUS_RELACIONAMENTO, SucessoClienteService


sucesso_cliente_bp = Blueprint("sucesso_cliente", __name__, url_prefix="/sucesso-cliente")


@sucesso_cliente_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    curva = request.args.get("curva")
    status_relacionamento = request.args.get("status_relacionamento")
    pagina = request.args.get("page", 1, type=int)
    contratos, total = SucessoClienteService.listar(pesquisa, curva, status_relacionamento, pagina)
    total_paginas = (total + 49) // 50
    return render_template(
        "sucesso_cliente/index.html",
        contratos=contratos,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        dashboard=SucessoClienteService.dashboard(),
        pesquisa=pesquisa,
        selected_curva=curva,
        selected_status=status_relacionamento,
        status_options=STATUS_RELACIONAMENTO,
        page_title="Sucesso do Cliente",
        page_description="Acompanhamento de contratos ativos, curva de cliente e relacionamento CS.",
        page_icon="bi-heart-pulse-fill",
    )


@sucesso_cliente_bp.route("/<int:contrato_id>")
def visualizar(contrato_id):
    contrato = SucessoClienteService.detalhe(contrato_id)
    if not contrato:
        flash("Contrato não encontrado.", "danger")
        return redirect(url_for("sucesso_cliente.index"))
    return render_template("sucesso_cliente/view.html", contrato=contrato, status_options=STATUS_RELACIONAMENTO)


@sucesso_cliente_bp.route("/<int:contrato_id>/relacionamento", methods=["POST"])
def registrar_relacionamento(contrato_id):
    try:
        historico_id = SucessoClienteService.registrar_relacionamento(
            contrato_id,
            request.form,
            request.files.getlist("anexos"),
            _email_usuario_logado(),
        )
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        registrar_evento("CS_RELACIONAMENTO_REGISTRADO", "crm_sucesso_cliente_historico", historico_id, {"contrato_id": contrato_id, "status": request.form.get("status_relacionamento")})
        flash("Relacionamento registrado com sucesso.", "success")
    return redirect(url_for("sucesso_cliente.visualizar", contrato_id=contrato_id))


@sucesso_cliente_bp.route("/<int:contrato_id>/contato", methods=["POST"])
def vincular_contato(contrato_id):
    try:
        SucessoClienteService.vincular_contato(contrato_id, request.form.get("contato_id"), _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        registrar_evento("CS_CONTATO_VINCULADO", "crm_sucesso_cliente", contrato_id, {"contato_id": request.form.get("contato_id")})
        flash("Contato vinculado ao acompanhamento CS.", "success")
    return redirect(url_for("sucesso_cliente.visualizar", contrato_id=contrato_id))


@sucesso_cliente_bp.route("/<int:contrato_id>/critico", methods=["POST"])
def atualizar_critico(contrato_id):
    try:
        historico_id = SucessoClienteService.marcar_critico(contrato_id, _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        registrar_evento("CS_RELACIONAMENTO_CRITICO", "crm_sucesso_cliente_historico", historico_id, {"contrato_id": contrato_id})
        flash("Contrato marcado como crítico.", "success")
    return redirect(request.referrer or url_for("sucesso_cliente.index"))


def _email_usuario_logado():
    return session.get("usuario_email") or session.get("email") or "sistema"
