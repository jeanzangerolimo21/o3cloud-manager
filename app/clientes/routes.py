from flask import Blueprint
from flask import render_template
from flask import flash
from flask import request
from flask import redirect
from flask import url_for
from app.clientes.implantacao_service import ImplantacaoService
from app.clientes.service import ClienteService
from app.integracoes.omie.sync import OmieSync


clientes_bp = Blueprint(

    "clientes",

    __name__,

    url_prefix="/clientes"

)


@clientes_bp.route("/sincronizar-omie")
def sincronizar_omie():
    try:
        OmieSync().sincronizar_clientes()
    except Exception as erro:
        flash(f"Erro ao sincronizar clientes Omie: {erro}", "danger")
    else:
        flash("Sincronização de clientes Omie concluída com sucesso.", "success")
    return redirect(url_for("clientes.index"))


@clientes_bp.route("/")
def index():

    pesquisa = request.args.get("q")

    pagina = int(request.args.get("page", 1))

    ativo = request.args.get("ativo")

    origem = request.args.get("origem")

    clientes, total = ClienteService.listar(

        pesquisa=pesquisa,

        ativo=ativo,

        origem=origem,

        pagina=pagina

    )
    
    total_paginas = (total + 49) // 50

    return render_template(

        "clientes/index.html",

        clientes=clientes,

        total=total,

        pesquisa=pesquisa,

        status=ativo,

        status_field="ativo",

        origem=origem,

        pagina=pagina,

        total_paginas=total_paginas,

        placeholder="Pesquisar por Nome, Razão Social ou CNPJ",

        show_status=True,

        show_origem=True,

        status_options={

            "1": "🟢 Ativo",

            "0": "⚫ Inativo"

        }

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

@clientes_bp.route("/excluir-em-massa", methods=["POST"])
def excluir_em_massa():
    ids = request.form.getlist("cliente_ids")
    if ids:
        ClienteService.excluir_manuais(ids)
        flash(f"{len(ids)} cliente(s) manual(is) removido(s) com sucesso.", "success")
    return redirect(url_for("clientes.index"))

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

        implantacao=implantacao,

        diagnostico_pre_beta=ClienteService.diagnostico_pre_beta(cliente, implantacao)

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
