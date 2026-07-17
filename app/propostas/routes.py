from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import session
from flask import url_for

from app.propostas.service import PropostaService
from app.propostas.service import STATUS_PROPOSTA

propostas_bp = Blueprint("propostas", __name__, url_prefix="/propostas")


@propostas_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    status = request.args.get("status")
    ativo = request.args.get("ativo")
    pagina = request.args.get("page", 1, type=int)
    propostas, total = PropostaService.listar(pesquisa=pesquisa, status=status, ativo=ativo, pagina=pagina)
    total_paginas = (total + 49) // 50
    return render_template(
        "propostas/index.html",
        propostas=propostas,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa,
        selected_status=status,
        selected_ativo=ativo or "1",
        status_options=STATUS_PROPOSTA,
        placeholder="Buscar por código, solução, cliente, contato ou executivo...",
        page_title="Propostas",
        page_description="Propostas comerciais estruturadas com licenças, servidores e preview para impressão.",
        page_icon="bi-file-earmark-richtext-fill",
        page_button_text="Nova Proposta",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("propostas.novo"),
    )


@propostas_bp.route("/novo", methods=["GET", "POST"])
def novo():
    contexto = PropostaService.listar_contexto_form(_email_usuario_logado())
    if request.method == "POST":
        dados = _coletar_dados_form()
        try:
            proposta_id = PropostaService.criar(dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("propostas/form.html", modo="novo", proposta=PropostaService.preparar_form_payload(dados, contexto["codigo_sugerido"]), status_options=STATUS_PROPOSTA, **contexto)
        flash("Proposta cadastrada com sucesso.", "success")
        return redirect(url_for("propostas.visualizar", proposta_id=proposta_id))
    return render_template("propostas/form.html", modo="novo", proposta=PropostaService.preparar_form_payload(codigo_sugerido=contexto["codigo_sugerido"]), status_options=STATUS_PROPOSTA, **contexto)


@propostas_bp.route("/<int:proposta_id>")
def visualizar(proposta_id):
    proposta = PropostaService.buscar_por_id(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "danger")
        return redirect(url_for("propostas.index"))
    return render_template("propostas/view.html", proposta=proposta, status_options=STATUS_PROPOSTA, print_mode=False)


@propostas_bp.route("/<int:proposta_id>/imprimir")
def imprimir(proposta_id):
    proposta = PropostaService.buscar_por_id(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "danger")
        return redirect(url_for("propostas.index"))
    return render_template("propostas/view.html", proposta=proposta, status_options=STATUS_PROPOSTA, print_mode=True)


@propostas_bp.route("/<int:proposta_id>/exportar.docx")
def exportar_docx(proposta_id):
    proposta = PropostaService.buscar_por_id(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "danger")
        return redirect(url_for("propostas.index"))
    arquivo = PropostaService.gerar_docx(proposta)
    nome = (proposta.get("codigo_proposta") or f"proposta-{proposta_id}").lower() + ".docx"
    return send_file(arquivo, as_attachment=True, download_name=nome, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@propostas_bp.route("/<int:proposta_id>/editar", methods=["GET", "POST"])
def editar(proposta_id):
    proposta = PropostaService.buscar_por_id(proposta_id)
    contexto = PropostaService.listar_contexto_form(_email_usuario_logado())
    if not proposta:
        flash("Proposta não encontrada.", "danger")
        return redirect(url_for("propostas.index"))
    if request.method == "POST":
        dados = _coletar_dados_form()
        try:
            PropostaService.atualizar(proposta_id, dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            dados["id"] = proposta_id
            dados["codigo_proposta"] = proposta.get("codigo_proposta")
            return render_template("propostas/form.html", modo="editar", proposta=PropostaService.preparar_form_payload(dados, proposta.get("codigo_proposta")), status_options=STATUS_PROPOSTA, **contexto)
        flash("Proposta atualizada com sucesso.", "success")
        return redirect(url_for("propostas.visualizar", proposta_id=proposta_id))
    return render_template("propostas/form.html", modo="editar", proposta=PropostaService.preparar_form_payload(proposta, proposta.get("codigo_proposta")), status_options=STATUS_PROPOSTA, **contexto)


@propostas_bp.route("/<int:proposta_id>/excluir")
def excluir(proposta_id):
    proposta = PropostaService.buscar_por_id(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "danger")
    else:
        PropostaService.excluir(proposta_id)
        flash("Proposta removida com sucesso.", "success")
    return redirect(url_for("propostas.index"))


def _coletar_dados_form():
    return {
        "oportunidade_id": request.form.get("oportunidade_id"),
        "cliente_id": request.form.get("cliente_id"),
        "contato_id": request.form.get("contato_id"),
        "parceiro_id": request.form.get("parceiro_id"),
        "executivo_responsavel_id": request.form.get("executivo_responsavel_id"),
        "codigo_proposta": request.form.get("codigo_proposta"),
        "titulo": request.form.get("titulo"),
        "status": request.form.get("status"),
        "validade": request.form.get("validade"),
        "setup_dias": request.form.get("setup_dias"),
        "mensalidade_dias": request.form.get("mensalidade_dias"),
        "prazo_contratual_meses": request.form.get("prazo_contratual_meses"),
        "detalhes_negociacao": request.form.get("detalhes_negociacao"),
        "condicoes_comerciais": request.form.get("condicoes_comerciais"),
        "observacoes": request.form.get("observacoes"),
        "cliente_nome": request.form.get("cliente_nome"),
        "contato_nome": request.form.get("contato_nome"),
        "contato_email": request.form.get("contato_email"),
        "contato_telefone": request.form.get("contato_telefone"),
        "executivo_nome": request.form.get("executivo_nome"),
        "executivo_email": request.form.get("executivo_email"),
        "executivo_telefone": request.form.get("executivo_telefone"),
        "parametrizacao_sistema": request.form.get("parametrizacao_sistema"),
        "setup_ambiente_cloud": request.form.get("setup_ambiente_cloud"),
        "total_mensal": request.form.get("total_mensal"),
        "total_instalacao": request.form.get("total_instalacao"),
        "valor_total": request.form.get("valor_total"),
        "licencas_snapshot": request.form.get("licencas_snapshot"),
        "servidores_snapshot": request.form.get("servidores_snapshot"),
        "ativo": request.form.get("ativo", "0"),
    }


def _email_usuario_logado():
    for chave in ("user_email", "email", "usuario_email", "login_email"):
        valor = session.get(chave)
        if valor:
            return valor
    return None
