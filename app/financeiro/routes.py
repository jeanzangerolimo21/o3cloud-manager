import csv
import io

from flask import Blueprint
from flask import Response
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from app.financeiro.inadimplencias_service import InadimplenciaService
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


@financeiro_bp.route("/financeiro/inadimplentes")
def inadimplentes():
    pagina = max(1, request.args.get("page", 1, type=int))
    filtros = {
        "q": request.args.get("q"),
        "status": request.args.get("status"),
        "data_de": request.args.get("data_de"),
        "data_ate": request.args.get("data_ate"),
        "responsavel_id": request.args.get("responsavel_id"),
    }
    itens, total = InadimplenciaService.listar(filtros, pagina=pagina)
    return render_template(
        "financeiro/inadimplencias/index.html",
        inadimplencias=itens,
        total=total,
        pagina=pagina,
        total_paginas=(total + 49) // 50,
        filtros=filtros,
        status_options=InadimplenciaService.STATUS,
        tipos_liberacao=InadimplenciaService.TIPOS_LIBERACAO,
    )


@financeiro_bp.route("/financeiro/inadimplentes/nova", methods=["GET", "POST"])
def nova_inadimplencia():
    if request.method == "POST":
        try:
            inadimplencia_id = InadimplenciaService.registrar(
                request.form,
                usuario_id=session.get("usuario_id"),
                usuario_email=_email_usuario_logado(),
            )
        except ValueError as erro:
            flash(str(erro), "danger")
        else:
            flash("Pendência financeira registrada.", "success")
            return redirect(url_for("financeiro.visualizar_inadimplencia", inadimplencia_id=inadimplencia_id))
    pesquisa = request.args.get("q") or request.form.get("q")
    return render_template(
        "financeiro/inadimplencias/form.html",
        inadimplencia=request.form if request.method == "POST" else {},
        pesquisa=pesquisa,
        modo="novo",
        **InadimplenciaService.contexto_form(pesquisa),
    )


@financeiro_bp.route("/financeiro/inadimplentes/contratos")
def pesquisar_contratos_inadimplencia():
    pesquisa = (request.args.get("q") or "").strip()
    contratos = InadimplenciaService.contratos_para_busca(pesquisa)
    return jsonify({"contratos": contratos})


@financeiro_bp.route("/financeiro/inadimplentes/<int:inadimplencia_id>")
def visualizar_inadimplencia(inadimplencia_id):
    inadimplencia = InadimplenciaService.buscar_por_id(inadimplencia_id)
    if not inadimplencia:
        flash("Inadimplência não encontrada.", "danger")
        return redirect(url_for("financeiro.inadimplentes"))
    return render_template(
        "financeiro/inadimplencias/view.html",
        inadimplencia=inadimplencia,
        pendencias_cliente=InadimplenciaService.pendencias_cliente(inadimplencia.get("cliente_id")),
        tipos_liberacao=InadimplenciaService.TIPOS_LIBERACAO,
    )


@financeiro_bp.route("/financeiro/inadimplentes/<int:inadimplencia_id>/excluir", methods=["POST"])
def excluir_inadimplencia(inadimplencia_id):
    if session.get("usuario_perfil") != "ADMIN":
        flash("Apenas Administrador pode excluir histórico de inadimplência.", "danger")
        return redirect(url_for("financeiro.visualizar_inadimplencia", inadimplencia_id=inadimplencia_id))
    try:
        InadimplenciaService.excluir_historico(inadimplencia_id)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(url_for("financeiro.visualizar_inadimplencia", inadimplencia_id=inadimplencia_id))
    flash("Histórico de inadimplência removido da lista.", "success")
    return redirect(url_for("financeiro.inadimplentes"))


@financeiro_bp.route("/financeiro/inadimplentes/<int:inadimplencia_id>/liberar", methods=["POST"])
def liberar_inadimplencia(inadimplencia_id):
    try:
        InadimplenciaService.liberar(
            inadimplencia_id,
            request.form,
            usuario_id=session.get("usuario_id"),
            usuario_email=_email_usuario_logado(),
        )
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Pendência financeira liberada.", "success")
    return redirect(url_for("financeiro.visualizar_inadimplencia", inadimplencia_id=inadimplencia_id))


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



def _email_usuario_logado():
    for chave in ("usuario_email", "email", "user_email", "login_email"):
        valor = session.get(chave)
        if valor:
            return valor
    return "sistema"
