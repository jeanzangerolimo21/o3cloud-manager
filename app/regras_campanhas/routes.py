from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from app.core.auditoria import registrar_evento
from app.regras_campanhas.service import RegraCampanhaService


regras_campanhas_bp = Blueprint("regras_campanhas", __name__, url_prefix="/regras-campanhas")


@regras_campanhas_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    ativo = request.args.get("ativo", "1")
    pagina = request.args.get("page", 1, type=int)
    regras, total = RegraCampanhaService.listar(pesquisa=pesquisa, ativo=ativo, pagina=pagina)
    total_paginas = (total + 49) // 50
    return render_template(
        "regras_campanhas/index.html",
        regras=regras,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa,
        selected_ativo=ativo,
        placeholder="Buscar por campanha ou descrição...",
        page_title="Regras Campanhas",
        page_description="Campanhas de comissão com percentual e vigência controlada.",
        page_icon="bi-percent",
        page_button_text="Nova Regra",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("regras_campanhas.novo"),
    )


@regras_campanhas_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        try:
            regra_id = RegraCampanhaService.criar(request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("regras_campanhas/form.html", modo="novo", regra=request.form, **RegraCampanhaService.contexto_form(request.form))
        registrar_evento("REGRA_CAMPANHA_CRIADA", "regras_campanhas_comissao", regra_id, {"nome": request.form.get("nome"), "vigencia_inicio": request.form.get("vigencia_inicio"), "vigencia_fim": request.form.get("vigencia_fim")})
        flash("Regra de campanha cadastrada.", "success")
        return redirect(url_for("regras_campanhas.index"))
    return render_template("regras_campanhas/form.html", modo="novo", regra={"ativo": 1}, contratos_elegiveis=[])


@regras_campanhas_bp.route("/<int:regra_id>/editar", methods=["GET", "POST"])
def editar(regra_id):
    regra = RegraCampanhaService.buscar_por_id(regra_id)
    if not regra:
        flash("Regra de campanha não encontrada.", "danger")
        return redirect(url_for("regras_campanhas.index"))
    if request.method == "POST":
        try:
            RegraCampanhaService.atualizar(regra_id, request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            regra = {**regra, **request.form}
            return render_template("regras_campanhas/form.html", modo="editar", regra=regra, **RegraCampanhaService.contexto_form(regra))
        registrar_evento("REGRA_CAMPANHA_ATUALIZADA", "regras_campanhas_comissao", regra_id, {"nome": request.form.get("nome"), "vigencia_inicio": request.form.get("vigencia_inicio"), "vigencia_fim": request.form.get("vigencia_fim")})
        flash("Regra de campanha atualizada.", "success")
        return redirect(url_for("regras_campanhas.index"))
    return render_template("regras_campanhas/form.html", modo="editar", regra=regra, **RegraCampanhaService.contexto_form(regra))


@regras_campanhas_bp.route("/<int:regra_id>/excluir", methods=["POST"])
def excluir(regra_id):
    try:
        RegraCampanhaService.excluir(regra_id, _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        registrar_evento("REGRA_CAMPANHA_INATIVADA", "regras_campanhas_comissao", regra_id)
        flash("Regra de campanha inativada.", "success")
    return redirect(url_for("regras_campanhas.index"))


def _email_usuario_logado():
    for chave in ("usuario_email", "email", "user_email", "login_email"):
        valor = session.get(chave)
        if valor:
            return valor
    return "sistema"
