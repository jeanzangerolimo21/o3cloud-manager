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

    status = request.args.get("status")

    origem = request.args.get("origem")

    pagina = request.args.get("page", 1, type=int)

    limit = 50

    offset = (pagina - 1) * limit

    contratos = ContratoRepository.listar(
        pesquisa=pesquisa,
        status=status,
        origem=origem,
        limit=limit,
        offset=offset
    )

    total = ContratoRepository.total(
        pesquisa=pesquisa,
        status=status,
        origem=origem
    )

    total_paginas = (total + limit - 1) // limit

    return render_template(

        "contratos/index.html",
        
        contratos=contratos,

        pesquisa=pesquisa,

        status=status,

        selected_status=status,

        status_field="status",

        origem=origem,

        pagina=pagina,

        total=total,

        total_paginas=total_paginas,

        placeholder="Pesquisar por Número ou Cliente",

        show_status=True,

        show_origem=True,

        status_options={

            "EM_ELABORACAO": "🟡 Em Elaboração",

            "EM_IMPLANTACAO": "🔵 Em Implantação",

            "ATIVO": "🟢 Ativo",

            "SUSPENSO": "🟠 Suspenso",

            "CANCELADO": "🔴 Cancelado",

            "ENCERRADO": "⚫ Encerrado"

        }

    )

@contratos_bp.route("/novo", methods=["GET", "POST"])
def novo():

    from app.clientes.service import ClienteService
    from app.contratos.service import ContratoService
    from flask import redirect, url_for

    clientes = ClienteService.listar_todos()

    if request.method == "POST":

        dados = {

            "cliente_id": request.form.get("cliente_id"),

            "numero": request.form.get("numero"),

            "descricao": request.form.get("descricao"),

            "status": request.form.get("status"),

            "inicio_vigencia": request.form.get("inicio_vigencia"),

            "fim_vigencia": request.form.get("fim_vigencia"),

            "valor_mensal": request.form.get("valor_mensal"),

            "dia_faturamento": request.form.get("dia_faturamento"),

            "observacoes": request.form.get("observacoes")

        }

        ContratoService.criar(dados)

        return redirect(url_for("contratos.index"))

    return render_template(

        "contratos/form.html",

        clientes=clientes,

        modo="novo"

    )

@contratos_bp.route("/<int:contrato_id>/editar", methods=["GET", "POST"])
def editar(contrato_id):

    from flask import redirect, url_for

    from app.clientes.service import ClienteService

    from app.contratos.service import ContratoService

    contrato = ContratoRepository.buscar_por_id(contrato_id)

    if not contrato:

        return redirect(url_for("contratos.index"))

    if contrato["origem"] != "MANUAL":

        return redirect(url_for("contratos.view", contrato_id=contrato_id))

    clientes = ClienteService.listar_todos()

    if request.method == "POST":

        dados = {

            "cliente_id": request.form.get("cliente_id"),

            "numero": request.form.get("numero"),

            "descricao": request.form.get("descricao"),

            "status": request.form.get("status"),

            "inicio_vigencia": request.form.get("inicio_vigencia"),

            "fim_vigencia": request.form.get("fim_vigencia"),

            "valor_mensal": request.form.get("valor_mensal"),

            "dia_faturamento": request.form.get("dia_faturamento"),

            "observacoes": request.form.get("observacoes")

        }

        ContratoService.atualizar(

            contrato_id,

            dados

        )

        return redirect(

            url_for(

                "contratos.view",

                contrato_id=contrato_id

            )

        )

    return render_template(

        "contratos/form.html",

        contrato=contrato,

        clientes=clientes,

        modo="editar"

    )

@contratos_bp.route("/<int:contrato_id>/excluir")
def excluir(contrato_id):

    from flask import redirect, url_for

    contrato = ContratoRepository.buscar_por_id(contrato_id)

    if not contrato:
        return redirect(url_for("contratos.index"))

    if contrato["origem"] != "MANUAL":
        return redirect(url_for("contratos.view", contrato_id=contrato_id))

    ContratoRepository.excluir(contrato_id)

    return redirect(url_for("contratos.index"))


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

