from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from app.leads.service import LeadService
from app.leads.service import ORIGEM_LEAD
from app.leads.service import STATUS_LEAD


leads_bp = Blueprint(
    "leads",
    __name__,
    url_prefix="/leads"
)


@leads_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    status = request.args.get("status")
    origem = request.args.get("origem")
    ativo = request.args.get("ativo")
    pagina = request.args.get("page", 1, type=int)

    leads, total = LeadService.listar(
        pesquisa=pesquisa,
        status=status,
        origem=origem,
        ativo=ativo,
        pagina=pagina,
    )

    total_paginas = (total + 49) // 50

    return render_template(
        "leads/index.html",
        leads=leads,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa,
        selected_status=status,
        selected_origem=origem,
        selected_ativo=ativo or "1",
        status_options=STATUS_LEAD,
        origem_options=ORIGEM_LEAD,
        placeholder="Buscar por empresa, contato, e-mail ou interesse...",
        page_title="Leads",
        page_description="Gestão inicial de oportunidades do CRM Comercial.",
        page_icon="bi-bullseye",
        page_button_text="Novo Lead",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("leads.novo"),
    )


@leads_bp.route("/novo", methods=["GET", "POST"])
def novo():
    parceiros = LeadService.listar_parceiros()
    executivos = LeadService.listar_executivos()

    if request.method == "POST":
        dados = _coletar_dados_form()
        try:
            LeadService.criar(dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template(
                "leads/form.html",
                modo="novo",
                lead=_lead_form_payload(),
                parceiros=parceiros,
                executivos=executivos,
                status_options=STATUS_LEAD,
                origem_options=ORIGEM_LEAD,
            )

        flash("Lead cadastrado com sucesso.", "success")
        return redirect(url_for("leads.index"))

    return render_template(
        "leads/form.html",
        modo="novo",
        lead=None,
        parceiros=parceiros,
        executivos=executivos,
        status_options=STATUS_LEAD,
        origem_options=ORIGEM_LEAD,
    )


@leads_bp.route("/<int:lead_id>")
def visualizar(lead_id):
    lead = LeadService.buscar_por_id(lead_id)

    if not lead:
        flash("Lead não encontrado.", "danger")
        return redirect(url_for("leads.index"))

    return render_template(
        "leads/view.html",
        lead=lead,
        status_options=STATUS_LEAD,
        origem_options=ORIGEM_LEAD,
    )


@leads_bp.route("/<int:lead_id>/editar", methods=["GET", "POST"])
def editar(lead_id):
    lead = LeadService.buscar_por_id(lead_id)
    parceiros = LeadService.listar_parceiros()
    executivos = LeadService.listar_executivos()

    if not lead:
        flash("Lead não encontrado.", "danger")
        return redirect(url_for("leads.index"))

    if request.method == "POST":
        dados = _coletar_dados_form()
        try:
            LeadService.atualizar(lead_id, dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            lead_form = _lead_form_payload()
            lead_form["id"] = lead_id
            return render_template(
                "leads/form.html",
                modo="editar",
                lead=lead_form,
                parceiros=parceiros,
                executivos=executivos,
                status_options=STATUS_LEAD,
                origem_options=ORIGEM_LEAD,
            )

        flash("Lead atualizado com sucesso.", "success")
        return redirect(url_for("leads.visualizar", lead_id=lead_id))

    return render_template(
        "leads/form.html",
        modo="editar",
        lead=lead,
        parceiros=parceiros,
        executivos=executivos,
        status_options=STATUS_LEAD,
        origem_options=ORIGEM_LEAD,
    )


@leads_bp.route("/<int:lead_id>/excluir")
def excluir(lead_id):
    lead = LeadService.buscar_por_id(lead_id)

    if not lead:
        flash("Lead não encontrado.", "danger")
    else:
        LeadService.excluir(lead_id)
        flash("Lead removido com sucesso.", "success")

    return redirect(url_for("leads.index"))


def _coletar_dados_form():
    return {
        "parceiro_id": request.form.get("parceiro_id"),
        "executivo_responsavel_id": request.form.get("executivo_responsavel_id"),
        "empresa": request.form.get("empresa"),
        "nome_contato": request.form.get("nome_contato"),
        "cargo": request.form.get("cargo"),
        "email": request.form.get("email"),
        "telefone": request.form.get("telefone"),
        "origem": request.form.get("origem"),
        "interesse": request.form.get("interesse"),
        "status": request.form.get("status"),
        "cidade": request.form.get("cidade"),
        "uf": request.form.get("uf"),
        "observacoes": request.form.get("observacoes"),
        "ativo": request.form.get("ativo", "0"),
    }


def _lead_form_payload():
    return {
        "parceiro_id": request.form.get("parceiro_id"),
        "executivo_responsavel_id": request.form.get("executivo_responsavel_id"),
        "empresa": request.form.get("empresa"),
        "nome_contato": request.form.get("nome_contato"),
        "cargo": request.form.get("cargo"),
        "email": request.form.get("email"),
        "telefone": request.form.get("telefone"),
        "origem": request.form.get("origem", "OUTRO"),
        "interesse": request.form.get("interesse"),
        "status": request.form.get("status", "NOVO"),
        "cidade": request.form.get("cidade"),
        "uf": request.form.get("uf"),
        "observacoes": request.form.get("observacoes"),
        "ativo": request.form.get("ativo") == "1",
    }
