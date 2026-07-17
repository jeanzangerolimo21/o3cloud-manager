from flask import Blueprint
from flask import render_template
from flask import request

from app.oportunidades.service import STATUS_OPORTUNIDADE
from app.pipeline.service import PipelineService


pipeline_bp = Blueprint(
    "pipeline",
    __name__,
    url_prefix="/pipeline-comercial"
)


@pipeline_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    colunas, resumo = PipelineService.carregar(pesquisa=pesquisa)

    return render_template(
        "pipeline/index.html",
        colunas=colunas,
        resumo=resumo,
        pesquisa=pesquisa,
        status_options=STATUS_OPORTUNIDADE,
        page_title="Pipeline Comercial",
        page_description="Visão do funil comercial baseada nas oportunidades ativas do CRM.",
        page_icon="bi-kanban-fill",
    )
