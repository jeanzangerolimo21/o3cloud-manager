from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for

from app.core.auditoria import registrar_evento
from app.contratos.service import ContratoService
from app.propostas.service import PropostaService
from app.implantacao.service import ImplantacaoService
from app.integracoes.omie.sync import OmieSync
from app.repositories.contrato_item_repository import ContratoItemRepository
from app.repositories.contrato_repository import ContratoRepository


contratos_bp = Blueprint("contratos", __name__, url_prefix="/contratos")


def _anexar_implantacoes(contratos):
    for contrato in contratos:
        implantacao = ImplantacaoService.buscar_por_contrato_id(contrato.get("id"))
        contrato["implantacao_id"] = implantacao.get("id") if implantacao else None


def _filtros():
    return {
        "pesquisa": request.args.get("q") or None,
        "status": request.args.get("status") or None,
        "origem": request.args.get("origem") or None,
        "data_de": request.args.get("data_de") or None,
        "data_ate": request.args.get("data_ate") or None,
    }


def _form_data():
    return {
        "cliente_id": request.form.get("cliente_id"),
        "contato_id": request.form.get("contato_id"),
        "proposta_id": request.form.get("proposta_id"),
        "numero": request.form.get("numero"),
        "descricao": request.form.get("descricao"),
        "status": request.form.get("status"),
        "inicio_vigencia": request.form.get("inicio_vigencia"),
        "fim_vigencia": request.form.get("fim_vigencia"),
        "contato_nome": request.form.get("contato_nome"),
        "contato_email": request.form.get("contato_email"),
        "contato_telefone": request.form.get("contato_telefone"),
        "data_fechamento": request.form.get("data_fechamento"),
        "executivo_id": request.form.get("executivo_id"),
        "parceiro_id": request.form.get("parceiro_id"),
        "tipo_venda": request.form.get("tipo_venda"),
        "valor_mensal": request.form.get("valor_mensal"),
        "valor_setup": request.form.get("valor_setup"),
        "valor_projeto": request.form.get("valor_projeto"),
        "valor_promocional": request.form.get("valor_promocional"),
        "quantidade_usuarios": request.form.get("quantidade_usuarios"),
        "data_inicio_recorrencia": request.form.get("data_inicio_recorrencia"),
        "data_ativacao": request.form.get("data_ativacao"),
        "dia_faturamento": request.form.get("dia_faturamento"),
        "observacoes": request.form.get("observacoes"),
    }


@contratos_bp.route("/sincronizar-omie")
def sincronizar_omie():
    try:
        resultado = OmieSync().sincronizar_contratos()
        registrar_evento("CONTRATOS_OMIE_SINCRONIZADOS", "contratos", None, resultado)
    except Exception as erro:
        flash(f"Erro ao sincronizar contratos Omie: {erro}", "danger")
    else:
        flash(
            "Sincronização de contratos Omie concluída: "
            f"{resultado.get('processados', 0)} processados, "
            f"{resultado.get('novos', 0)} novos, "
            f"{resultado.get('atualizados', 0)} atualizados, "
            f"{resultado.get('ignorados', 0)} ignorados.",
            "success",
        )
    return redirect(url_for("contratos.index"))


@contratos_bp.route("/")
def index():
    pagina = request.args.get("page", 1, type=int)
    filtros = _filtros()
    contratos, total, total_paginas = ContratoService.listar(filtros, pagina=pagina)
    _anexar_implantacoes(contratos)
    dashboard = ContratoService.dashboard(filtros)
    pendencias_upload = ContratoService.contar_encaminhados_sem_arquivo()

    return render_template(
        "contratos/index.html",
        contratos=contratos,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        filtros=filtros,
        dashboard=dashboard,
        pendencias_upload=pendencias_upload,
        status_options=ContratoService.STATUS_OPTIONS,
        view_mode="lista",
    )


@contratos_bp.route("/dashboard")
def dashboard():
    pagina = request.args.get("page", 1, type=int)
    filtros = _filtros()
    contratos, total, total_paginas = ContratoService.listar(filtros, pagina=pagina)
    _anexar_implantacoes(contratos)
    dashboard_dados = ContratoService.dashboard(filtros)
    pendencias_upload = ContratoService.contar_encaminhados_sem_arquivo()

    return render_template(
        "contratos/dashboard.html",
        contratos=contratos,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        filtros=filtros,
        dashboard=dashboard_dados,
        pendencias_upload=pendencias_upload,
        status_options=ContratoService.STATUS_OPTIONS,
        view_mode="dashboard",
    )


@contratos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    contexto = ContratoService.contexto_form()
    proposta_id = request.args.get("proposta_id", type=int)
    if proposta_id and request.method == "GET":
        proposta = PropostaService.buscar_por_id(proposta_id)
        if proposta:
            contexto["contrato"] = ContratoService._proposta_para_form(proposta_id)
            contexto["contrato"].update({
                "proposta_id": proposta_id,
                "numero": proposta.get("codigo_proposta"),
                "descricao": proposta.get("titulo"),
                "data_fechamento": date.today().isoformat(),
                "status": "RASCUNHO",
            })
        else:
            flash("Proposta não encontrada para gerar contrato.", "danger")

    if request.method == "POST":
        dados = _form_data()
        try:
            contrato_id = ContratoService.criar(dados, request.files.get("arquivo_preparado"))
            registrar_evento("CONTRATO_CRIADO", "contratos", contrato_id, {"numero": dados.get("numero"), "status": dados.get("status")})
            flash("Contrato criado como rascunho para assinatura.", "success")
            return redirect(url_for("contratos.view", contrato_id=contrato_id))
        except ValueError as exc:
            for erro in str(exc).split("|"):
                flash(erro, "danger")
            contexto["contrato"] = dados

    return render_template("contratos/form.html", modo="novo", **contexto)


@contratos_bp.route("/<int:contrato_id>/editar", methods=["GET", "POST"])
def editar(contrato_id):
    contrato = ContratoRepository.buscar_por_id(contrato_id)
    if not contrato:
        return redirect(url_for("contratos.index"))
    contexto = ContratoService.contexto_form()
    if request.method == "POST":
        dados = _form_data()
        try:
            if contrato["origem"] == "OMIE":
                ContratoService.atualizar_vinculos_comerciais(contrato_id, dados)
                registrar_evento("CONTRATO_VINCULOS_COMERCIAIS_ATUALIZADOS", "contratos", contrato_id, {"origem": contrato.get("origem")})
                flash("Vinculos comerciais do contrato Omie atualizados.", "success")
            else:
                ContratoService.atualizar(contrato_id, dados, request.files.get("arquivo_preparado"))
                registrar_evento("CONTRATO_ATUALIZADO", "contratos", contrato_id, {"numero": contrato.get("numero"), "status": dados.get("status")})
                flash("Contrato atualizado.", "success")
            return redirect(url_for("contratos.view", contrato_id=contrato_id))
        except ValueError as exc:
            for erro in str(exc).split("|"):
                flash(erro, "danger")
            contrato = {**contrato, **dados}

    return render_template("contratos/form.html", contrato=contrato, modo="editar", **contexto)


@contratos_bp.route("/<int:contrato_id>/iniciar-implantacao", methods=["POST"])
def iniciar_implantacao(contrato_id):
    try:
        implantacao_id, criada = ImplantacaoService.iniciar_por_contrato(contrato_id)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(request.referrer or url_for("contratos.view", contrato_id=contrato_id))
    registrar_evento("CONTRATO_IMPLANTACAO_INICIADA", "implantacoes", implantacao_id, {"contrato_id": contrato_id, "criada": criada})
    flash("Implantação criada." if criada else "Este contrato já possui implantação ativa.", "success" if criada else "info")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))


@contratos_bp.route("/<int:contrato_id>/upload-assinado", methods=["POST"])
def upload_assinado(contrato_id):
    try:
        ContratoService.salvar_assinado(contrato_id, request.files.get("arquivo_assinado"))
        registrar_evento("CONTRATO_ASSINADO_VINCULADO", "contratos", contrato_id)
        flash("Contrato assinado vinculado ao cliente.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(request.referrer or url_for("contratos.view", contrato_id=contrato_id))


@contratos_bp.route("/<int:contrato_id>/download")
def download(contrato_id):
    caminho, nome = ContratoService.caminho_assinado(contrato_id)
    if not caminho:
        abort(404)
    return send_file(caminho, as_attachment=True, download_name=nome, mimetype="application/pdf")


@contratos_bp.route("/<int:contrato_id>/abrir")
def abrir(contrato_id):
    caminho, nome = ContratoService.caminho_assinado(contrato_id)
    if not caminho:
        abort(404)
    return send_file(caminho, as_attachment=False, download_name=nome, mimetype="application/pdf")


@contratos_bp.route("/<int:contrato_id>/excluir")
def excluir(contrato_id):
    contrato = ContratoRepository.buscar_por_id(contrato_id)
    if not contrato:
        return redirect(url_for("contratos.index"))
    if contrato["origem"] != "MANUAL":
        flash("Contratos sincronizados do Omie nao podem ser excluidos.", "warning")
        return redirect(url_for("contratos.view", contrato_id=contrato_id))

    ContratoRepository.excluir(contrato_id)
    registrar_evento("CONTRATO_EXCLUIDO", "contratos", contrato_id, {"numero": contrato.get("numero")})
    flash("Contrato removido.", "success")
    return redirect(url_for("contratos.index"))


@contratos_bp.route("/<int:contrato_id>")
def view(contrato_id):
    contrato = ContratoRepository.buscar_por_id(contrato_id)
    if not contrato:
        return redirect(url_for("contratos.index"))
    implantacao = ImplantacaoService.buscar_por_contrato_id(contrato_id)
    contrato["implantacao_id"] = implantacao.get("id") if implantacao else None
    itens = ContratoItemRepository.listar_por_contrato(contrato_id)
    return render_template(
        "contratos/view.html",
        contrato=contrato,
        itens=itens,
        rastreabilidade=ImplantacaoService.rastreabilidade_por_contrato(contrato_id),
        diagnostico_pre_beta=ContratoService.diagnostico_pre_beta(contrato, implantacao),
        status_options=ContratoService.STATUS_OPTIONS,
    )
