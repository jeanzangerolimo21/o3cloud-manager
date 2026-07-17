from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from app.contatos.service import CANAL_PREFERIDO
from app.contatos.service import ContatoService
from app.contatos.service import TIPO_CONTATO


contatos_bp = Blueprint(
    "contatos",
    __name__,
    url_prefix="/contatos"
)


@contatos_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    tipo_contato = request.args.get("tipo")
    ativo = request.args.get("ativo")
    pagina = request.args.get("page", 1, type=int)

    contatos, total = ContatoService.listar(
        pesquisa=pesquisa,
        tipo_contato=tipo_contato,
        ativo=ativo,
        pagina=pagina,
    )

    total_paginas = (total + 49) // 50

    return render_template(
        "contatos/index.html",
        contatos=contatos,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa,
        selected_tipo=tipo_contato,
        selected_ativo=ativo or "1",
        tipo_options=TIPO_CONTATO,
        placeholder="Buscar por nome, empresa, e-mail, telefone ou vínculo...",
        page_title="Contatos",
        page_description="Gestão de contatos vinculados ao CRM Comercial.",
        page_icon="bi-person-lines-fill",
        page_button_text="Novo Contato",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("contatos.novo"),
    )


@contatos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    parceiros = ContatoService.listar_parceiros()
    executivos = ContatoService.listar_executivos()
    leads = ContatoService.listar_leads()

    if request.method == "POST":
        dados = _coletar_dados_form()
        try:
            ContatoService.criar(dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template(
                "contatos/form.html",
                modo="novo",
                contato=_contato_form_payload(),
                parceiros=parceiros,
                executivos=executivos,
                leads=leads,
                tipo_options=TIPO_CONTATO,
                canal_options=CANAL_PREFERIDO,
            )

        flash("Contato cadastrado com sucesso.", "success")
        return redirect(url_for("contatos.index"))

    return render_template(
        "contatos/form.html",
        modo="novo",
        contato=None,
        parceiros=parceiros,
        executivos=executivos,
        leads=leads,
        tipo_options=TIPO_CONTATO,
        canal_options=CANAL_PREFERIDO,
    )


@contatos_bp.route("/<int:contato_id>")
def visualizar(contato_id):
    contato = ContatoService.buscar_por_id(contato_id)

    if not contato:
        flash("Contato não encontrado.", "danger")
        return redirect(url_for("contatos.index"))

    return render_template(
        "contatos/view.html",
        contato=contato,
        tipo_options=TIPO_CONTATO,
        canal_options=CANAL_PREFERIDO,
    )


@contatos_bp.route("/<int:contato_id>/editar", methods=["GET", "POST"])
def editar(contato_id):
    contato = ContatoService.buscar_por_id(contato_id)
    parceiros = ContatoService.listar_parceiros()
    executivos = ContatoService.listar_executivos()
    leads = ContatoService.listar_leads()

    if not contato:
        flash("Contato não encontrado.", "danger")
        return redirect(url_for("contatos.index"))

    if request.method == "POST":
        dados = _coletar_dados_form()
        try:
            ContatoService.atualizar(contato_id, dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            contato_form = _contato_form_payload()
            contato_form["id"] = contato_id
            return render_template(
                "contatos/form.html",
                modo="editar",
                contato=contato_form,
                parceiros=parceiros,
                executivos=executivos,
                leads=leads,
                tipo_options=TIPO_CONTATO,
                canal_options=CANAL_PREFERIDO,
            )

        flash("Contato atualizado com sucesso.", "success")
        return redirect(url_for("contatos.visualizar", contato_id=contato_id))

    return render_template(
        "contatos/form.html",
        modo="editar",
        contato=contato,
        parceiros=parceiros,
        executivos=executivos,
        leads=leads,
        tipo_options=TIPO_CONTATO,
        canal_options=CANAL_PREFERIDO,
    )


@contatos_bp.route("/<int:contato_id>/excluir")
def excluir(contato_id):
    contato = ContatoService.buscar_por_id(contato_id)

    if not contato:
        flash("Contato não encontrado.", "danger")
    else:
        ContatoService.excluir(contato_id)
        flash("Contato removido com sucesso.", "success")

    return redirect(url_for("contatos.index"))


def _coletar_dados_form():
    return {
        "lead_id": request.form.get("lead_id"),
        "parceiro_id": request.form.get("parceiro_id"),
        "executivo_responsavel_id": request.form.get("executivo_responsavel_id"),
        "empresa": request.form.get("empresa"),
        "nome": request.form.get("nome"),
        "cargo": request.form.get("cargo"),
        "email": request.form.get("email"),
        "telefone": request.form.get("telefone"),
        "whatsapp": request.form.get("whatsapp"),
        "tipo_contato": request.form.get("tipo_contato"),
        "canal_preferido": request.form.get("canal_preferido"),
        "cidade": request.form.get("cidade"),
        "uf": request.form.get("uf"),
        "observacoes": request.form.get("observacoes"),
        "ativo": request.form.get("ativo", "0"),
    }


def _contato_form_payload():
    return {
        "lead_id": request.form.get("lead_id"),
        "parceiro_id": request.form.get("parceiro_id"),
        "executivo_responsavel_id": request.form.get("executivo_responsavel_id"),
        "empresa": request.form.get("empresa"),
        "nome": request.form.get("nome"),
        "cargo": request.form.get("cargo"),
        "email": request.form.get("email"),
        "telefone": request.form.get("telefone"),
        "whatsapp": request.form.get("whatsapp"),
        "tipo_contato": request.form.get("tipo_contato", "COMERCIAL"),
        "canal_preferido": request.form.get("canal_preferido", "WHATSAPP"),
        "cidade": request.form.get("cidade"),
        "uf": request.form.get("uf"),
        "observacoes": request.form.get("observacoes"),
        "ativo": request.form.get("ativo") == "1",
    }
