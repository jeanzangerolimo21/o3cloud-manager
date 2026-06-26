from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from app.clientes.implantacao_service import ImplantacaoService
from app.clientes.service import ClienteService


clientes_bp = Blueprint(

    "clientes",

    __name__,

    url_prefix="/clientes"

)


@clientes_bp.route("/")
def index():

    pesquisa = request.args.get("q")

    pagina = int(request.args.get("page", 1))

    clientes, total = ClienteService.listar(

        pesquisa=pesquisa,

        pagina=pagina

    )
    
    import math

    total_paginas = math.ceil(total / 50)

    return render_template(

        "clientes/index.html",

        clientes=clientes,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa

    )


@clientes_bp.route("/novo", methods=["GET", "POST"])
def novo():

    if request.method == "POST":

        dados = {

            "codigo_externo": None,

            "origem": "MANUAL",

            "nome_fantasia": request.form.get("nome_fantasia"),

            "razao_social": request.form.get("razao_social"),

            "cnpj": request.form.get("cnpj"),

            "email": request.form.get("email"),

            "telefone": request.form.get("telefone"),

            "cidade": request.form.get("cidade"),

            "estado": request.form.get("estado")

        }

        ClienteService.criar(dados)

        return redirect(url_for("clientes.index"))

    return render_template(

        "clientes/form.html"

    )

@clientes_bp.route("/<int:id>/excluir")
def excluir(id):

    ClienteService.excluir(id)

    return redirect(url_for("clientes.index"))


@clientes_bp.route("/<int:id>")
def visualizar(id):

    cliente = ClienteService.buscar_por_id(id)

    implantacao = ImplantacaoService.buscar(id)

    return render_template(

        "clientes/view.html",

        cliente=cliente,

        implantacao=implantacao

    )
@clientes_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):

    cliente = ClienteService.buscar_por_id(id)

    if not cliente:
        return redirect(url_for("clientes.index"))

    if request.method == "POST":

        dados = {
            "nome_fantasia": request.form.get("nome_fantasia"),
            "razao_social": request.form.get("razao_social"),
            "cnpj": request.form.get("cnpj"),
            "email": request.form.get("email"),
            "telefone": request.form.get("telefone"),
            "cidade": request.form.get("cidade"),
            "estado": request.form.get("estado"),
        }

        ClienteService.atualizar(id, dados)

        return redirect(url_for("clientes.visualizar", id=id))

    return render_template(
        "clientes/form.html",
        cliente=cliente,
        modo="editar"
    )
