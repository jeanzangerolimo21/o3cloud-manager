from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from app.oportunidades.service import OportunidadeService
from app.oportunidades.service import STATUS_OPORTUNIDADE


oportunidades_bp = Blueprint(
    "oportunidades",
    __name__,
    url_prefix="/oportunidades"
)


@oportunidades_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    status = request.args.get("status")
    ativo = request.args.get("ativo")
    pagina = request.args.get("page", 1, type=int)

    oportunidades, total = OportunidadeService.listar(
        pesquisa=pesquisa,
        status=status,
        ativo=ativo,
        pagina=pagina,
    )

    total_paginas = (total + 49) // 50

    return render_template(
        "oportunidades/index.html",
        oportunidades=oportunidades,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa,
        selected_status=status,
        selected_ativo=ativo or "1",
        status_options=STATUS_OPORTUNIDADE,
        placeholder="Buscar por título, empresa, ERP, cliente, parceiro ou responsável...",
        page_title="Oportunidades",
        page_description="Negociações ativas do CRM Comercial.",
        page_icon="bi-briefcase-fill",
        page_button_text="Nova Oportunidade",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("oportunidades.novo"),
    )


@oportunidades_bp.route("/novo", methods=["GET", "POST"])
def novo():
    contexto = _carregar_contexto_formulario()

    if request.method == "POST":
        dados = _coletar_dados_form()
        try:
            OportunidadeService.criar(dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template(
                "oportunidades/form.html",
                modo="novo",
                oportunidade=_oportunidade_form_payload(),
                status_options=STATUS_OPORTUNIDADE,
                **contexto,
            )

        flash("Oportunidade cadastrada com sucesso.", "success")
        return redirect(url_for("oportunidades.index"))

    return render_template(
        "oportunidades/form.html",
        modo="novo",
        oportunidade=_oportunidade_query_payload(),
        status_options=STATUS_OPORTUNIDADE,
        **contexto,
    )


@oportunidades_bp.route("/<int:oportunidade_id>")
def visualizar(oportunidade_id):
    oportunidade = OportunidadeService.buscar_por_id(oportunidade_id)

    if not oportunidade:
        flash("Oportunidade não encontrada.", "danger")
        return redirect(url_for("oportunidades.index"))

    return render_template(
        "oportunidades/view.html",
        oportunidade=oportunidade,
        status_options=STATUS_OPORTUNIDADE,
    )


@oportunidades_bp.route("/<int:oportunidade_id>/editar", methods=["GET", "POST"])
def editar(oportunidade_id):
    oportunidade = OportunidadeService.buscar_por_id(oportunidade_id)
    contexto = _carregar_contexto_formulario()

    if not oportunidade:
        flash("Oportunidade não encontrada.", "danger")
        return redirect(url_for("oportunidades.index"))

    if request.method == "POST":
        dados = _coletar_dados_form()
        try:
            OportunidadeService.atualizar(oportunidade_id, dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            oportunidade_form = _oportunidade_form_payload()
            oportunidade_form["id"] = oportunidade_id
            return render_template(
                "oportunidades/form.html",
                modo="editar",
                oportunidade=oportunidade_form,
                status_options=STATUS_OPORTUNIDADE,
                **contexto,
            )

        flash("Oportunidade atualizada com sucesso.", "success")
        return redirect(url_for("oportunidades.visualizar", oportunidade_id=oportunidade_id))

    return render_template(
        "oportunidades/form.html",
        modo="editar",
        oportunidade=oportunidade,
        status_options=STATUS_OPORTUNIDADE,
        **contexto,
    )


@oportunidades_bp.route("/excluir-em-massa", methods=["POST"])
def excluir_em_massa():
    ids = request.form.getlist("oportunidade_ids")
    if ids:
        OportunidadeService.excluir_em_massa(ids)
        flash(f"{len(ids)} oportunidade(s) removida(s) com sucesso.", "success")
    return redirect(url_for("oportunidades.index"))

@oportunidades_bp.route("/<int:oportunidade_id>/excluir")
def excluir(oportunidade_id):
    oportunidade = OportunidadeService.buscar_por_id(oportunidade_id)

    if not oportunidade:
        flash("Oportunidade não encontrada.", "danger")
    else:
        OportunidadeService.excluir(oportunidade_id)
        flash("Oportunidade removida com sucesso.", "success")

    return redirect(url_for("oportunidades.index"))


def _carregar_contexto_formulario():
    return {
        "leads": OportunidadeService.listar_leads(),
        "contatos": OportunidadeService.listar_contatos(),
        "clientes": OportunidadeService.listar_clientes(),
        "parceiros": OportunidadeService.listar_parceiros(),
        "executivos": OportunidadeService.listar_executivos(),
    }


def _coletar_dados_form():
    return {
        "lead_id": request.form.get("lead_id"),
        "contato_id": request.form.get("contato_id"),
        "cliente_id": request.form.get("cliente_id"),
        "parceiro_id": request.form.get("parceiro_id"),
        "executivo_responsavel_id": request.form.get("executivo_responsavel_id"),
        "titulo": request.form.get("titulo"),
        "empresa": request.form.get("empresa"),
        "erp": request.form.get("erp"),
        "quantidade_usuarios": request.form.get("quantidade_usuarios"),
        "valor_estimado": request.form.get("valor_estimado"),
        "probabilidade": request.form.get("probabilidade"),
        "status": request.form.get("status"),
        "observacoes": request.form.get("observacoes"),
        "ativo": request.form.get("ativo", "0"),
    }


def _oportunidade_query_payload():
    if not any(request.args.get(campo) for campo in ("titulo", "empresa", "observacoes")):
        return None
    return {
        "titulo": request.args.get("titulo", "")[:180],
        "empresa": request.args.get("empresa", "")[:150],
        "observacoes": request.args.get("observacoes", "")[:4000],
        "status": "NOVA",
        "ativo": True,
    }


def _oportunidade_form_payload():
    return {
        "lead_id": request.form.get("lead_id"),
        "contato_id": request.form.get("contato_id"),
        "cliente_id": request.form.get("cliente_id"),
        "parceiro_id": request.form.get("parceiro_id"),
        "executivo_responsavel_id": request.form.get("executivo_responsavel_id"),
        "titulo": request.form.get("titulo"),
        "empresa": request.form.get("empresa"),
        "erp": request.form.get("erp"),
        "quantidade_usuarios": request.form.get("quantidade_usuarios"),
        "valor_estimado": request.form.get("valor_estimado"),
        "probabilidade": request.form.get("probabilidade"),
        "status": request.form.get("status", "NOVA"),
        "observacoes": request.form.get("observacoes"),
        "ativo": request.form.get("ativo") == "1",
    }
