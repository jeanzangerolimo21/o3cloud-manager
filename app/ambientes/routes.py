from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from app.ambientes.service import AmbienteService


ambientes_bp = Blueprint(

    "ambientes",

    __name__,

    url_prefix="/ambientes"

)


def obter_dados_formulario():

    return {

        "cliente_id": request.form.get("cliente_id"),

        "parceiro_id": request.form.get("parceiro_id"),

        "contrato_id": request.form.get("contrato_id"),

        "nome": request.form.get("nome"),

        "origem": request.form.get("origem"),

        "ambiente_tipo": request.form.get("ambiente_tipo"),

        "situacao": request.form.get("situacao"),

        "prefixo_proxmox": request.form.get("prefixo_proxmox"),

        "responsavel_implantacao": request.form.get("responsavel_implantacao"),

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


@ambientes_bp.route("/novo", methods=["GET", "POST"])
def novo():

    dependencias = AmbienteService.carregar_dependencias_formulario()

    if request.method == "POST":

        AmbienteService.criar(

            obter_dados_formulario()

        )

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

        AmbienteService.atualizar(

            ambiente_id,

            obter_dados_formulario()

        )

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
