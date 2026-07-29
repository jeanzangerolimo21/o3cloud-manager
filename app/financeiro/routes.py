import csv
import io

from flask import Blueprint
from flask import Response
from flask import flash
from flask import render_template
from flask import request

from app.financeiro.service import FinanceiroService

financeiro_bp = Blueprint(
    "financeiro",
    __name__
)


@financeiro_bp.route("/")
def dashboard():

    dados = FinanceiroService.dashboard()

    return render_template(
        "dashboards/index.html",
        dashboard=dados,
    )


@financeiro_bp.route("/financeiro/faturamentos", methods=["GET", "POST"])
def faturamentos():

    resumo_importacao = None

    if request.method == "POST":
        try:
            resumo_importacao = FinanceiroService.importar_faturamentos_csv(request.files.get("arquivo"))
            if resumo_importacao["erros"]:
                flash("Importacao concluida com erros. Verifique o resumo abaixo.", "warning")
            else:
                flash("Faturamentos importados com sucesso.", "success")
        except Exception as erro:
            flash(str(erro), "danger")

    return render_template(
        "financeiro/faturamentos.html",
        faturamentos=FinanceiroService.listar_faturamentos(),
        resumo=FinanceiroService.resumo_faturamentos(),
        resumo_importacao=resumo_importacao,
    )


@financeiro_bp.route("/financeiro/faturamentos/modelo.csv")
def exportar_modelo_faturamentos_csv():

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow([
        "contrato_id",
        "contrato_numero",
        "contrato_codigo_externo",
        "cliente",
        "competencia",
        "valor_bruto",
        "percentual_comissao",
        "valor_comissao",
        "valor_liquido",
        "origem",
        "observacoes",
    ])
    writer.writerows(FinanceiroService.linhas_modelo_faturamentos())

    return Response(
        buffer.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=faturamentos_modelo.csv",
        },
    )


@financeiro_bp.route("/dashboard/executivo")
def dashboard_executivo():

    filtros = FinanceiroService.filtros_dashboard(request.args)
    dados = FinanceiroService.dashboard(filtros)

    return render_template(
        "dashboards/executivo.html",
        dashboard=dados,
        filtros=filtros,
        dashboard_links=FinanceiroService.links_dashboard(filtros),
        **FinanceiroService.contexto_dashboard(),
    )

@financeiro_bp.route("/dashboard/produtos-clientes")
def produtos_clientes():

    filtros = FinanceiroService.filtros_produtos_clientes(request.args)
    dados = FinanceiroService.produtos_clientes(filtros)

    return render_template(
        "dashboards/produtos_clientes.html",
        dashboard=dados,
        filtros=filtros,
        status_options={
            "RASCUNHO": "Rascunho",
            "EM_ELABORACAO": "Em elaboracao",
            "ENCAMINHADO_PROJETO": "Encaminhado para projeto",
            "ATIVO": "Ativo",
            "CONCLUIDO": "Concluido",
            "CANCELADO": "Cancelado",
        },
    )

