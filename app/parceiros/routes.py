from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from app.core.storage import StorageService
from app.parceiros.service import ParceiroService


parceiros_bp = Blueprint(

    "parceiros",

    __name__,

    url_prefix="/parceiros"

)


@parceiros_bp.route("/")
def index():

    pesquisa = request.args.get("q")

    pagina = request.args.get("page", 1, type=int)

    parceiros, total = ParceiroService.listar(

        pesquisa=pesquisa,

        pagina=pagina

    )

    total_paginas = (total + 49) // 50

    return render_template(

        "parceiros/index.html",

        parceiros=parceiros,

        pesquisa=pesquisa,

        pagina=pagina,

        total=total,

        total_paginas=total_paginas,

        placeholder="Pesquisar por Nome ou Sigla",

        page_title="Parceiros",

        page_description="Cadastro dos parceiros comerciais da O3 Cloud.",

        page_icon="bi-people-fill",

        page_button_text="Novo Parceiro",

        page_button_icon="bi-plus-circle",

        page_button_url=url_for("parceiros.novo"),

    )


@parceiros_bp.route("/novo", methods=["GET", "POST"])
def novo():

    if request.method == "POST":

        logo = None

        arquivo = request.files.get("logo")

        if arquivo and arquivo.filename:

            try:

                logo = StorageService.salvar(

                    arquivo,

                    StorageService.PARCEIROS

                )

            except ValueError as erro:

                return render_template(

                    "parceiros/form.html",

                    modo="novo",

                    erro=str(erro)

                )

        dados = {

            "nome": request.form.get("nome"),

            "sigla": request.form.get("sigla"),

            "tipo": request.form.get("tipo"),

            "contato": request.form.get("contato"),

            "email": request.form.get("email"),

            "telefone": request.form.get("telefone"),

            "site": request.form.get("site"),

            "descricao": request.form.get("descricao"),

            "logo": logo,

            "ativo": 1 if request.form.get("ativo") else 0

        }

        ParceiroService.criar(dados)

        flash(

            "Parceiro cadastrado com sucesso.",

            "success"

        )

        return redirect(url_for("parceiros.index"))

    return render_template(

        "parceiros/form.html",

        modo="novo"

    )


@parceiros_bp.route("/<int:parceiro_id>")
def visualizar(parceiro_id):

    parceiro = ParceiroService.buscar_por_id(

        parceiro_id

    )

    return render_template(

        "parceiros/view.html",

        parceiro=parceiro

    )


@parceiros_bp.route("/<int:parceiro_id>/editar", methods=["GET", "POST"])
def editar(parceiro_id):

    parceiro = ParceiroService.buscar_por_id(

        parceiro_id

    )

    if not parceiro:

        return redirect(url_for("parceiros.index"))

    if request.method == "POST":

        logo = parceiro.get("logo")

        arquivo = request.files.get("logo")

        if arquivo and arquivo.filename:

            try:

                novo_logo = StorageService.salvar(

                    arquivo,

                    StorageService.PARCEIROS

                )

                if parceiro.get("logo"):

                    StorageService.excluir(

                        StorageService.PARCEIROS,

                        parceiro.get("logo")

                    )

                logo = novo_logo

            except ValueError as erro:

                return render_template(

                    "parceiros/form.html",

                    parceiro=parceiro,

                    modo="editar",

                    erro=str(erro)

                )

        dados = {

            "nome": request.form.get("nome"),

            "sigla": request.form.get("sigla"),

            "tipo": request.form.get("tipo"),

            "contato": request.form.get("contato"),

            "email": request.form.get("email"),

            "telefone": request.form.get("telefone"),

            "site": request.form.get("site"),

            "descricao": request.form.get("descricao"),

            "logo": logo,

            "ativo": 1 if request.form.get("ativo") else 0

        }

        ParceiroService.atualizar(

            parceiro_id,

            dados

        )
        
        flash(

            "Parceiro atualizado com sucesso.",

            "success"

        )

        return redirect(

            url_for(

                "parceiros.visualizar",

                parceiro_id=parceiro_id

            )

        )

    return render_template(

        "parceiros/form.html",

        parceiro=parceiro,

        modo="editar"

    )


@parceiros_bp.route("/<int:parceiro_id>/excluir")
def excluir(parceiro_id):

    parceiro = ParceiroService.buscar_por_id(
        parceiro_id
    )

    if parceiro and parceiro.get("logo"):

        StorageService.excluir(

            StorageService.PARCEIROS,

            parceiro.get("logo")

        )


    ParceiroService.excluir(

        parceiro_id

    )

    flash(

        "Parceiro removido com sucesso.",

        "success"

    )


    return redirect(

        url_for("parceiros.index")

    )
