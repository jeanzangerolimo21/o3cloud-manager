from flask import Blueprint, render_template, request
from app.repositories.contrato_item_repository import ContratoItemRepository
from app.repositories.contrato_repository import ContratoRepository

contratos_bp = Blueprint(
    "contratos",
    __name__,
    url_prefix="/contratos"
)


@contratos_bp.route("/")
def index():

    pesquisa = request.args.get("q")

    pagina = request.args.get("page", 1, type=int)

    limit = 50

    offset = (pagina - 1) * limit

    contratos = ContratoRepository.listar(
        pesquisa,
        limit,
        offset
    )

    total = ContratoRepository.total(
        pesquisa
    )

    total_paginas = (total + limit - 1) // limit

    return render_template(

        "contratos/index.html",

        contratos=contratos,

        pesquisa=pesquisa,

        pagina=pagina,

        total=total,

        total_paginas=total_paginas

    )



@contratos_bp.route("/<int:contrato_id>")
def view(contrato_id):



    contrato = ContratoRepository.buscar_por_id(
        contrato_id
    )

    itens = ContratoItemRepository.listar_por_contrato(
        contrato_id
    )

    return render_template(
        "contratos/view.html",
        contrato=contrato,
        itens=itens
    )

