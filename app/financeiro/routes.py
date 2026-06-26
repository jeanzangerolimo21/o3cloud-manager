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

