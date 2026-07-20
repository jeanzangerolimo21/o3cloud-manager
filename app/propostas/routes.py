import mimetypes

from flask import Blueprint
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import session
from flask import url_for

from app.core.storage import StorageService
from app.propostas.service import PropostaService
from app.propostas.service import STATUS_CLICKSIGN
from app.propostas.service import STATUS_PROPOSTA

propostas_bp = Blueprint("propostas", __name__, url_prefix="/propostas")


@propostas_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    status = request.args.get("status")
    ativo = request.args.get("ativo")
    clicksign_status = request.args.get("clicksign_status")
    pagina = request.args.get("page", 1, type=int)
    propostas, total = PropostaService.listar(pesquisa=pesquisa, status=status, ativo=ativo, clicksign_status=clicksign_status, pagina=pagina)
    total_paginas = (total + 49) // 50
    return render_template(
        "propostas/index.html",
        propostas=propostas,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa,
        selected_status=status,
        selected_ativo=ativo or "1",
        selected_clicksign_status=clicksign_status,
        status_options=STATUS_PROPOSTA,
        clicksign_status_options=STATUS_CLICKSIGN,
        placeholder="Buscar por código, solução, cliente, contato ou executivo...",
        page_title="Propostas",
        page_description="Propostas comerciais estruturadas com licenças, servidores e preview para impressão.",
        page_icon="bi-file-earmark-richtext-fill",
        page_button_text="Nova Proposta",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("propostas.novo"),
    )


@propostas_bp.route("/novo", methods=["GET", "POST"])
def novo():
    contexto = PropostaService.listar_contexto_form(_email_usuario_logado())
    if request.method == "POST":
        arquivo_nome = None
        arquivo = request.files.get("arquivo")
        if arquivo and arquivo.filename:
            try:
                arquivo_nome = StorageService.salvar(arquivo, StorageService.PROPOSTAS)["nome"]
            except ValueError as erro:
                flash(str(erro), "danger")
                return render_template("propostas/form.html", modo="novo", proposta=PropostaService.preparar_form_payload(_coletar_dados_form(), contexto["codigo_sugerido"]), status_options=STATUS_PROPOSTA, **contexto)
        dados = _coletar_dados_form()
        dados["arquivo"] = arquivo_nome
        try:
            proposta_id = PropostaService.criar(dados)
        except ValueError as erro:
            if arquivo_nome:
                StorageService.excluir(StorageService.PROPOSTAS, arquivo_nome)
            flash(str(erro), "danger")
            return render_template("propostas/form.html", modo="novo", proposta=PropostaService.preparar_form_payload(dados, contexto["codigo_sugerido"]), status_options=STATUS_PROPOSTA, **contexto)
        flash("Proposta cadastrada com sucesso.", "success")
        return redirect(url_for("propostas.visualizar", proposta_id=proposta_id))
    return render_template("propostas/form.html", modo="novo", proposta=PropostaService.preparar_form_payload(codigo_sugerido=contexto["codigo_sugerido"]), status_options=STATUS_PROPOSTA, **contexto)


@propostas_bp.route("/<int:proposta_id>")
def visualizar(proposta_id):
    proposta = PropostaService.buscar_por_id(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "danger")
        return redirect(url_for("propostas.index"))
    return render_template("propostas/view.html", proposta=proposta, status_options=STATUS_PROPOSTA, clicksign_status_options=STATUS_CLICKSIGN, print_mode=False)


@propostas_bp.route("/<int:proposta_id>/imprimir")
def imprimir(proposta_id):
    proposta = PropostaService.buscar_por_id(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "danger")
        return redirect(url_for("propostas.index"))
    return render_template("propostas/view.html", proposta=proposta, status_options=STATUS_PROPOSTA, clicksign_status_options=STATUS_CLICKSIGN, print_mode=True)


@propostas_bp.route("/<int:proposta_id>/exportar.docx")
def exportar_docx(proposta_id):
    proposta = PropostaService.buscar_por_id(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "danger")
        return redirect(url_for("propostas.index"))
    arquivo = PropostaService.gerar_docx(proposta)
    nome = (proposta.get("codigo_proposta") or f"proposta-{proposta_id}").lower() + ".docx"
    return send_file(arquivo, as_attachment=True, download_name=nome, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@propostas_bp.route("/<int:proposta_id>/editar", methods=["GET", "POST"])
def editar(proposta_id):
    proposta = PropostaService.buscar_por_id(proposta_id)
    contexto = PropostaService.listar_contexto_form(_email_usuario_logado())
    if not proposta:
        flash("Proposta não encontrada.", "danger")
        return redirect(url_for("propostas.index"))
    if request.method == "POST":
        arquivo_atual = proposta.get("arquivo")
        arquivo_nome = arquivo_atual
        arquivo = request.files.get("arquivo")
        remover_arquivo = request.form.get("remover_arquivo") == "1"
        if arquivo and arquivo.filename:
            try:
                arquivo_nome = StorageService.salvar(arquivo, StorageService.PROPOSTAS)["nome"]
                if arquivo_atual:
                    StorageService.excluir(StorageService.PROPOSTAS, arquivo_atual)
            except ValueError as erro:
                flash(str(erro), "danger")
                dados = _coletar_dados_form()
                dados["id"] = proposta_id
                dados["codigo_proposta"] = proposta.get("codigo_proposta")
                dados["arquivo"] = arquivo_atual
                return render_template("propostas/form.html", modo="editar", proposta=PropostaService.preparar_form_payload(dados, proposta.get("codigo_proposta")), status_options=STATUS_PROPOSTA, **contexto)
        elif remover_arquivo and arquivo_atual:
            StorageService.excluir(StorageService.PROPOSTAS, arquivo_atual)
            arquivo_nome = None
        dados = _coletar_dados_form()
        dados["arquivo"] = arquivo_nome
        try:
            PropostaService.atualizar(proposta_id, dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            dados["id"] = proposta_id
            dados["codigo_proposta"] = proposta.get("codigo_proposta")
            dados["arquivo"] = arquivo_nome
            return render_template("propostas/form.html", modo="editar", proposta=PropostaService.preparar_form_payload(dados, proposta.get("codigo_proposta")), status_options=STATUS_PROPOSTA, **contexto)
        flash("Proposta atualizada com sucesso.", "success")
        return redirect(url_for("propostas.visualizar", proposta_id=proposta_id))
    return render_template("propostas/form.html", modo="editar", proposta=PropostaService.preparar_form_payload(proposta, proposta.get("codigo_proposta")), status_options=STATUS_PROPOSTA, **contexto)


@propostas_bp.route("/<int:proposta_id>/contrato")
def visualizar_contrato(proposta_id):
    caminho, nome = PropostaService.caminho_contrato_clicksign(proposta_id)
    if not caminho:
        flash("Gere o documento do contrato antes de visualizar.", "warning")
        return redirect(url_for("propostas.visualizar", proposta_id=proposta_id))
    mimetype = mimetypes.guess_type(nome)[0] or "application/octet-stream"
    return send_file(caminho, as_attachment=False, download_name=nome, mimetype=mimetype)


@propostas_bp.route("/clicksign/sincronizar")
def sincronizar_clicksign_todas():
    resultados = PropostaService.sincronizar_clicksign_pendentes(_email_usuario_logado())
    total = len(resultados)
    erros = [item for item in resultados if item.get("status") == "ERRO"]
    if not total:
        flash("Nenhuma proposta pendente para sincronizar com a ClickSign.", "info")
    elif erros:
        flash(f"ClickSign sincronizada com {total - len(erros)} sucesso(s) e {len(erros)} erro(s).", "warning")
    else:
        flash(f"ClickSign sincronizada com sucesso em {total} proposta(s).", "success")
    return redirect(url_for("propostas.index"))


@propostas_bp.route("/<int:proposta_id>/clicksign/<acao>")
def atualizar_clicksign(proposta_id, acao):
    try:
        PropostaService.atualizar_status_clicksign(proposta_id, acao, _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Fluxo de ClickSign atualizado com sucesso.", "success")
    return redirect(url_for("propostas.visualizar", proposta_id=proposta_id))


@propostas_bp.route("/<int:proposta_id>/excluir")
def excluir(proposta_id):
    proposta = PropostaService.buscar_por_id(proposta_id)
    if not proposta:
        flash("Proposta não encontrada.", "danger")
    else:
        PropostaService.excluir(proposta_id)
        flash("Proposta removida com sucesso.", "success")
    return redirect(url_for("propostas.index"))


def _coletar_dados_form():
    return {
        "oportunidade_id": request.form.get("oportunidade_id"),
        "cliente_id": request.form.get("cliente_id"),
        "contato_id": request.form.get("contato_id"),
        "parceiro_id": request.form.get("parceiro_id"),
        "executivo_responsavel_id": request.form.get("executivo_responsavel_id"),
        "codigo_proposta": request.form.get("codigo_proposta"),
        "titulo": request.form.get("titulo"),
        "status": request.form.get("status"),
        "validade": request.form.get("validade"),
        "setup_dias": request.form.get("setup_dias"),
        "mensalidade_dias": request.form.get("mensalidade_dias"),
        "prazo_contratual_meses": request.form.get("prazo_contratual_meses"),
        "detalhes_negociacao": request.form.get("detalhes_negociacao"),
        "condicoes_comerciais": request.form.get("condicoes_comerciais"),
        "observacoes": request.form.get("observacoes"),
        "cliente_nome": request.form.get("cliente_nome"),
        "contato_nome": request.form.get("contato_nome"),
        "contato_email": request.form.get("contato_email"),
        "contato_telefone": request.form.get("contato_telefone"),
        "executivo_nome": request.form.get("executivo_nome"),
        "executivo_email": request.form.get("executivo_email"),
        "executivo_telefone": request.form.get("executivo_telefone"),
        "parametrizacao_sistema": request.form.get("parametrizacao_sistema"),
        "setup_ambiente_cloud": request.form.get("setup_ambiente_cloud"),
        "total_mensal": request.form.get("total_mensal"),
        "total_instalacao": request.form.get("total_instalacao"),
        "valor_total": request.form.get("valor_total"),
        "licencas_snapshot": request.form.get("licencas_snapshot"),
        "servidores_snapshot": request.form.get("servidores_snapshot"),
        "arquivo": request.form.get("arquivo_atual"),
        "ativo": request.form.get("ativo", "0"),
    }


def _email_usuario_logado():
    for chave in ("user_email", "email", "usuario_email", "login_email"):
        valor = session.get(chave)
        if valor:
            return valor
    return None
