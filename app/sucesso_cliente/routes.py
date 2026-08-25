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
        dashboard_pesquisas=SucessoClienteService.dashboard_pesquisas(),
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


@sucesso_cliente_bp.route("/pesquisa-implantacao/<int:pesquisa_id>")
def detalhe_pesquisa_implantacao(pesquisa_id):
    pesquisa = SucessoClienteService.buscar_pesquisa_interna(pesquisa_id)
    if not pesquisa:
        flash("Pesquisa não encontrada.", "danger")
        return redirect(url_for("sucesso_cliente.index"))
    return render_template("sucesso_cliente/pesquisa_detalhe.html", pesquisa=pesquisa)


@sucesso_cliente_bp.route("/<int:contrato_id>/pesquisa-implantacao/nova")
def nova_pesquisa_implantacao(contrato_id):
    try:
        contrato, pesquisa = SucessoClienteService.nova_pesquisa_payload(contrato_id, request.args)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(url_for("sucesso_cliente.index"))
    return render_template("sucesso_cliente/pesquisa_form.html", contrato=contrato, pesquisa=pesquisa)


@sucesso_cliente_bp.route("/<int:contrato_id>/pesquisa-implantacao/preview", methods=["POST"])
def preview_pesquisa_implantacao(contrato_id):
    try:
        contrato, pesquisa = SucessoClienteService.preview_pesquisa(contrato_id, request.form)
    except ValueError as erro:
        flash(str(erro), "danger")
        contrato, pesquisa = SucessoClienteService.nova_pesquisa_payload(contrato_id, request.form)
        return render_template("sucesso_cliente/pesquisa_form.html", contrato=contrato, pesquisa=pesquisa)
    return render_template("sucesso_cliente/pesquisa_preview.html", contrato=contrato, pesquisa=pesquisa)


@sucesso_cliente_bp.route("/<int:contrato_id>/pesquisa-implantacao/enviar", methods=["POST"])
def enviar_pesquisa_implantacao(contrato_id):
    try:
        pesquisas, resultados, links = SucessoClienteService.enviar_pesquisa(
            contrato_id,
            request.form,
            lambda token: url_for("sucesso_cliente.responder_pesquisa", token=token, _external=True),
            _email_usuario_logado(),
        )
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(url_for("sucesso_cliente.nova_pesquisa_implantacao", contrato_id=contrato_id))
    enviados = sum(1 for resultado in resultados if resultado.get("enviado"))
    registrar_evento("CS_PESQUISA_IMPLANTACAO_ENVIADA", "crm_sucesso_cliente_pesquisas", pesquisas[0]["id"] if pesquisas else None, {"contrato_id": contrato_id, "total_destinatarios": len(resultados), "emails_enviados": enviados})
    if enviados == len(resultados):
        flash(f"Pesquisa enviada para {enviados} destinatário(s).", "success")
    elif enviados:
        flash(f"Pesquisa criada para {len(resultados)} destinatário(s), com {enviados} e-mail(s) enviados. Links manuais disponíveis no histórico do contrato.", "warning")
    else:
        flash(f"Pesquisa criada, mas nenhum e-mail foi enviado. Links manuais disponíveis no histórico do contrato.", "warning")
    return redirect(url_for("sucesso_cliente.visualizar", contrato_id=contrato_id))


@sucesso_cliente_bp.route("/pesquisa/<token>", methods=["GET", "POST"])
def responder_pesquisa(token):
    pesquisa = SucessoClienteService.buscar_pesquisa_publica(token)
    if not pesquisa:
        return render_template("sucesso_cliente/pesquisa_publica.html", pesquisa=None), 404
    if request.method == "POST":
        try:
            SucessoClienteService.registrar_resposta_pesquisa(token, request.form, request.remote_addr, request.headers.get("User-Agent"))
        except ValueError as erro:
            flash(str(erro), "danger")
        else:
            flash("Obrigado. Sua avaliação foi registrada.", "success")
            pesquisa = SucessoClienteService.buscar_pesquisa_publica(token)
            return render_template("sucesso_cliente/pesquisa_publica.html", pesquisa=pesquisa, respondida=True)
    return render_template("sucesso_cliente/pesquisa_publica.html", pesquisa=pesquisa)


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
