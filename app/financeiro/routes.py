from flask import Blueprint
from flask import render_template

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
        dashboard=dados
    )


@financeiro_bp.route("/dashboard/executivo")
def dashboard_executivo():

    dados = FinanceiroService.dashboard()

    return render_template(
        "dashboards/executivo.html",
        dashboard=dados
    )

