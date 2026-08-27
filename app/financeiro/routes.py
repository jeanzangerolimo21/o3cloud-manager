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

from app.configuracoes.sincronismos_service import SincronismosAgendadosService
from app.financeiro.inadimplencias_service import InadimplenciaService
from app.financeiro.reajuste_service import ReajusteContratoService
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


@financeiro_bp.route("/financeiro/comissoes")
def comissoes():

    filtros = FinanceiroService.filtros_comissoes(request.args)
    pagina = max(1, request.args.get("page", 1, type=int))
    limite = 50
    resumo = FinanceiroService.resumo_comissoes_contratos(filtros)
    total = int(resumo.get("total") or 0)
    total_paginas = max(1, (total + limite - 1) // limite)
    if pagina > total_paginas:
        pagina = total_paginas

    return render_template(
        "financeiro/comissoes.html",
        comissoes=FinanceiroService.listar_comissoes_contratos(filtros, pagina=pagina, limite=limite),
        resumo=resumo,
        filtros=filtros,
        campanhas=FinanceiroService.listar_campanhas_comissao(),
        campanha_selecionada=FinanceiroService.buscar_campanha_comissao(filtros.get("campanha_id")),
        status_options=FinanceiroService.status_comissoes(),
        status_premiacao_manual_options=FinanceiroService.status_premiacao_manual_options(),
        pagina=pagina,
        total_paginas=total_paginas,
        total=total,
    )


@financeiro_bp.route("/financeiro/comissoes/<int:contrato_id>/status-premiacao", methods=["POST"])
def atualizar_status_premiacao(contrato_id):

    dados = request.get_json(silent=True) or request.form
    try:
        resultado = FinanceiroService.atualizar_status_premiacao_manual(
            contrato_id,
            dados.get("campanha_id"),
            dados.get("status"),
            _email_usuario_logado(),
        )
    except ValueError as erro:
        return jsonify({"ok": False, "erro": str(erro)}), 400
    return jsonify({"ok": True, **resultado})


@financeiro_bp.route("/financeiro/comissoes/<int:contrato_id>/calcular", methods=["GET", "POST"])
def calcular_comissao(contrato_id):

    campanha_id = request.args.get("campanha_id", type=int) or request.form.get("campanha_id", type=int)
    contrato = FinanceiroService.buscar_comissao_contrato(contrato_id, campanha_id)
    if not contrato:
        flash("Contrato ativo não encontrado para cálculo de premiação.", "danger")
        return redirect(url_for("financeiro.comissoes"))

    if not contrato.get("premiacao_liberada"):
        flash("Contrato sem parceiro ou executivo habilitado para premiação.", "warning")
        destino = url_for("financeiro.comissoes", campanha_id=campanha_id) if campanha_id else url_for("financeiro.comissoes")
        return redirect(destino)

    calculo = None
    valor_manual_base = request.form.get("valor_manual_base") if request.method == "POST" else ""
    if request.method == "POST":
        try:
            calculo = FinanceiroService.calcular_comissao_manual(contrato, request.form)
            flash("Premiação calculada para conferência financeira.", "success")
        except ValueError as erro:
            flash(str(erro), "danger")

    return render_template(
        "financeiro/comissao_calculo.html",
        contrato=contrato,
        campanhas=FinanceiroService.campanhas_contrato(contrato_id),
        calculo=calculo,
        valor_manual_base=valor_manual_base,
    )


@financeiro_bp.route("/financeiro/receitas-servidor")
def receitas_servidor():

    filtros = FinanceiroService.filtros_receitas_servidor(request.args)
    dashboard = FinanceiroService.receitas_por_servidor(filtros)

    return render_template(
        "financeiro/receitas_servidor.html",
        dashboard=dashboard,
        filtros=filtros,
    )




@financeiro_bp.route("/financeiro/reajustes-contratuais")
def reajustes_contratuais():

    filtros = ReajusteContratoService.filtros(request.args)
    contexto = ReajusteContratoService.contexto(filtros)

    return render_template(
        "financeiro/reajustes_contratuais.html",
        filtros=filtros,
        **contexto,
    )


@financeiro_bp.route("/financeiro/reajustes-contratuais/configuracao", methods=["POST"])
def reajustes_contratuais_configuracao():

    try:
        ReajusteContratoService.salvar_configuracao(request.form, _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Configuracao de reajustes contratuais atualizada.", "success")
    return redirect(url_for("financeiro.reajustes_contratuais"))


@financeiro_bp.route("/financeiro/reajustes-contratuais/sincronizar-omie", methods=["POST"])
def reajustes_contratuais_sincronizar_omie():
    try:
        resultado = SincronismosAgendadosService.executar_manual_por_tipo(
            "OMIE_FATURAMENTO_PREVISOES",
            _email_usuario_logado(),
        )
    except Exception as erro:
        flash("Falha ao sincronizar Faturamento e Previsoes OMIE: {}".format(erro), "danger")
    else:
        flash(resultado, "success" if ": OK" in resultado else "warning")
    return redirect(url_for("financeiro.reajustes_contratuais"))


@financeiro_bp.route("/financeiro/reajustes-contratuais/verificar", methods=["POST"])
def reajustes_contratuais_verificar():

    resultado = ReajusteContratoService.processar_alertas(_email_usuario_logado())
    flash(
        "Verificacao concluida: {} alerta(s) registrado(s), {} e-mail(s) enviado(s).".format(
            resultado.get("criados", 0), resultado.get("emails", 0)
        ),
        "success",
    )
    return redirect(url_for("financeiro.reajustes_contratuais"))


@financeiro_bp.route("/financeiro/faturamentos")
def faturamentos():

    filtros_recebimentos = FinanceiroService.filtros_recebimentos(request.args)
    pagina_recebimentos = max(1, request.args.get("recebimentos_page", 1, type=int))
    limite_recebimentos = 50
    resumo_recebimentos = FinanceiroService.resumo_recebimentos_omie(filtros_recebimentos)
    total_recebimentos = int(resumo_recebimentos.get("total") or 0)
    total_paginas_recebimentos = max(1, (total_recebimentos + limite_recebimentos - 1) // limite_recebimentos)
    if pagina_recebimentos > total_paginas_recebimentos:
        pagina_recebimentos = total_paginas_recebimentos

    return render_template(
        "financeiro/faturamentos.html",
        faturamentos=FinanceiroService.listar_faturamentos(),
        resumo=FinanceiroService.resumo_faturamentos(),
        recebimentos=FinanceiroService.listar_recebimentos_omie(filtros_recebimentos, pagina=pagina_recebimentos, limite=limite_recebimentos),
        resumo_recebimentos=resumo_recebimentos,
        filtros_recebimentos=filtros_recebimentos,
        pagina_recebimentos=pagina_recebimentos,
        total_paginas_recebimentos=total_paginas_recebimentos,
        total_recebimentos=total_recebimentos,
        situacoes_recebimentos=FinanceiroService.situacoes_recebimentos_omie(),
    )


@financeiro_bp.route("/financeiro/faturamentos/sincronizar-recebimentos-omie", methods=["POST"])
def sincronizar_recebimentos_omie():

    try:
        resultado = SincronismosAgendadosService.executar_manual_por_tipo("OMIE_RECEBIMENTOS", _email_usuario_logado())
    except Exception as erro:
        flash("Falha ao sincronizar recebimentos OMIE: {}".format(erro), "danger")
    else:
        flash(resultado, "success" if ": OK" in resultado else "warning")
    return redirect(url_for("financeiro.faturamentos"))


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
