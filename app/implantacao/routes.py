from flask import Blueprint
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from app.implantacao.service import ImplantacaoService
from app.implantacao.service import KANBAN_COLUNAS
from app.implantacao.service import KANBAN_LABELS
from app.implantacao.service import PRIORIDADE_IMPLANTACAO
from app.implantacao.service import STATUS_CHECKLIST
from app.implantacao.service import STATUS_IMPLANTACAO
from app.implantacao.service import STATUS_PROVISIONAMENTO
from app.implantacao.o3web_licencas_service import O3WebLicencaService
from app.implantacao.o3web_licencas_service import TIPOS_LICENCA_O3WEB


implantacao_bp = Blueprint("implantacao", __name__, url_prefix="/implantacao")


@implantacao_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    status = request.args.get("status")
    responsavel = request.args.get("responsavel")
    ativo = request.args.get("ativo", "1")
    pagina = request.args.get("page", 1, type=int)
    implantacoes, total = ImplantacaoService.listar(
        pesquisa=pesquisa,
        status=status,
        responsavel=responsavel,
        ativo=ativo,
        pagina=pagina,
    )
    total_paginas = (total + 49) // 50
    return render_template(
        "implantacao/index.html",
        implantacoes=implantacoes,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa,
        selected_status=status,
        responsavel=responsavel,
        selected_ativo=ativo,
        status_options=STATUS_IMPLANTACAO,
        dashboard=ImplantacaoService.dashboard(),
        page_title="Implantação",
        page_description="Workflow técnico pós-contrato encaminhado para projeto.",
        page_icon="bi-hdd-network",
        page_button_text="Nova Implantação",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("implantacao.novo"),
    )



@implantacao_bp.route("/licencas-o3web")
def licencas_o3web():
    pesquisa = request.args.get("q")
    tipo = request.args.get("tipo")
    ativo = request.args.get("ativo", "1")
    pagina = request.args.get("page", 1, type=int)
    licencas, total = O3WebLicencaService.listar(
        pesquisa=pesquisa,
        tipo=tipo,
        ativo=ativo,
        pagina=pagina,
    )
    total_paginas = (total + 49) // 50
    return render_template(
        "implantacao/licencas_o3web/index.html",
        licencas=licencas,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa,
        selected_tipo=tipo,
        selected_ativo=ativo,
        tipo_options=TIPOS_LICENCA_O3WEB,
        dashboard=O3WebLicencaService.dashboard(),
        page_title="Licenças O3Web",
        page_description="Controle operacional de licenças por usuários da aplicação O3Web.",
        page_icon="bi-key-fill",
        page_button_text="Importar CSV",
        page_button_icon="bi-upload",
        page_button_url=url_for("implantacao.importar_licencas_o3web"),
    )


@implantacao_bp.route("/licencas-o3web/importar", methods=["GET", "POST"])
def importar_licencas_o3web():
    resumo = None
    if request.method == "POST":
        try:
            resumo = O3WebLicencaService.importar_csv(request.files.get("arquivo"))
        except ValueError as erro:
            flash(str(erro), "danger")
        else:
            flash(
                f"Importação concluída: {resumo['criadas']} criada(s), {resumo['atualizadas']} atualizada(s), {resumo['ignoradas']} ignorada(s).",
                "success" if not resumo.get("erros") else "warning",
            )
    return render_template(
        "implantacao/licencas_o3web/importar.html",
        resumo=resumo,
        page_title="Importar Licenças O3Web",
        page_description="Importação CSV das licenças da aplicação O3Web.",
        page_icon="bi-upload",
        page_button_text="Voltar",
        page_button_icon="bi-arrow-left",
        page_button_url=url_for("implantacao.licencas_o3web"),
    )


@implantacao_bp.route("/licencas-o3web/novo", methods=["GET", "POST"])
def nova_licenca_o3web():
    if request.method == "POST":
        try:
            licenca_id = O3WebLicencaService.criar(_licenca_o3web_form_data())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("implantacao/licencas_o3web/form.html", licenca=request.form, tipo_options=TIPOS_LICENCA_O3WEB, modo="novo")
        flash("Licença O3Web cadastrada.", "success")
        return redirect(url_for("implantacao.editar_licenca_o3web", licenca_id=licenca_id))
    return render_template("implantacao/licencas_o3web/form.html", licenca={}, tipo_options=TIPOS_LICENCA_O3WEB, modo="novo")


@implantacao_bp.route("/licencas-o3web/<int:licenca_id>/editar", methods=["GET", "POST"])
def editar_licenca_o3web(licenca_id):
    licenca = O3WebLicencaService.buscar_por_id(licenca_id)
    if not licenca:
        flash("Licença O3Web não encontrada.", "danger")
        return redirect(url_for("implantacao.licencas_o3web"))
    if request.method == "POST":
        try:
            O3WebLicencaService.atualizar(licenca_id, _licenca_o3web_form_data())
        except ValueError as erro:
            flash(str(erro), "danger")
            licenca = {**licenca, **request.form}
        else:
            flash("Licença O3Web atualizada.", "success")
            return redirect(url_for("implantacao.licencas_o3web"))
    return render_template("implantacao/licencas_o3web/form.html", licenca=licenca, tipo_options=TIPOS_LICENCA_O3WEB, modo="editar")


@implantacao_bp.route("/licencas-o3web/<int:licenca_id>/excluir", methods=["POST"])
def excluir_licenca_o3web(licenca_id):
    try:
        O3WebLicencaService.excluir(licenca_id)
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Licença O3Web inativada.", "success")
    return redirect(url_for("implantacao.licencas_o3web"))


@implantacao_bp.route("/kanban")
def kanban():
    return render_template(
        "implantacao/kanban.html",
        colunas=ImplantacaoService.kanban(),
        kanban_labels=KANBAN_LABELS,
        page_title="Kanban de Implantação",
        page_description="Organização operacional das etapas de projeto.",
        page_icon="bi-kanban-fill",
        page_button_text="Nova Implantação",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("implantacao.novo"),
    )


@implantacao_bp.route("/kanban/mover", methods=["POST"])
def mover_kanban():
    dados = request.get_json(silent=True) or request.form
    try:
        resultado = ImplantacaoService.mover_kanban(
            int(dados.get("implantacao_id")),
            dados.get("etapa_kanban"),
        )
    except (TypeError, ValueError) as erro:
        return jsonify({"ok": False, "erro": str(erro)}), 400
    return jsonify({"ok": True, **resultado})

@implantacao_bp.route("/novo", methods=["GET", "POST"])
def novo():
    contratos = ImplantacaoService.listar_contratos_elegiveis()
    contexto = ImplantacaoService.contexto_form()
    if request.method == "POST":
        dados = _form_data()
        try:
            implantacao_id = ImplantacaoService.criar(dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template(
                "implantacao/form.html",
                modo="novo",
                implantacao=dados,
                contratos=contratos,
                contratos_origem=_contratos_origem_json(contratos),
                status_options=STATUS_IMPLANTACAO,
                prioridade_options=PRIORIDADE_IMPLANTACAO,
                provisionamento_options=STATUS_PROVISIONAMENTO,
                kanban_options=KANBAN_COLUNAS,
                **contexto,
            )
        flash("Implantação criada com checklist padrão.", "success")
        return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))

    return render_template(
        "implantacao/form.html",
        modo="novo",
        implantacao={},
        contratos=contratos,
        contratos_origem=_contratos_origem_json(contratos),
        status_options=STATUS_IMPLANTACAO,
        prioridade_options=PRIORIDADE_IMPLANTACAO,
        provisionamento_options=STATUS_PROVISIONAMENTO,
        kanban_options=KANBAN_COLUNAS,
        **contexto,
    )



@implantacao_bp.route("/contrato/<int:contrato_id>/visualizar")
def visualizar_contrato_operacional(contrato_id):
    try:
        contrato = ImplantacaoService.buscar_contrato_operacional(contrato_id)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(url_for("implantacao.novo"))
    if not contrato:
        flash("Contrato não encontrado.", "danger")
        return redirect(url_for("implantacao.novo"))
    return render_template("implantacao/contrato_operacional.html", contrato=contrato)

@implantacao_bp.route("/<int:implantacao_id>")
def visualizar(implantacao_id):
    implantacao = ImplantacaoService.buscar_por_id(implantacao_id)
    if not implantacao:
        flash("Implantação não encontrada.", "danger")
        return redirect(url_for("implantacao.index"))
    return render_template(
        "implantacao/view.html",
        implantacao=implantacao,
        status_options=STATUS_IMPLANTACAO,
        prioridade_options=PRIORIDADE_IMPLANTACAO,
        provisionamento_options=STATUS_PROVISIONAMENTO,
        checklist_status_options=STATUS_CHECKLIST,
        kanban_labels=KANBAN_LABELS,
    )


@implantacao_bp.route("/<int:implantacao_id>/editar", methods=["GET", "POST"])
def editar(implantacao_id):
    implantacao = ImplantacaoService.buscar_por_id(implantacao_id)
    if not implantacao:
        flash("Implantação não encontrada.", "danger")
        return redirect(url_for("implantacao.index"))
    contexto = ImplantacaoService.contexto_form()
    if request.method == "POST":
        dados = _form_data()
        try:
            ImplantacaoService.atualizar(implantacao_id, dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            implantacao = {**implantacao, **dados}
        else:
            flash("Implantação atualizada.", "success")
            return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))

    return render_template(
        "implantacao/form.html",
        modo="editar",
        implantacao=implantacao,
        contratos=[],
        status_options=STATUS_IMPLANTACAO,
        prioridade_options=PRIORIDADE_IMPLANTACAO,
        provisionamento_options=STATUS_PROVISIONAMENTO,
        kanban_options=KANBAN_COLUNAS,
        **contexto,
    )


@implantacao_bp.route("/<int:implantacao_id>/comentarios", methods=["POST"])
def adicionar_comentario(implantacao_id):
    try:
        email = ImplantacaoService.adicionar_comentario(implantacao_id, request.form)
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        if email and email.get("enviado"):
            flash("Comentário registrado e e-mail enviado.", "success")
        elif email:
            flash("Comentário registrado. E-mail não enviado porque o SMTP não está configurado ou não há destinatários.", "warning")
        else:
            flash("Comentário registrado no histórico.", "success")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))

@implantacao_bp.route("/comentarios/<int:historico_id>/editar", methods=["POST"])
def editar_comentario(historico_id):
    try:
        implantacao_id = ImplantacaoService.editar_comentario(historico_id, request.form)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(request.referrer or url_for("implantacao.index"))
    flash("Comentário atualizado.", "success")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))


@implantacao_bp.route("/comentarios/<int:historico_id>/excluir", methods=["POST"])
def excluir_comentario(historico_id):
    try:
        implantacao_id = ImplantacaoService.excluir_comentario(historico_id)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(request.referrer or url_for("implantacao.index"))
    flash("Comentário excluído.", "success")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))


@implantacao_bp.route("/checklist/<int:item_id>", methods=["POST"])
def atualizar_checklist(item_id):
    try:
        implantacao_id = ImplantacaoService.atualizar_item_checklist(item_id, request.form)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(request.referrer or url_for("implantacao.index"))
    flash("Checklist atualizado.", "success")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))


def _licenca_o3web_form_data():
    return {
        "chave_ativacao": request.form.get("chave_ativacao"),
        "id_licenca": request.form.get("id_licenca"),
        "tipo": request.form.get("tipo"),
        "bkp": request.form.get("bkp"),
        "dias": request.form.get("dias"),
        "usuarios": request.form.get("usuarios"),
        "edicao": request.form.get("edicao"),
        "data_ativacao": request.form.get("data_ativacao"),
        "data_expiracao": request.form.get("data_expiracao"),
        "cliente_nome": request.form.get("cliente_nome"),
        "url_principal": request.form.get("url_principal"),
        "url_secundaria": request.form.get("url_secundaria"),
        "comments": request.form.get("comments"),
        "observacao": request.form.get("observacao"),
        "ativo": request.form.get("ativo", "1"),
        "origem": "MANUAL",
    }


def _form_data():
    return {
        "contrato_id": request.form.get("contrato_id"),
        "titulo": request.form.get("titulo"),
        "status": request.form.get("status"),
        "prioridade": request.form.get("prioridade"),
        "responsavel": request.form.get("responsavel"),
        "implantador_nome": request.form.get("implantador_nome"),
        "implantador_email": request.form.get("implantador_email"),
        "emails_adicionais": request.form.get("emails_adicionais"),
        "etapa_kanban": request.form.get("etapa_kanban"),
        "executivo_id": request.form.get("executivo_id"),
        "parceiro_id": request.form.get("parceiro_id"),
        "data_prevista_inicio": request.form.get("data_prevista_inicio"),
        "data_prevista_entrega": request.form.get("data_prevista_entrega"),
        "data_inicio": request.form.get("data_inicio"),
        "data_entrega": request.form.get("data_entrega"),
        "observacoes": request.form.get("observacoes"),
        "provisionamento_status": request.form.get("provisionamento_status"),
        "provisionamento_notas": request.form.get("provisionamento_notas"),
    }


def _contratos_origem_json(contratos):
    origem = []
    for contrato in contratos:
        origem.append({
            "id": contrato.get("id"),
            "numero": contrato.get("numero") or f"Contrato #{contrato.get('id')}",
            "status": contrato.get("status") or "",
            "cliente_nome": contrato.get("cliente_nome") or "",
            "executivo_id": contrato.get("executivo_id"),
            "parceiro_id": contrato.get("parceiro_id"),
            "executivo_nome": contrato.get("executivo_nome") or "",
            "parceiro_nome": contrato.get("parceiro_nome") or "",
            "contrato_descricao": contrato.get("contrato_descricao") or "",
            "proposta_titulo": contrato.get("proposta_titulo") or "",
            "proposta_escopo": contrato.get("proposta_escopo") or "",
            "visualizar_url": url_for("implantacao.visualizar_contrato_operacional", contrato_id=contrato.get("id")),
        })
    return origem
