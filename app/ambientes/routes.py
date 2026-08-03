from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from app.ambientes.service import AmbienteService
from app.ambientes.implantador_service import ImplantadorService


ambientes_bp = Blueprint(

    "ambientes",

    __name__,

    url_prefix="/ambientes"

)


def obter_dados_formulario():

    return {

        "cliente_id": request.form.get("cliente_id"),

        "cliente_ids": request.form.getlist("cliente_ids"),

        "parceiro_id": request.form.get("parceiro_id"),

        "contrato_id": request.form.get("contrato_id"),

        "contrato_ids": request.form.getlist("contrato_ids"),

        "recurso_ids": request.form.getlist("recurso_ids"),

        "nome": request.form.get("nome"),

        "origem": request.form.get("origem"),

        "ambiente_tipo": request.form.get("ambiente_tipo"),

        "situacao": request.form.get("situacao"),

        "prefixo_proxmox": request.form.get("prefixo_proxmox"),

        "responsavel_implantacao": request.form.get("responsavel_implantacao"),

        "implantador_id": request.form.get("implantador_id"),

        "descricao": request.form.get("descricao"),

        "observacoes": request.form.get("observacoes"),

        "ativo": 1 if request.form.get("ativo") else 0

    }


@ambientes_bp.route("/")
def index():

    pesquisa = request.args.get("q")

    pagina = request.args.get("page", 1, type=int)

    ambientes, total = AmbienteService.listar(

        pesquisa=pesquisa,

        pagina=pagina

    )

    total_paginas = (total + 49) // 50

    return render_template(

        "ambientes/index.html",

        ambientes=ambientes,

        pesquisa=pesquisa,

        pagina=pagina,

        total=total,

        total_paginas=total_paginas,

        placeholder="Pesquisar por Ambiente, Cliente ou Prefixo"

    )




def _dados_implantador_formulario():
    return {
        "nome": request.form.get("nome"),
        "email": request.form.get("email"),
        "telefone": request.form.get("telefone"),
        "observacoes": request.form.get("observacoes"),
        "ativo": 1 if request.form.get("ativo") else 0,
    }


@ambientes_bp.route("/implantadores")
def implantadores():
    pesquisa = request.args.get("q")
    pagina = request.args.get("page", 1, type=int)
    implantadores, total = ImplantadorService.listar(pesquisa=pesquisa, pagina=pagina)
    return render_template(
        "ambientes/implantadores/index.html",
        implantadores=implantadores,
        pesquisa=pesquisa,
        pagina=pagina,
        total=total,
        total_paginas=(total + 49) // 50,
        placeholder="Pesquisar por implantador",
    )


@ambientes_bp.route("/implantadores/novo", methods=["GET", "POST"])
def novo_implantador():
    if request.method == "POST":
        try:
            ImplantadorService.criar(_dados_implantador_formulario())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("ambientes/implantadores/form.html", implantador=request.form, modo="novo")
        flash("Implantador cadastrado com sucesso.", "success")
        return redirect(url_for("ambientes.implantadores"))
    return render_template("ambientes/implantadores/form.html", implantador={"ativo": 1}, modo="novo")


@ambientes_bp.route("/implantadores/<int:implantador_id>/editar", methods=["GET", "POST"])
def editar_implantador(implantador_id):
    implantador = ImplantadorService.buscar_por_id(implantador_id)
    if not implantador:
        flash("Implantador não encontrado.", "danger")
        return redirect(url_for("ambientes.implantadores"))
    if request.method == "POST":
        try:
            ImplantadorService.atualizar(implantador_id, _dados_implantador_formulario())
        except ValueError as erro:
            flash(str(erro), "danger")
            implantador = {**implantador, **request.form}
            return render_template("ambientes/implantadores/form.html", implantador=implantador, modo="editar")
        flash("Implantador atualizado com sucesso.", "success")
        return redirect(url_for("ambientes.implantadores"))
    return render_template("ambientes/implantadores/form.html", implantador=implantador, modo="editar")


@ambientes_bp.route("/implantadores/<int:implantador_id>/excluir")
def excluir_implantador(implantador_id):
    ImplantadorService.inativar(implantador_id)
    flash("Implantador inativado com sucesso.", "success")
    return redirect(url_for("ambientes.implantadores"))


@ambientes_bp.route("/novo", methods=["GET", "POST"])
def novo():

    dependencias = AmbienteService.carregar_dependencias_formulario()

    if request.method == "POST":

        try:
            AmbienteService.criar(

                obter_dados_formulario()

            )
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("ambientes/form.html", modo="novo", ambiente=request.form, **dependencias)

        flash(

            "Ambiente cadastrado com sucesso.",

            "success"

        )

        return redirect(

            url_for("ambientes.index")

        )

    return render_template(

        "ambientes/form.html",

        modo="novo",

        **dependencias

    )


@ambientes_bp.route("/<int:ambiente_id>")
def visualizar(ambiente_id):

    ambiente = AmbienteService.buscar_por_id(

        ambiente_id

    )

    return render_template(

        "ambientes/view.html",

        ambiente=ambiente

    )


@ambientes_bp.route("/<int:ambiente_id>/editar", methods=["GET", "POST"])
def editar(ambiente_id):

    ambiente = AmbienteService.buscar_por_id(

        ambiente_id

    )

    if not ambiente:

        return redirect(

            url_for("ambientes.index")

        )

    dependencias = AmbienteService.carregar_dependencias_formulario()

    if request.method == "POST":

        try:
            AmbienteService.atualizar(

                ambiente_id,

                obter_dados_formulario()

            )
        except ValueError as erro:
            flash(str(erro), "danger")
            ambiente = {**ambiente, **request.form}
            return render_template("ambientes/form.html", ambiente=ambiente, modo="editar", **dependencias)

        flash(

            "Ambiente atualizado com sucesso.",

            "success"

        )

        return redirect(

            url_for(

                "ambientes.visualizar",

                ambiente_id=ambiente_id

            )

        )

    return render_template(

        "ambientes/form.html",

        ambiente=ambiente,

        modo="editar",

        **dependencias

    )


@ambientes_bp.route("/<int:ambiente_id>/excluir")
def excluir(ambiente_id):

    AmbienteService.excluir(

        ambiente_id

    )

    flash(

        "Ambiente removido com sucesso.",

        "success"

    )

    return redirect(

        url_for(

            "ambientes.index"

        )

    )
