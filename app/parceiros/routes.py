import re
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from app.clientes.service import ClienteService
from app.core.storage import StorageService
from app.parceiros.executivo_service import ParceiroExecutivoService
from app.parceiros.service import ParceiroService


STATUS_NEGOCIACAO = {
    "PRIMEIRO_CONTATO": "Primeiro Contato",
    "AGUARDANDO_PARCEIRO": "Aguardando Parceiro",
    "HOMOLOGADO": "Homologado",
    "SUCESSO": "Sucesso",
    "PERDIDO": "Perdido",
}

CATEGORIAS_PARCEIRO = {
    "PLATINIUM": "Platinium",
    "OURO": "Ouro",
    "PRATA": "Prata",
    "BRONZE": "Bronze",
}


parceiros_bp = Blueprint(
    "parceiros",
    __name__,
    url_prefix="/parceiros"
)


@parceiros_bp.route("/")
def index():
    pesquisa = request.args.get("q")
    status_negociacao = request.args.get("negociacao")
    ativo = _normalizar_filtro_ativo(request.args.get("ativo"))
    executivo_id = request.args.get("executivo_id", type=int)
    pagina = request.args.get("page", 1, type=int)

    parceiros, total = ParceiroService.listar(
        pesquisa=pesquisa,
        status_negociacao=status_negociacao,
        ativo=ativo,
        executivo_id=executivo_id,
        pagina=pagina
    )

    total_paginas = (total + 49) // 50

    return render_template(
        "parceiros/index.html",
        parceiros=parceiros,
        pesquisa=pesquisa,
        selected_negociacao=status_negociacao,
        selected_ativo=request.args.get("ativo", "1"),
        selected_executivo_id=executivo_id,
        executivos_filtro=ParceiroExecutivoService.listar_todos_ativos(),
        pagina=pagina,
        total=total,
        total_paginas=total_paginas,
        placeholder="Pesquisar por parceiro, contato ou telefone",
        page_title="Parceiros",
        page_description="Cadastro dos parceiros comerciais da O3 Cloud.",
        page_icon="bi-people-fill",
        page_button_text="Novo Parceiro",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("parceiros.novo"),
        negociacao_options=STATUS_NEGOCIACAO,
        categoria_options=CATEGORIAS_PARCEIRO,
    )


@parceiros_bp.route("/novo", methods=["GET", "POST"])
def novo():
    executivos = ParceiroExecutivoService.listar_todos_ativos()
    clientes_importacao = ClienteService.listar_para_importacao() if _admin() else []

    if request.method == "POST":
        logo = None
        arquivo = request.files.get("logo")

        if arquivo and arquivo.filename:
            try:
                logo = StorageService.salvar(arquivo, StorageService.PARCEIROS)["nome"]
            except ValueError as erro:
                flash(str(erro), "danger")
                return render_template(
                    "parceiros/form.html",
                    modo="novo",
                    parceiro=_parceiro_form_payload(),
                    executivos=executivos,
                    clientes_importacao=clientes_importacao,
                    status_negociacao_options=STATUS_NEGOCIACAO,
                    categoria_options=CATEGORIAS_PARCEIRO,
                )

        dados = _coletar_dados_parceiro_form(logo=logo)
        try:
            ParceiroService.criar(dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template(
                "parceiros/form.html",
                modo="novo",
                parceiro=_parceiro_form_payload(),
                executivos=executivos,
                clientes_importacao=clientes_importacao,
                status_negociacao_options=STATUS_NEGOCIACAO,
                categoria_options=CATEGORIAS_PARCEIRO,
            )

        flash("Parceiro cadastrado com sucesso.", "success")
        return redirect(url_for("parceiros.index"))

    return render_template(
        "parceiros/form.html",
        modo="novo",
        parceiro=None,
        executivos=executivos,
        clientes_importacao=clientes_importacao,
        status_negociacao_options=STATUS_NEGOCIACAO,
        categoria_options=CATEGORIAS_PARCEIRO,
    )


@parceiros_bp.route("/<int:parceiro_id>")
def visualizar(parceiro_id):
    parceiro = ParceiroService.buscar_por_id(parceiro_id)

    if not parceiro:
        flash("Parceiro não encontrado.", "danger")
        return redirect(url_for("parceiros.index"))

    total_executivos = ParceiroExecutivoService.contar_por_parceiro(parceiro_id)

    return render_template(
        "parceiros/view.html",
        parceiro=parceiro,
        total_executivos=total_executivos,
        status_negociacao_options=STATUS_NEGOCIACAO,
        categoria_options=CATEGORIAS_PARCEIRO,
    )


@parceiros_bp.route("/<int:parceiro_id>/editar", methods=["GET", "POST"])
def editar(parceiro_id):
    parceiro = ParceiroService.buscar_por_id(parceiro_id)
    executivos = ParceiroExecutivoService.listar_todos_ativos()
    clientes_importacao = ClienteService.listar_para_importacao() if _admin() else []

    if not parceiro:
        return redirect(url_for("parceiros.index"))

    if request.method == "POST":
        logo = parceiro.get("logo")
        arquivo = request.files.get("logo")

        if arquivo and arquivo.filename:
            try:
                novo_logo = StorageService.salvar(arquivo, StorageService.PARCEIROS)["nome"]
                if parceiro.get("logo"):
                    StorageService.excluir(StorageService.PARCEIROS, parceiro.get("logo"))
                logo = novo_logo
            except ValueError as erro:
                flash(str(erro), "danger")
                parceiro_form = _parceiro_form_payload()
                parceiro_form["id"] = parceiro_id
                parceiro_form["logo"] = parceiro.get("logo")
                return render_template(
                    "parceiros/form.html",
                    parceiro=parceiro_form,
                    modo="editar",
                    executivos=executivos,
                    clientes_importacao=clientes_importacao,
                    status_negociacao_options=STATUS_NEGOCIACAO,
                    categoria_options=CATEGORIAS_PARCEIRO,
                )

        dados = _coletar_dados_parceiro_form(logo=logo)
        try:
            ParceiroService.atualizar(parceiro_id, dados)
        except ValueError as erro:
            flash(str(erro), "danger")
            parceiro_form = _parceiro_form_payload()
            parceiro_form["id"] = parceiro_id
            parceiro_form["logo"] = parceiro.get("logo")
            return render_template(
                "parceiros/form.html",
                parceiro=parceiro_form,
                modo="editar",
                executivos=executivos,
                clientes_importacao=clientes_importacao,
                status_negociacao_options=STATUS_NEGOCIACAO,
                categoria_options=CATEGORIAS_PARCEIRO,
            )

        flash("Parceiro atualizado com sucesso.", "success")
        return redirect(url_for("parceiros.visualizar", parceiro_id=parceiro_id))

    return render_template(
        "parceiros/form.html",
        parceiro=parceiro,
        modo="editar",
        executivos=executivos,
        clientes_importacao=clientes_importacao,
        status_negociacao_options=STATUS_NEGOCIACAO,
        categoria_options=CATEGORIAS_PARCEIRO,
    )


@parceiros_bp.route("/<int:parceiro_id>/excluir")
def excluir(parceiro_id):
    parceiro = ParceiroService.buscar_por_id(parceiro_id)

    if parceiro and parceiro.get("logo"):
        StorageService.excluir(StorageService.PARCEIROS, parceiro.get("logo"))

    ParceiroService.excluir(parceiro_id)
    flash("Parceiro removido com sucesso.", "success")
    return redirect(url_for("parceiros.index"))


@parceiros_bp.route("/executivos")
@parceiros_bp.route("/<int:parceiro_id>/executivos")
def listar_executivos(parceiro_id=None):
    pesquisa = request.args.get("q")
    pagina = request.args.get("page", 1, type=int)
    ativo = request.args.get("ativo")
    parceiro = None

    if parceiro_id is not None:
        parceiro = ParceiroService.buscar_por_id(parceiro_id)
        if not parceiro:
            flash("Parceiro não encontrado.", "danger")
            return redirect(url_for("parceiros.index"))

    executivos, total = ParceiroExecutivoService.listar(
        pesquisa=pesquisa,
        ativo=ativo,
        parceiro_id=parceiro_id,
        pagina=pagina,
    )

    total_paginas = (total + 49) // 50

    if parceiro:
        page_title = f"Executivos de {parceiro.get('nome_fantasia') or parceiro.get('nome') or parceiro.get('razao_social')}"
        page_description = "Cadastro de executivos de vendas vinculados ao parceiro."
        page_button_url = url_for("parceiros.novo_executivo", parceiro_id=parceiro_id)
        page_secondary_button_url = url_for("parceiros.index")
        page_secondary_button_text = "Voltar Parceiros"
        page_secondary_button_icon = "bi-arrow-left"
    else:
        page_title = "Executivos"
        page_description = "Cadastro de executivos de vendas."
        page_button_url = url_for("parceiros.novo_executivo")
        page_secondary_button_url = url_for("parceiros.index")
        page_secondary_button_text = "Parceiros"
        page_secondary_button_icon = "bi-arrow-left"

    return render_template(
        "parceiros/executivos/index.html",
        executivos=executivos,
        parceiro=parceiro,
        pesquisa=pesquisa,
        selected_status=ativo,
        pagina=pagina,
        total=total,
        total_paginas=total_paginas,
        placeholder="Buscar por nome, parceiro ou e-mail...",
        page_title=page_title,
        page_description=page_description,
        page_icon="bi-person-badge",
        page_button_text="Novo Executivo",
        page_button_icon="bi-plus-circle",
        page_button_url=page_button_url,
        page_secondary_button_url=page_secondary_button_url,
        page_secondary_button_text=page_secondary_button_text,
        page_secondary_button_icon=page_secondary_button_icon,
        pode_excluir_executivo=_pode_excluir_executivo(),
    )


@parceiros_bp.route("/executivos/novo", methods=["GET", "POST"])
def novo_executivo():
    parceiro_id = _partner_id_from_request()
    parceiros = ParceiroExecutivoService.listar_parceiros()

    if request.method == "POST":
        dados = {
            "nome": request.form.get("nome"),
            "email": request.form.get("email"),
            "telefone": request.form.get("telefone"),
            "parceiro_id": request.form.get("parceiro_id"),
            "chave_pix": request.form.get("chave_pix"),
            "informacoes_pagamento": request.form.get("informacoes_pagamento"),
            "premiacao_ativa": request.form.get("premiacao_ativa", "0"),
            "ativo": request.form.get("ativo", "1"),
        }

        try:
            executivo_id = ParceiroExecutivoService.criar(dados)
            flash("Executivo cadastrado com sucesso.", "success")
            return redirect(_executivo_redirect_url(dados.get("parceiro_id"), executivo_id))
        except ValueError as erro:
            flash(str(erro), "danger")

    return render_template(
        "parceiros/executivos/form.html",
        executivo=None,
        parceiros=parceiros,
        parceiro_id=parceiro_id,
        cancel_url=_executivo_cancel_url(parceiro_id),
    )


@parceiros_bp.route("/executivos/<int:executivo_id>")
def visualizar_executivo(executivo_id):
    executivo = ParceiroExecutivoService.buscar_por_id(executivo_id)

    if not executivo:
        flash("Executivo não encontrado.", "danger")
        return redirect(url_for("parceiros.listar_executivos"))

    return render_template(
        "parceiros/executivos/view.html",
        executivo=executivo,
        cancel_url=_executivo_cancel_url(executivo.get("parceiro_id")),
        pode_excluir_executivo=_pode_excluir_executivo(),
    )


@parceiros_bp.route("/executivos/<int:executivo_id>/editar", methods=["GET", "POST"])
def editar_executivo(executivo_id):
    executivo = ParceiroExecutivoService.buscar_por_id(executivo_id)

    if not executivo:
        flash("Executivo não encontrado.", "danger")
        return redirect(url_for("parceiros.listar_executivos"))

    parceiros = ParceiroExecutivoService.listar_parceiros()

    if request.method == "POST":
        dados = {
            "nome": request.form.get("nome"),
            "email": request.form.get("email"),
            "telefone": request.form.get("telefone"),
            "parceiro_id": request.form.get("parceiro_id"),
            "chave_pix": request.form.get("chave_pix"),
            "informacoes_pagamento": request.form.get("informacoes_pagamento"),
            "premiacao_ativa": request.form.get("premiacao_ativa", "0"),
            "ativo": request.form.get("ativo", "1"),
        }

        try:
            ParceiroExecutivoService.atualizar(executivo_id, dados)
            flash("Executivo atualizado com sucesso.", "success")
            return redirect(url_for("parceiros.visualizar_executivo", executivo_id=executivo_id))
        except ValueError as erro:
            flash(str(erro), "danger")

    return render_template(
        "parceiros/executivos/form.html",
        executivo=executivo,
        parceiros=parceiros,
        parceiro_id=executivo.get("parceiro_id"),
        cancel_url=_executivo_cancel_url(executivo.get("parceiro_id")),
    )


@parceiros_bp.route("/executivos/<int:executivo_id>/premiacao", methods=["POST"])
def atualizar_premiacao_executivo(executivo_id):
    executivo = ParceiroExecutivoService.buscar_por_id(executivo_id)

    if not executivo:
        flash("Executivo não encontrado.", "danger")
        return redirect(url_for("parceiros.listar_executivos"))

    try:
        ParceiroExecutivoService.atualizar_premiacao(
            executivo_id,
            request.form.get("premiacao_ativa"),
        )
        flash("Status de premiação do executivo atualizado com sucesso.", "success")
    except ValueError as erro:
        flash(str(erro), "danger")

    return redirect(_redirect_pos_acao(_executivo_cancel_url(executivo.get("parceiro_id"))))


@parceiros_bp.route("/executivos/<int:executivo_id>/excluir", methods=["POST"])
def excluir_executivo(executivo_id):
    if not _pode_excluir_executivo():
        flash("Apenas Administrador ou Diretoria podem excluir executivos.", "danger")
        return redirect(url_for("parceiros.listar_executivos"))

    executivo = ParceiroExecutivoService.buscar_por_id(executivo_id)

    if not executivo:
        flash("Executivo não encontrado.", "danger")
        return redirect(url_for("parceiros.listar_executivos"))

    parceiro_id = executivo.get("parceiro_id")

    try:
        ParceiroExecutivoService.excluir(executivo_id)
        flash("Executivo excluído e desvinculado do parceiro com sucesso.", "success")
    except ValueError as erro:
        flash(str(erro), "danger")

    return redirect(_executivo_cancel_url(parceiro_id))


def _admin():
    return session.get("usuario_perfil") == "ADMIN"


def _pode_excluir_executivo():
    return session.get("usuario_perfil") in ("ADMIN", "DIRETORIA")


def _coletar_dados_parceiro_form(logo=None, parceiro_atual=None):
    razao_social = (request.form.get("razao_social") or "").strip()
    nome_fantasia = (request.form.get("nome_fantasia") or "").strip()
    contato_1_nome = (request.form.get("contato_1_nome") or "").strip()
    contato_1_email = (request.form.get("contato_1_email") or "").strip()
    contato_1_telefone = (request.form.get("contato_1_telefone") or "").strip()

    if not contato_1_nome or not contato_1_email or not contato_1_telefone:
        raise ValueError("Em Pessoas Chave, apenas os campos do Contato 1 sao obrigatorios: nome, e-mail e Cel/WhatsApp.")

    executivo_responsavel_id = request.form.get("executivo_responsavel_id")
    if executivo_responsavel_id in (None, ""):
        executivo_responsavel_id = None
    else:
        executivo_responsavel_id = int(executivo_responsavel_id)

    uf = _normalizar_uf(request.form.get("uf"))
    if len(uf) > 2:
        raise ValueError("UF deve ter no maximo 2 caracteres.")

    status_negociacao = request.form.get("status_negociacao") or "PRIMEIRO_CONTATO"
    informacoes_gerais = (request.form.get("informacoes_gerais") or "").strip()

    sigla = (request.form.get("sigla") or "").strip().upper() or None

    return {
        "nome": nome_fantasia or razao_social,
        "sigla": sigla,
        "tipo": (request.form.get("tipo") or "OUTRO").strip() or "OUTRO",
        "contato": contato_1_nome,
        "email": (request.form.get("email") or "").strip(),
        "telefone": (request.form.get("telefone") or "").strip(),
        "site": (request.form.get("site") or "").strip(),
        "descricao": informacoes_gerais,
        "logo": logo,
        "ativo": 1 if request.form.get("ativo") else 0,
        "premiacao_ativa": 1 if request.form.get("premiacao_ativa") else 0,
        "cnpj": _normalizar_cnpj(request.form.get("cnpj")),
        "segmento": (request.form.get("segmento") or "").strip(),
        "categoria_parceiro": _normalizar_categoria_parceiro(request.form.get("categoria_parceiro")),
        "razao_social": razao_social,
        "nome_fantasia": nome_fantasia,
        "endereco": (request.form.get("endereco") or "").strip(),
        "cidade": (request.form.get("cidade") or "").strip(),
        "uf": uf,
        "contato_1_nome": contato_1_nome,
        "contato_1_email": contato_1_email,
        "contato_1_telefone": contato_1_telefone,
        "contato_2_nome": (request.form.get("contato_2_nome") or "").strip(),
        "contato_2_email": (request.form.get("contato_2_email") or "").strip(),
        "contato_2_telefone": (request.form.get("contato_2_telefone") or "").strip(),
        "contato_3_nome": (request.form.get("contato_3_nome") or "").strip(),
        "contato_3_email": (request.form.get("contato_3_email") or "").strip(),
        "contato_3_telefone": (request.form.get("contato_3_telefone") or "").strip(),
        "executivo_responsavel_id": executivo_responsavel_id,
        "status_negociacao": status_negociacao,
        "informacoes_gerais": informacoes_gerais,
    }


def _parceiro_form_payload():
    return {
        "cnpj": _normalizar_cnpj(request.form.get("cnpj")),
        "segmento": request.form.get("segmento"),
        "categoria_parceiro": request.form.get("categoria_parceiro"),
        "razao_social": request.form.get("razao_social"),
        "nome_fantasia": request.form.get("nome_fantasia"),
        "endereco": request.form.get("endereco"),
        "cidade": request.form.get("cidade"),
        "uf": request.form.get("uf"),
        "telefone": request.form.get("telefone"),
        "email": request.form.get("email"),
        "site": request.form.get("site"),
        "cliente_importado_id": request.form.get("cliente_importado_id"),
        "contato_1_nome": request.form.get("contato_1_nome"),
        "contato_1_email": request.form.get("contato_1_email"),
        "contato_1_telefone": request.form.get("contato_1_telefone"),
        "contato_2_nome": request.form.get("contato_2_nome"),
        "contato_2_email": request.form.get("contato_2_email"),
        "contato_2_telefone": request.form.get("contato_2_telefone"),
        "contato_3_nome": request.form.get("contato_3_nome"),
        "contato_3_email": request.form.get("contato_3_email"),
        "contato_3_telefone": request.form.get("contato_3_telefone"),
        "executivo_responsavel_id": request.form.get("executivo_responsavel_id"),
        "status_negociacao": request.form.get("status_negociacao"),
        "informacoes_gerais": request.form.get("informacoes_gerais"),
        "ativo": 1 if request.form.get("ativo") else 0,
        "premiacao_ativa": 1 if request.form.get("premiacao_ativa") else 0,
    }


def _normalizar_categoria_parceiro(valor):
    categoria = (valor or "").strip().upper()
    return categoria if categoria in CATEGORIAS_PARCEIRO else None


def _normalizar_uf(valor):
    uf = (valor or "").strip().upper()
    if len(uf) <= 2:
        return uf
    return uf[:2]


def _normalizar_filtro_ativo(valor):
    if valor in (None, "", "todos"):
        return None
    if str(valor) == "1":
        return 1
    if str(valor) == "0":
        return 0
    return 1


def _partner_id_from_request():
    valor = request.args.get("parceiro_id") or request.form.get("parceiro_id")
    if not valor:
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _redirect_pos_acao(default_url):
    next_url = request.form.get("next")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return next_url
    return default_url


def _executivo_cancel_url(parceiro_id):
    if parceiro_id:
        return url_for("parceiros.listar_executivos", parceiro_id=parceiro_id)
    return url_for("parceiros.listar_executivos")


def _executivo_redirect_url(parceiro_id, executivo_id):
    if parceiro_id:
        return url_for("parceiros.listar_executivos", parceiro_id=parceiro_id)
    return url_for("parceiros.visualizar_executivo", executivo_id=executivo_id)


def _normalizar_cnpj(valor):
    cnpj = re.sub(r"[^0-9A-Za-z]", "", str(valor or "")).upper()
    return cnpj or None
