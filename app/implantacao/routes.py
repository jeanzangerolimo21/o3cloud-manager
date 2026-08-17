from flask import Blueprint
from flask import current_app
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from urllib.parse import urljoin

from app.core.auditoria import registrar_evento
from app.implantacao.service import ImplantacaoService
from app.repositories.contrato_item_repository import ContratoItemRepository
from app.implantacao.service import KANBAN_COLUNAS
from app.implantacao.service import KANBAN_LABELS
from app.implantacao.service import CHECKLIST_MODELOS
from app.implantacao.service import PRIORIDADE_IMPLANTACAO
from app.implantacao.service import STATUS_CHECKLIST
from app.implantacao.service import STATUS_IMPLANTACAO
from app.implantacao.service import STATUS_PROVISIONAMENTO
from app.clientes.service import ClienteService
from app.implantacao.o3web_licencas_service import O3WebLicencaService
from app.implantacao.o3web_licencas_service import TIPOS_LICENCA_O3WEB
from app.implantacao.faixas_rede_service import FaixaRedeService
from app.implantacao.integracoes_service import IntegracaoConfigService
from app.implantacao.integracoes_service import GRUPOS_INTEGRACAO
from app.implantacao.integracoes_service import TIPOS_INTEGRACAO
from app.implantacao.cofre_senhas_service import CATEGORIAS_COFRE_SENHAS
from app.implantacao.cofre_pastas_service import CofrePastaService
from app.implantacao.cofre_pastas_service import TIPOS_COFRE_PASTA
from app.implantacao.cofre_senhas_service import CofreSenhaService


implantacao_bp = Blueprint("implantacao", __name__, url_prefix="/implantacao")


@implantacao_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    status = request.args.get("status")
    responsavel = request.args.get("responsavel")
    prazo = request.args.get("prazo")
    ativo = request.args.get("ativo", "1")
    pagina = request.args.get("page", 1, type=int)
    implantacoes, total = ImplantacaoService.listar(
        pesquisa=pesquisa,
        status=status,
        responsavel=responsavel,
        prazo=prazo,
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
        selected_prazo=prazo,
        status_options=STATUS_IMPLANTACAO,
        prazo_options={
            "atrasadas": "Atrasadas",
            "vence_7": "Vencem em 7 dias",
            "vence_30": "Vencem em 30 dias",
            "sem_prazo": "Sem prazo",
        },
        dashboard=ImplantacaoService.dashboard(
            pesquisa=pesquisa,
            status=status,
            responsavel=responsavel,
            prazo=prazo,
            ativo=ativo,
        ),
        page_title="Implantação",
        page_description="Workflow técnico pós-contrato encaminhado para projeto.",
        page_icon="bi-hdd-network",
        page_button_text="Nova Implantação",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("implantacao.novo"),
    )



@implantacao_bp.route("/faixas-rede")
def faixas_rede():
    pesquisa = request.args.get("q")
    ativo = request.args.get("ativo", "1")
    pagina = request.args.get("page", 1, type=int)
    rede_base = request.args.get("rede_base")
    quantidade_servidores = request.args.get("quantidade_servidores")
    sugestao = None
    if rede_base or quantidade_servidores:
        try:
            sugestao = FaixaRedeService.calcular_proxima(rede_base, quantidade_servidores)
        except ValueError as erro:
            flash(str(erro), "danger")
    faixas, total = FaixaRedeService.listar(
        pesquisa=pesquisa,
        ativo=ativo,
        pagina=pagina,
    )
    total_paginas = (total + 49) // 50
    return render_template(
        "implantacao/faixas_rede/index.html",
        faixas=faixas,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa,
        selected_ativo=ativo,
        rede_base=rede_base,
        quantidade_servidores=quantidade_servidores,
        sugestao=sugestao,
        dashboard=FaixaRedeService.dashboard(),
        page_title="Faixas de Rede",
        page_description="Gerenciamento das faixas reservadas para novos ambientes de clientes.",
        page_icon="bi-diagram-3-fill",
        page_button_text="Nova Faixa",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("implantacao.nova_faixa_rede"),
    )


@implantacao_bp.route("/faixas-rede/novo", methods=["GET", "POST"])
def nova_faixa_rede():
    clientes = ClienteService.listar_para_importacao()
    faixa = {
        "rede": request.args.get("rede"),
        "quantidade_servidores": request.args.get("quantidade_servidores"),
        "fw_wan": request.args.get("fw_wan"),
        "fw_lan": request.args.get("fw_lan"),
        "pve": request.args.get("pve"),
        "ativo": 1,
    }
    if request.method == "POST":
        try:
            faixa_id = FaixaRedeService.criar(_faixa_rede_form_data())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("implantacao/faixas_rede/form.html", faixa=request.form, clientes=clientes, modo="novo")
        flash("Faixa de rede cadastrada.", "success")
        return redirect(url_for("implantacao.editar_faixa_rede", faixa_id=faixa_id))
    return render_template("implantacao/faixas_rede/form.html", faixa=faixa, clientes=clientes, modo="novo")


@implantacao_bp.route("/faixas-rede/<int:faixa_id>/editar", methods=["GET", "POST"])
def editar_faixa_rede(faixa_id):
    faixa = FaixaRedeService.buscar_por_id(faixa_id)
    if not faixa:
        flash("Faixa de rede não encontrada.", "danger")
        return redirect(url_for("implantacao.faixas_rede"))
    clientes = ClienteService.listar_para_importacao()
    if request.method == "POST":
        try:
            FaixaRedeService.atualizar(faixa_id, _faixa_rede_form_data())
        except ValueError as erro:
            flash(str(erro), "danger")
            faixa = {**faixa, **request.form}
        else:
            flash("Faixa de rede atualizada.", "success")
            return redirect(url_for("implantacao.faixas_rede"))
    return render_template("implantacao/faixas_rede/form.html", faixa=faixa, clientes=clientes, modo="editar")


@implantacao_bp.route("/faixas-rede/<int:faixa_id>/excluir", methods=["POST"])
def excluir_faixa_rede(faixa_id):
    try:
        FaixaRedeService.excluir(faixa_id)
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Faixa de rede inativada.", "success")
    return redirect(url_for("implantacao.faixas_rede"))


@implantacao_bp.route("/cofre-senhas")
def cofre_senhas():
    pesquisa = request.args.get("q")
    categoria = request.args.get("categoria")
    parceiro_id = request.args.get("parceiro_id", type=int)
    pasta_id = request.args.get("pasta_id", type=int)
    ativo = request.args.get("ativo", "1")
    pagina = request.args.get("page", 1, type=int)

    usuario_logado = _email_usuario_logado()
    selected_pasta = CofrePastaService.buscar_por_id(pasta_id) if pasta_id else None
    if selected_pasta and not parceiro_id:
        parceiro_id = selected_pasta.get("parceiro_id")
    if selected_pasta and parceiro_id and int(selected_pasta.get("parceiro_id") or 0) != int(parceiro_id):
        selected_pasta = None
        pasta_id = None
    if selected_pasta and selected_pasta.get("tipo") == "usuario" and not _usuario_pode_acessar_pasta(selected_pasta, usuario_logado):
        flash("Você não tem acesso a esta pasta particular do cofre.", "danger")
        selected_pasta = None
        pasta_id = None

    selected_parceiro = CofrePastaService.buscar_parceiro_navegacao(parceiro_id)
    if parceiro_id and not selected_parceiro:
        parceiro_id = None
        pasta_id = None
        selected_pasta = None

    senhas = []
    total = 0
    if selected_pasta or pesquisa:
        senhas, total = CofreSenhaService.listar(
            pesquisa=pesquisa,
            categoria=categoria,
            ativo=ativo,
            pasta_id=pasta_id,
            apenas_clientes=bool(pesquisa and not selected_pasta),
            pagina=pagina,
        )
    total_paginas = (total + 49) // 50
    return render_template(
        "implantacao/cofre_senhas/index.html",
        senhas=senhas,
        total=total,
        pagina=pagina,
        total_paginas=total_paginas,
        pesquisa=pesquisa,
        selected_categoria=categoria,
        selected_parceiro_id=parceiro_id,
        selected_parceiro=selected_parceiro,
        selected_pasta_id=pasta_id,
        selected_pasta=selected_pasta,
        selected_ativo=ativo,
        parceiros_navegacao=CofrePastaService.listar_parceiros_navegacao(),
        pastas_usuario=CofrePastaService.listar_pastas_usuario(usuario_logado),
        pastas_compartilhadas=CofrePastaService.listar_pastas_compartilhadas_com_usuario(usuario_logado),
        usuario_email_logado=usuario_logado,
        pastas_cliente=CofrePastaService.listar_pastas_cliente_por_parceiro(parceiro_id),
        pastas=CofrePastaService.listar_ativas(),
        pasta_tipo_options=TIPOS_COFRE_PASTA,
        categoria_options=CATEGORIAS_COFRE_SENHAS,
        dashboard=CofreSenhaService.dashboard(),
        page_title="Cofre de Senhas",
        page_description="Credenciais operacionais vinculadas a clientes e faixas de rede.",
        page_icon="bi-shield-lock-fill",
        page_button_text="Nova Credencial",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("implantacao.nova_senha_cofre"),
    )


@implantacao_bp.route("/cofre-senhas/pastas/novo", methods=["GET", "POST"])
def nova_pasta_cofre():
    contexto = CofrePastaService.contexto_form()
    if request.method == "POST":
        try:
            CofrePastaService.criar(_cofre_pasta_form_data(), _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("implantacao/cofre_senhas/pasta_form.html", pasta=request.form, modo="novo", owner_email=_email_usuario_logado(), **contexto)
        flash("Pasta criada no cofre.", "success")
        return redirect(url_for("implantacao.cofre_senhas"))
    pasta = {
        "tipo": request.args.get("tipo") or "usuario",
        "parceiro_id": request.args.get("parceiro_id"),
        "ativo": 1,
    }
    return render_template("implantacao/cofre_senhas/pasta_form.html", pasta=pasta, modo="novo", owner_email=_email_usuario_logado(), **contexto)


@implantacao_bp.route("/cofre-senhas/pastas/<int:pasta_id>/editar", methods=["GET", "POST"])
def editar_pasta_cofre(pasta_id):
    pasta = CofrePastaService.buscar_por_id(pasta_id)
    if not pasta:
        flash("Pasta não encontrada.", "danger")
        return redirect(url_for("implantacao.cofre_senhas"))
    contexto = CofrePastaService.contexto_form()
    if request.method == "POST":
        try:
            CofrePastaService.atualizar(pasta_id, _cofre_pasta_form_data(), _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            pasta = {**pasta, **request.form}
        else:
            flash("Pasta atualizada.", "success")
            return redirect(url_for("implantacao.cofre_senhas", pasta_id=pasta_id))
    return render_template("implantacao/cofre_senhas/pasta_form.html", pasta=pasta, modo="editar", owner_email=pasta.get("owner_email") or _email_usuario_logado(), **contexto)


@implantacao_bp.route("/cofre-senhas/pastas/<int:pasta_id>/excluir", methods=["POST"])
def excluir_pasta_cofre(pasta_id):
    try:
        CofrePastaService.excluir(pasta_id)
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Pasta inativada.", "success")
    return redirect(url_for("implantacao.cofre_senhas"))


@implantacao_bp.route("/cofre-senhas/novo", methods=["GET", "POST"])
def nova_senha_cofre():
    contexto = CofreSenhaService.contexto_form(_email_usuario_logado())
    if request.method == "POST":
        try:
            senha_id = CofreSenhaService.criar(_cofre_senha_form_data(), _email_usuario_logado(), request.remote_addr)
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("implantacao/cofre_senhas/form.html", senha=request.form, modo="novo", **contexto)
        flash("Credencial cadastrada no cofre.", "success")
        return redirect(url_for("implantacao.editar_senha_cofre", senha_id=senha_id))
    senha = {"ativo": 1, "pasta_id": request.args.get("pasta_id")}
    if senha.get("pasta_id"):
        pasta = CofrePastaService.buscar_por_id(senha.get("pasta_id"))
        if pasta and pasta.get("cliente_id"):
            senha["cliente_id"] = pasta.get("cliente_id")
    return render_template("implantacao/cofre_senhas/form.html", senha=senha, modo="novo", **contexto)


@implantacao_bp.route("/cofre-senhas/<int:senha_id>/editar", methods=["GET", "POST"])
def editar_senha_cofre(senha_id):
    senha = CofreSenhaService.buscar_por_id(senha_id, _email_usuario_logado())
    if not senha:
        flash("Credencial não encontrada.", "danger")
        return redirect(url_for("implantacao.cofre_senhas"))
    contexto = CofreSenhaService.contexto_form(_email_usuario_logado())
    if request.method == "POST":
        try:
            CofreSenhaService.atualizar(senha_id, _cofre_senha_form_data(), _email_usuario_logado(), request.remote_addr)
        except ValueError as erro:
            flash(str(erro), "danger")
            senha = {**senha, **request.form}
        else:
            flash("Credencial atualizada.", "success")
            return redirect(url_for("implantacao.cofre_senhas"))
    return render_template("implantacao/cofre_senhas/form.html", senha=senha, modo="editar", **contexto)


@implantacao_bp.route("/cofre-senhas/<int:senha_id>/revelar", methods=["POST"])
def revelar_senha_cofre(senha_id):
    try:
        senha = CofreSenhaService.revelar_senha(senha_id, _email_usuario_logado(), request.remote_addr)
    except ValueError as erro:
        return jsonify({"ok": False, "erro": str(erro)}), 400
    return jsonify({"ok": True, "senha": senha})


def _url_publica(caminho):
    base_url = (current_app.config.get("PUBLIC_BASE_URL") or "").strip().rstrip("/")
    if base_url:
        return urljoin(f"{base_url}/", caminho.lstrip("/"))
    return urljoin(request.url_root, caminho.lstrip("/"))


@implantacao_bp.route("/cofre-senhas/<int:senha_id>/compartilhar", methods=["POST"])
def compartilhar_senha_cofre(senha_id):
    try:
        token = CofreSenhaService.criar_compartilhamento(
            senha_id, _email_usuario_logado(), request.remote_addr
        )
    except ValueError as erro:
        return jsonify({"ok": False, "erro": str(erro)}), 400
    caminho = url_for("implantacao.acessar_compartilhamento_senha", token=token)
    link = _url_publica(caminho)
    return jsonify({"ok": True, "link": link})


@implantacao_bp.route("/compartilhar-senha/<token>", methods=["GET", "POST"])
def acessar_compartilhamento_senha(token):
    compartilhamento = None
    status = 200
    if request.method == "POST":
        compartilhamento = CofreSenhaService.consumir_compartilhamento(token, request.remote_addr)
        if not compartilhamento:
            status = 410
    response = current_app.make_response(render_template(
        "implantacao/cofre_senhas/compartilhamento.html",
        titulo=compartilhamento.get("titulo") if compartilhamento else None,
        senha=compartilhamento.get("senha") if compartilhamento else None,
        token=token,
        indisponivel=status == 410,
    ))
    response.status_code = status
    response.headers["Cache-Control"] = "no-store, no-cache, max-age=0, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response


@implantacao_bp.route("/cofre-senhas/<int:senha_id>/excluir", methods=["POST"])
def excluir_senha_cofre(senha_id):
    try:
        CofreSenhaService.excluir(senha_id, _email_usuario_logado(), request.remote_addr)
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Credencial inativada.", "success")
    return redirect(url_for("implantacao.cofre_senhas"))


@implantacao_bp.route("/licencas-o3web")
def licencas_o3web():
    pesquisa = request.args.get("q")
    tipo = request.args.get("tipo")
    validade = request.args.get("validade")
    ativo = request.args.get("ativo", "1")
    pagina = request.args.get("page", 1, type=int)
    licencas, total = O3WebLicencaService.listar(
        pesquisa=pesquisa,
        tipo=tipo,
        ativo=ativo,
        validade=validade,
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
        selected_validade=validade,
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
    clientes = ClienteService.listar_para_importacao()
    if request.method == "POST":
        try:
            licenca_id = O3WebLicencaService.criar(_licenca_o3web_form_data())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("implantacao/licencas_o3web/form.html", licenca=request.form, tipo_options=TIPOS_LICENCA_O3WEB, clientes=clientes, modo="novo")
        flash("Licença O3Web cadastrada.", "success")
        return redirect(url_for("implantacao.editar_licenca_o3web", licenca_id=licenca_id))
    return render_template("implantacao/licencas_o3web/form.html", licenca={}, tipo_options=TIPOS_LICENCA_O3WEB, clientes=clientes, modo="novo")


@implantacao_bp.route("/licencas-o3web/<int:licenca_id>/editar", methods=["GET", "POST"])
def editar_licenca_o3web(licenca_id):
    licenca = O3WebLicencaService.buscar_por_id(licenca_id)
    if not licenca:
        flash("Licença O3Web não encontrada.", "danger")
        return redirect(url_for("implantacao.licencas_o3web"))
    clientes = ClienteService.listar_para_importacao()
    if request.method == "POST":
        try:
            O3WebLicencaService.atualizar(licenca_id, _licenca_o3web_form_data())
        except ValueError as erro:
            flash(str(erro), "danger")
            licenca = {**licenca, **request.form}
        else:
            flash("Licença O3Web atualizada.", "success")
            return redirect(url_for("implantacao.licencas_o3web"))
    return render_template("implantacao/licencas_o3web/form.html", licenca=licenca, tipo_options=TIPOS_LICENCA_O3WEB, clientes=clientes, modo="editar")


@implantacao_bp.route("/licencas-o3web/<int:licenca_id>/excluir", methods=["POST"])
def excluir_licenca_o3web(licenca_id):
    try:
        O3WebLicencaService.excluir(licenca_id)
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Licença O3Web inativada.", "success")
    return redirect(url_for("implantacao.licencas_o3web"))


@implantacao_bp.route("/integracoes")
def integracoes_config():
    return redirect(url_for("implantacao.integracoes_tecnicas"))


@implantacao_bp.route("/integracoes/negocio")
def integracoes_negocio():
    return _render_integracoes_config("negocio")


@implantacao_bp.route("/integracoes/tecnicas")
def integracoes_tecnicas():
    return _render_integracoes_config("tecnicas")


def _render_integracoes_config(grupo):
    tipo = request.args.get("tipo")
    ativo = request.args.get("ativo", "1")
    contexto = IntegracaoConfigService.contexto_grupo(grupo)
    tipo_options = IntegracaoConfigService.tipo_options(contexto["grupo"])
    if tipo and tipo not in tipo_options:
        tipo = None
    return render_template(
        "implantacao/integracoes/index.html",
        integracoes=IntegracaoConfigService.listar(tipo=tipo, ativo=ativo, grupo=contexto["grupo"]),
        integracoes_ambiente=IntegracaoConfigService.integracoes_ambiente(contexto["grupo"]),
        validacoes_recentes=IntegracaoConfigService.validacoes_recentes(contexto["grupo"]),
        dashboard=IntegracaoConfigService.dashboard(contexto["grupo"]),
        tipo_options=tipo_options,
        selected_tipo=tipo,
        selected_ativo=ativo,
        grupo_integracao=contexto["grupo"],
        grupos_integracao=GRUPOS_INTEGRACAO,
        page_title=contexto["titulo"],
        page_description=contexto["descricao"],
        page_icon="bi-plug-fill",
        page_button_text="Nova Integração",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("implantacao.nova_integracao_config", grupo=contexto["grupo"]),
    )


@implantacao_bp.route("/integracoes/ambiente/segredo", methods=["POST"])
def revelar_integracao_ambiente_segredo():
    try:
        valor = IntegracaoConfigService.revelar_segredo_ambiente(request.form.get("chave"))
        registrar_evento("INTEGRACAO_SEGREDO_AMBIENTE_REVELADO", "integracoes_ambiente", None, {"chave": request.form.get("chave")})
    except ValueError as erro:
        response = jsonify({"erro": str(erro)})
        response.status_code = 400
    else:
        response = jsonify({"valor": valor})
    response.headers["Cache-Control"] = "no-store"
    return response


@implantacao_bp.route("/integracoes/<int:integracao_id>/segredo", methods=["POST"])
def revelar_integracao_config_segredo(integracao_id):
    try:
        valor = IntegracaoConfigService.revelar_segredo_config(integracao_id)
        registrar_evento("INTEGRACAO_SEGREDO_REVELADO", "integracoes_config", integracao_id)
    except ValueError as erro:
        response = jsonify({"erro": str(erro)})
        response.status_code = 400
    else:
        response = jsonify({"valor": valor})
    response.headers["Cache-Control"] = "no-store"
    return response


@implantacao_bp.route("/integracoes/novo", methods=["GET", "POST"])
def nova_integracao_config():
    grupo = request.args.get("grupo") or "tecnicas"
    tipo_options = IntegracaoConfigService.tipo_options(grupo)
    tipo_padrao = request.args.get("tipo") if request.args.get("tipo") in tipo_options else None
    if request.method == "POST":
        try:
            integracao_id = IntegracaoConfigService.criar(request.form, _email_usuario_logado())
            registrar_evento("INTEGRACAO_CRIADA", "integracoes_config", integracao_id, {"tipo": request.form.get("tipo"), "nome": request.form.get("nome")})
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("implantacao/integracoes/form.html", integracao=request.form, tipo_options=tipo_options, grupo_integracao=grupo, modo="novo", historico_validacoes=[])
        flash("Integração cadastrada.", "success")
        return redirect(url_for("implantacao.editar_integracao_config", integracao_id=integracao_id))
    return render_template("implantacao/integracoes/form.html", integracao={"tipo": tipo_padrao, "ativo": 1, "verify_ssl": 1, "timeout_seconds": 30}, tipo_options=tipo_options, grupo_integracao=grupo, modo="novo", historico_validacoes=[])


@implantacao_bp.route("/integracoes/<int:integracao_id>/editar", methods=["GET", "POST"])
def editar_integracao_config(integracao_id):
    integracao = IntegracaoConfigService.buscar_por_id(integracao_id)
    if not integracao:
        flash("Integração não encontrada.", "danger")
        return redirect(url_for("implantacao.integracoes_tecnicas"))
    if request.method == "POST":
        try:
            IntegracaoConfigService.atualizar(integracao_id, request.form, _email_usuario_logado())
            registrar_evento("INTEGRACAO_ATUALIZADA", "integracoes_config", integracao_id, {"tipo": request.form.get("tipo"), "nome": request.form.get("nome")})
        except ValueError as erro:
            flash(str(erro), "danger")
            integracao = {**integracao, **request.form}
            historico_validacoes = IntegracaoConfigService.historico_validacoes(integracao_id)
        else:
            flash("Integração atualizada.", "success")
            grupo = IntegracaoConfigService.grupo_por_tipo(request.form.get("tipo") or integracao.get("tipo"))
            return redirect(url_for(f"implantacao.integracoes_{grupo}"))
    grupo = IntegracaoConfigService.grupo_por_tipo(integracao.get("tipo"))
    historico_validacoes = IntegracaoConfigService.historico_validacoes(integracao_id)
    return render_template("implantacao/integracoes/form.html", integracao=integracao, tipo_options=IntegracaoConfigService.tipo_options(grupo), grupo_integracao=grupo, modo="editar", historico_validacoes=historico_validacoes)


@implantacao_bp.route("/integracoes/<int:integracao_id>/testar", methods=["POST"])
def testar_integracao_config(integracao_id):
    try:
        resultado = IntegracaoConfigService.testar_configuracao(integracao_id, _email_usuario_logado())
        registrar_evento("INTEGRACAO_TESTADA", "integracoes_config", integracao_id, {"status": resultado.get("status"), "mensagem": resultado.get("mensagem")})
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        categoria = "success" if resultado.get("status") == "OK" else "warning"
        flash(resultado.get("mensagem"), categoria)
    return redirect(request.referrer or url_for("implantacao.integracoes_tecnicas"))


@implantacao_bp.route("/integracoes/<int:integracao_id>/excluir", methods=["POST"])
def excluir_integracao_config(integracao_id):
    try:
        IntegracaoConfigService.inativar(integracao_id, _email_usuario_logado())
        registrar_evento("INTEGRACAO_INATIVADA", "integracoes_config", integracao_id)
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Integração inativada.", "success")
    return redirect(request.referrer or url_for("implantacao.integracoes_tecnicas"))


@implantacao_bp.route("/kanban")
def kanban():
    return render_template(
        "implantacao/kanban.html",
        colunas=ImplantacaoService.kanban(),
        kanban_labels=ImplantacaoService.kanban_labels(),
        page_title="Kanban de Implantação",
        page_description="Organização operacional das etapas de projeto.",
        page_icon="bi-kanban-fill",
        page_button_text="Nova Implantação",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("implantacao.novo"),
    )


@implantacao_bp.route("/kanban/colunas")
def kanban_colunas():
    return render_template(
        "implantacao/kanban_colunas.html",
        colunas=ImplantacaoService.kanban_colunas(ativo=None),
        page_title="Colunas do Kanban",
        page_description="Configuração administrativa das etapas de implantação.",
        page_icon="bi-columns-gap",
        page_button_text="Voltar ao Kanban",
        page_button_icon="bi-kanban-fill",
        page_button_url=url_for("implantacao.kanban"),
    )


@implantacao_bp.route("/kanban/colunas/novo", methods=["POST"])
def criar_coluna_kanban():
    try:
        ImplantacaoService.criar_coluna_kanban(request.form)
        registrar_evento("KANBAN_COLUNA_CRIADA", "implantacao_kanban_colunas", None, {"nome": request.form.get("nome"), "status": request.form.get("status")})
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Coluna do Kanban criada.", "success")
    return redirect(url_for("implantacao.kanban_colunas"))


@implantacao_bp.route("/kanban/colunas/<int:coluna_id>/editar", methods=["POST"])
def editar_coluna_kanban(coluna_id):
    try:
        ImplantacaoService.atualizar_coluna_kanban(coluna_id, request.form)
        registrar_evento("KANBAN_COLUNA_ATUALIZADA", "implantacao_kanban_colunas", coluna_id, {"nome": request.form.get("nome"), "status": request.form.get("status")})
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Coluna do Kanban atualizada.", "success")
    return redirect(url_for("implantacao.kanban_colunas"))


@implantacao_bp.route("/kanban/mover", methods=["POST"])
def mover_kanban():
    dados = request.get_json(silent=True) or request.form
    try:
        resultado = ImplantacaoService.mover_kanban(
            int(dados.get("implantacao_id")),
            dados.get("etapa_kanban"),
        )
        registrar_evento("IMPLANTACAO_KANBAN_MOVIMENTADO", "implantacoes", dados.get("implantacao_id"), {"etapa_kanban": dados.get("etapa_kanban")})
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
            registrar_evento("IMPLANTACAO_CRIADA", "implantacoes", implantacao_id, {"contrato_id": dados.get("contrato_id"), "status": dados.get("status")})
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
                kanban_options=ImplantacaoService.kanban_options(),
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
        kanban_options=ImplantacaoService.kanban_options(),
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
    itens = ContratoItemRepository.listar_por_contrato(contrato_id)
    return render_template("implantacao/contrato_operacional.html", contrato=contrato, itens=itens)

@implantacao_bp.route("/<int:implantacao_id>")
def visualizar(implantacao_id):
    implantacao = ImplantacaoService.buscar_por_id(implantacao_id)
    if not implantacao:
        flash("Implantação não encontrada.", "danger")
        return redirect(url_for("implantacao.index"))
    return render_template(
        "implantacao/view.html",
        implantacao=implantacao,
        rastreabilidade=ImplantacaoService.rastreabilidade_por_implantacao(implantacao_id),
        diagnostico_pre_beta=ImplantacaoService.diagnostico_pre_beta(implantacao),
        status_options=STATUS_IMPLANTACAO,
        prioridade_options=PRIORIDADE_IMPLANTACAO,
        provisionamento_options=STATUS_PROVISIONAMENTO,
        checklist_status_options=STATUS_CHECKLIST,
        checklist_modelos=CHECKLIST_MODELOS,
        kanban_labels=ImplantacaoService.kanban_labels(),
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
            registrar_evento("IMPLANTACAO_ATUALIZADA", "implantacoes", implantacao_id, {"status": dados.get("status"), "provisionamento_status": dados.get("provisionamento_status")})
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
        kanban_options=ImplantacaoService.kanban_options(),
        **contexto,
    )


@implantacao_bp.route("/<int:implantacao_id>/comentarios", methods=["POST"])
def adicionar_comentario(implantacao_id):
    try:
        email = ImplantacaoService.adicionar_comentario(implantacao_id, request.form, request.files.getlist("anexos"))
        registrar_evento("IMPLANTACAO_COMENTARIO_ADICIONADO", "implantacoes", implantacao_id, {"enviar_email": request.form.get("enviar_email"), "anexos": len(request.files.getlist("anexos"))})
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
    registrar_evento("IMPLANTACAO_COMENTARIO_ATUALIZADO", "implantacao_historico", historico_id, {"implantacao_id": implantacao_id})
    flash("Comentário atualizado.", "success")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))


@implantacao_bp.route("/comentarios/<int:historico_id>/excluir", methods=["POST"])
def excluir_comentario(historico_id):
    try:
        implantacao_id = ImplantacaoService.excluir_comentario(historico_id)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(request.referrer or url_for("implantacao.index"))
    registrar_evento("IMPLANTACAO_COMENTARIO_EXCLUIDO", "implantacao_historico", historico_id, {"implantacao_id": implantacao_id})
    flash("Comentário excluído.", "success")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))



@implantacao_bp.route("/<int:implantacao_id>/checklist/novo", methods=["POST"])
def adicionar_item_checklist(implantacao_id):
    try:
        ImplantacaoService.adicionar_item_checklist(implantacao_id, request.form)
        registrar_evento("IMPLANTACAO_CHECKLIST_ITEM_ADICIONADO", "implantacoes", implantacao_id, {"titulo": request.form.get("titulo")})
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Item adicionado ao checklist.", "success")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))


@implantacao_bp.route("/<int:implantacao_id>/checklist/modelo", methods=["POST"])
def aplicar_modelo_checklist(implantacao_id):
    try:
        criados = ImplantacaoService.aplicar_modelo_checklist(implantacao_id, request.form.get("modelo"))
        registrar_evento("IMPLANTACAO_CHECKLIST_MODELO_APLICADO", "implantacoes", implantacao_id, {"modelo": request.form.get("modelo"), "criados": criados})
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        if criados:
            flash(f"Modelo aplicado com {criados} novo(s) item(ns).", "success")
        else:
            flash("Modelo já estava aplicado ao checklist.", "info")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))


@implantacao_bp.route("/checklist/<int:item_id>/excluir", methods=["POST"])
def excluir_item_checklist(item_id):
    try:
        implantacao_id = ImplantacaoService.excluir_item_checklist(item_id)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(request.referrer or url_for("implantacao.index"))
    registrar_evento("IMPLANTACAO_CHECKLIST_ITEM_EXCLUIDO", "implantacao_checklist", item_id, {"implantacao_id": implantacao_id})
    flash("Item removido do checklist.", "success")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))

@implantacao_bp.route("/checklist/<int:item_id>", methods=["POST"])
def atualizar_checklist(item_id):
    try:
        implantacao_id = ImplantacaoService.atualizar_item_checklist(item_id, request.form)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(request.referrer or url_for("implantacao.index"))
    registrar_evento("IMPLANTACAO_CHECKLIST_ATUALIZADO", "implantacao_checklist", item_id, {"implantacao_id": implantacao_id, "status": request.form.get("status")})
    flash("Checklist atualizado.", "success")
    return redirect(url_for("implantacao.visualizar", implantacao_id=implantacao_id))


def _usuario_pode_acessar_pasta(pasta, usuario_email):
    if not pasta or pasta.get("tipo") != "usuario":
        return True
    usuario_email = (usuario_email or "sistema").strip().lower()
    if usuario_email == "sistema":
        return True
    if (pasta.get("owner_email") or "").strip().lower() == usuario_email:
        return True
    if not pasta.get("compartilhada"):
        return False
    compartilhados = {
        item.strip().lower()
        for item in str(pasta.get("compartilhada_com") or "").replace(";", ",").split(",")
        if item.strip()
    }
    return usuario_email in compartilhados


def _cofre_pasta_form_data():
    return {
        "nome": request.form.get("nome"),
        "tipo": request.form.get("tipo"),
        "parceiro_id": request.form.get("parceiro_id"),
        "cliente_id": request.form.get("cliente_id"),
        "owner_email": request.form.get("owner_email") or _email_usuario_logado(),
        "compartilhada": request.form.get("compartilhada", "0"),
        "compartilhada_com": ",".join(request.form.getlist("compartilhada_com_multi")) or request.form.get("compartilhada_com"),
        "observacoes": request.form.get("observacoes"),
        "ativo": request.form.get("ativo", "1"),
    }


def _cofre_senha_form_data():
    return {
        "pasta_id": request.form.get("pasta_id"),
        "cliente_id": request.form.get("cliente_id"),
        "ambiente_id": request.form.get("ambiente_id"),
        "implantador_id": request.form.get("implantador_id"),
        "faixa_rede_id": request.form.get("faixa_rede_id"),
        "licenca_o3web_id": request.form.get("licenca_o3web_id"),
        "categoria": request.form.get("categoria"),
        "titulo": request.form.get("titulo"),
        "host": request.form.get("host"),
        "porta": request.form.get("porta"),
        "url": request.form.get("url"),
        "usuario": request.form.get("usuario"),
        "senha": request.form.get("senha"),
        "observacoes": request.form.get("observacoes"),
        "proxmox_node_id": request.form.get("proxmox_node_id"),
        "proxmox_vm_id": request.form.get("proxmox_vm_id"),
        "pbs_server_id": request.form.get("pbs_server_id"),
        "zabbix_host_id": request.form.get("zabbix_host_id"),
        "proxmox_node_inventory_id": request.form.get("proxmox_node_inventory_id"),
        "proxmox_inventory_id": request.form.get("proxmox_inventory_id"),
        "pbs_backup_snapshot_id": request.form.get("pbs_backup_snapshot_id"),
        "zabbix_host_inventory_id": request.form.get("zabbix_host_inventory_id"),
        "ativo": request.form.get("ativo", "1"),
    }


def _email_usuario_logado():
    for chave in ("user_email", "email", "usuario_email", "login_email"):
        valor = session.get(chave)
        if valor:
            return valor
    return "sistema"


def _faixa_rede_form_data():
    return {
        "rede": request.form.get("rede"),
        "quantidade_servidores": request.form.get("quantidade_servidores"),
        "fw_wan": request.form.get("fw_wan"),
        "fw_lan": request.form.get("fw_lan"),
        "cliente_id": request.form.get("cliente_id"),
        "cliente_nome": request.form.get("cliente_nome"),
        "cliente_cnpj": request.form.get("cliente_cnpj"),
        "vpn": request.form.get("vpn"),
        "porta_inicio": request.form.get("porta_inicio"),
        "porta_fim": request.form.get("porta_fim"),
        "portas": request.form.get("portas"),
        "pve": request.form.get("pve"),
        "observacoes": request.form.get("observacoes"),
        "ativo": request.form.get("ativo", "1"),
    }


def _licenca_o3web_form_data():
    return {
        "cliente_id": request.form.get("cliente_id"),
        "cliente_cnpj": request.form.get("cliente_cnpj"),
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
        "responsavel_implantador_id": request.form.get("responsavel_implantador_id"),
        "implantador_id": request.form.get("implantador_id"),
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
