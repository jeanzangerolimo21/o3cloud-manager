import csv
import io

from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.catalogo.service import CatalogoService
from app.catalogo.categorias.service import CategoriaService
from app.catalogo.faixas.service import ProdutoFaixaService
from app.catalogo.import_service import ImportCatalogService
from app.catalogo.modelos.service import ProdutoModeloService
from app.catalogo.precos.service import PrecoCatalogoService
from app.catalogo.produtos.service import ProdutoService
from app.catalogo.recursos.service import ProdutoRecursoService
from app.core.storage import StorageService
from app.catalogo.servidores.service import ProdutoServidorService
from app.catalogo.hardware_parceiros_service import HardwareParceirosService
from app.importadores.base44 import Base44Importer


catalogo_bp = Blueprint(
    "catalogo",
    __name__,
    url_prefix="/catalogo"
)


####################################################################
# DASHBOARD
####################################################################

@catalogo_bp.route("/")
def index():

    dashboard = CatalogoService.dashboard()

    return render_template(
        "catalogo/index.html",
        **dashboard
    )


####################################################################
# CATEGORIAS
####################################################################

@catalogo_bp.route("/categorias")
def listar_categorias():

    return render_template(
        "catalogo/categorias/index.html",
        categorias=CategoriaService.listar()
    )


####################################################################
# NOVA CATEGORIA
####################################################################

@catalogo_bp.route(
    "/categorias/novo",
    methods=["GET", "POST"]
)
def nova_categoria():

    if request.method == "POST":

        dados = {

            "codigo": request.form.get("codigo"),

            "nome": request.form.get("nome"),

            "descricao": request.form.get("descricao"),

            "cor": request.form.get("cor"),

            "ordem": request.form.get("ordem", 0),

            "ativo": bool(request.form.get("ativo"))

        }

        try:

            CategoriaService.criar(dados)

            flash(
                "Categoria cadastrada com sucesso.",
                "success"
            )

            return redirect(
                url_for("catalogo.listar_categorias")
            )

        except Exception as e:

            flash(str(e), "danger")

    return render_template(

        "catalogo/categorias/form.html",

        categoria=None,

        cancel_url=url_for(
            "catalogo.listar_categorias"
        )

    )


####################################################################
# VISUALIZAR CATEGORIA
####################################################################

@catalogo_bp.route("/categorias/<int:categoria_id>")
def visualizar_categoria(categoria_id):

    categoria = CategoriaService.buscar(categoria_id)

    return render_template(

        "catalogo/categorias/view.html",

        categoria=categoria

    )


####################################################################
# EDITAR CATEGORIA
####################################################################

@catalogo_bp.route(
    "/categorias/<int:categoria_id>/editar",
    methods=["GET", "POST"]
)
def editar_categoria(categoria_id):

    categoria = CategoriaService.buscar(categoria_id)

    if not categoria:

        flash(
            "Categoria não encontrada.",
            "danger"
        )

        return redirect(
            url_for(
                "catalogo.listar_categorias"
            )
        )

    if request.method == "POST":

        dados = {

            "codigo": request.form.get("codigo"),

            "nome": request.form.get("nome"),

            "descricao": request.form.get("descricao"),

            "cor": request.form.get("cor"),

            "ordem": request.form.get("ordem", 0),

            "ativo": bool(
                request.form.get("ativo")
            )

        }

        try:

            CategoriaService.atualizar(

                categoria_id,

                dados

            )

            flash(

                "Categoria atualizada com sucesso.",

                "success"

            )

            return redirect(

                url_for(

                    "catalogo.listar_categorias"

                )

            )

        except Exception as e:

            flash(str(e), "danger")

    return render_template(

        "catalogo/categorias/form.html",

        categoria=categoria,

        cancel_url=url_for(

            "catalogo.listar_categorias"

        )

    )


####################################################################
# DESATIVAR CATEGORIA
####################################################################

@catalogo_bp.route(
    "/categorias/<int:categoria_id>/desativar"
)
def desativar_categoria(categoria_id):

    try:

        CategoriaService.desativar(categoria_id)

        flash(

            "Categoria desativada com sucesso.",

            "success"

        )

    except Exception as e:

        flash(str(e), "danger")

    return redirect(

        url_for(

            "catalogo.listar_categorias"

        )

    )


####################################################################
# PRODUTOS
####################################################################
@catalogo_bp.route("/produtos")
def listar_produtos():

    return render_template(
        "catalogo/produtos/index.html",
        produtos=ProdutoService.listar()
    )


@catalogo_bp.route("/produtos/custos", methods=["GET", "POST"])
def custos_produtos():

    resumo = None

    if request.method == "POST":
        try:
            resumo = ProdutoService.importar_custos_csv(request.files.get("arquivo"))
            if resumo["erros"]:
                flash("Importacao concluida com erros. Verifique o resumo abaixo.", "warning")
            else:
                flash("Custos importados com sucesso.", "success")
        except Exception as erro:
            flash(str(erro), "danger")

    return render_template(
        "catalogo/produtos/custos.html",
        produtos=ProdutoService.listar_custos_pendentes(),
        resumo=resumo,
    )


@catalogo_bp.route("/produtos/custos/exportar.csv")
def exportar_custos_produtos_csv():

    produtos = ProdutoService.listar_custos_pendentes()

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=';')
    writer.writerow([
        'codigo',
        'codigo_externo',
        'nome',
        'categoria',
        'tipo_recurso',
        'itens_vinculados',
        'clientes_total',
        'valor_total_itens',
        'valor_custo',
    ])
    writer.writerows(ProdutoService.linhas_exportacao_custos(produtos))

    return Response(
        buffer.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': 'attachment; filename=produtos_custos_pendentes.csv',
        },
    )


####################################################################
# RECURSOS DE SERVIDOR
####################################################################

@catalogo_bp.route("/recursos-servidor")
def listar_recursos_servidor():

    return render_template(
        "catalogo/recursos/index.html",
        recursos=ProdutoRecursoService.listar()
    )


@catalogo_bp.route(
    "/recursos-servidor/novo",
    methods=["GET", "POST"]
)
def novo_recurso_servidor():

    if request.method == "POST":

        dados = {
            "codigo": request.form.get("codigo"),
            "categoria": request.form.get("categoria"),
            "nome": request.form.get("nome"),
            "descricao": request.form.get("descricao"),
            "tipo_recurso": request.form.get("tipo_recurso"),
            "valor_mensal": request.form.get("valor_mensal"),
            "valor_instalacao": request.form.get("valor_instalacao"),
            "ordem": request.form.get("ordem", 0),
            "ativo": bool(request.form.get("ativo")),
        }

        try:
            ProdutoRecursoService.criar(dados)
            flash("Recurso de servidor cadastrado com sucesso.", "success")
            return redirect(url_for("catalogo.listar_recursos_servidor"))
        except Exception as erro:
            flash(str(erro), "danger")

    return render_template(
        "catalogo/recursos/form.html",
        recurso=None,
        categorias_recurso=ProdutoRecursoService.listar_categorias(),
        tipos_recurso=ProdutoRecursoService.listar_tipos_recurso(),
        cancel_url=url_for("catalogo.listar_recursos_servidor"),
    )


@catalogo_bp.route("/recursos-servidor/<int:recurso_id>")
def visualizar_recurso_servidor(recurso_id):

    recurso = ProdutoRecursoService.buscar(recurso_id)

    if not recurso:
        flash("Recurso de servidor não encontrado.", "danger")
        return redirect(url_for("catalogo.listar_recursos_servidor"))

    return render_template(
        "catalogo/recursos/view.html",
        recurso=recurso,
        cancel_url=url_for("catalogo.listar_recursos_servidor"),
    )


@catalogo_bp.route(
    "/recursos-servidor/<int:recurso_id>/editar",
    methods=["GET", "POST"]
)
def editar_recurso_servidor(recurso_id):

    recurso = ProdutoRecursoService.buscar(recurso_id)

    if not recurso:
        flash("Recurso de servidor não encontrado.", "danger")
        return redirect(url_for("catalogo.listar_recursos_servidor"))

    if request.method == "POST":

        dados = {
            "codigo": request.form.get("codigo"),
            "categoria": request.form.get("categoria"),
            "nome": request.form.get("nome"),
            "descricao": request.form.get("descricao"),
            "tipo_recurso": request.form.get("tipo_recurso"),
            "valor_mensal": request.form.get("valor_mensal"),
            "valor_instalacao": request.form.get("valor_instalacao"),
            "ordem": request.form.get("ordem", 0),
            "ativo": bool(request.form.get("ativo")),
        }

        try:
            ProdutoRecursoService.atualizar(recurso_id, dados)
            flash("Recurso de servidor atualizado com sucesso.", "success")
            return redirect(url_for("catalogo.listar_recursos_servidor"))
        except Exception as erro:
            flash(str(erro), "danger")

    return render_template(
        "catalogo/recursos/form.html",
        recurso=recurso,
        categorias_recurso=ProdutoRecursoService.listar_categorias(),
        tipos_recurso=ProdutoRecursoService.listar_tipos_recurso(),
        cancel_url=url_for("catalogo.listar_recursos_servidor"),
    )


@catalogo_bp.route("/recursos-servidor/<int:recurso_id>/desativar")
def desativar_recurso_servidor(recurso_id):

    try:
        ProdutoRecursoService.desativar(recurso_id)
        flash("Recurso de servidor desativado com sucesso.", "success")
    except Exception as erro:
        flash(str(erro), "danger")

    return redirect(url_for("catalogo.listar_recursos_servidor"))


####################################################################
# NOVO PRODUTO
####################################################################

@catalogo_bp.route(
    "/produtos/novo",
    methods=["GET", "POST"]
)
def novo_produto():

    if request.method == "POST":

        dados = {

            "categoria_id": request.form.get("categoria_id"),

            "parceiro_id": request.form.get("parceiro_id"),

            "codigo": request.form.get("codigo"),

            "codigo_externo": request.form.get("codigo_externo"),

            "nome": request.form.get("nome"),

            "descricao": request.form.get("descricao"),

            "unidade": request.form.get("unidade") or "UN",

            "tipo_recurso": request.form.get("tipo_recurso"),

            "valor_venda": request.form.get("valor_venda"),

            "valor_custo": request.form.get("valor_custo"),

            "origem": request.form.get("origem", "MANUAL"),

            "ativo": bool(request.form.get("ativo"))

        }

        try:

            ProdutoService.criar(dados)

            flash(
                "Produto cadastrado com sucesso.",
                "success"
            )

            return redirect(
                url_for("catalogo.listar_produtos")
            )

        except Exception as e:

            flash(str(e), "danger")

    return render_template(

        "catalogo/produtos/form.html",

        produto=None,

        categorias=ProdutoService.listar_categorias(),

        parceiros=ProdutoService.listar_parceiros(),

        tipos_recurso=ProdutoService.listar_tipos_recurso(),

        cancel_url=url_for(
            "catalogo.listar_produtos"
        )

    )


####################################################################
# VISUALIZAR PRODUTO
####################################################################

@catalogo_bp.route("/produtos/<int:produto_id>")
def visualizar_produto(produto_id):

    produto = ProdutoService.buscar(produto_id)

    if not produto:

        flash(
            "Produto não encontrado.",
            "danger"
        )

        return redirect(
            url_for("catalogo.listar_produtos")
        )

    return render_template(

        "catalogo/produtos/view.html",

        produto=produto

    )


####################################################################
# EDITAR PRODUTO
####################################################################

@catalogo_bp.route(
    "/produtos/<int:produto_id>/editar",
    methods=["GET", "POST"]
)
def editar_produto(produto_id):

    produto = ProdutoService.buscar(produto_id)

    if not produto:

        flash(
            "Produto não encontrado.",
            "danger"
        )

        return redirect(
            url_for("catalogo.listar_produtos")
        )

    if request.method == "POST":

        dados = {

            "categoria_id": request.form.get("categoria_id"),

            "parceiro_id": request.form.get("parceiro_id"),

            "codigo": request.form.get("codigo"),

            "codigo_externo": request.form.get("codigo_externo"),

            "nome": request.form.get("nome"),

            "descricao": request.form.get("descricao"),

            "unidade": request.form.get("unidade") or "UN",

            "tipo_recurso": request.form.get("tipo_recurso"),

            "valor_venda": request.form.get("valor_venda"),

            "valor_custo": request.form.get("valor_custo"),

            "origem": request.form.get("origem", "MANUAL"),

            "ativo": bool(request.form.get("ativo"))

        }

        try:

            ProdutoService.atualizar(

                produto_id,

                dados

            )

            flash(

                "Produto atualizado com sucesso.",

                "success"

            )

            return redirect(

                url_for(

                    "catalogo.listar_produtos"

                )

            )

        except Exception as e:

            flash(str(e), "danger")

    return render_template(

        "catalogo/produtos/form.html",

        produto=produto,

        categorias=ProdutoService.listar_categorias(),

        parceiros=ProdutoService.listar_parceiros(),

        tipos_recurso=ProdutoService.listar_tipos_recurso(),

        cancel_url=url_for(
            "catalogo.listar_produtos"
        )

    )


####################################################################
# DESATIVAR PRODUTO
####################################################################

@catalogo_bp.route(
    "/produtos/<int:produto_id>/desativar"
)
def desativar_produto(produto_id):

    try:

        ProdutoService.desativar(produto_id)

        flash(

            "Produto desativado com sucesso.",

            "success"

        )

    except Exception as e:

        flash(str(e), "danger")

    return redirect(

        url_for(

            "catalogo.listar_produtos"

        )

    )

####################################################################
# MODELOS
####################################################################

@catalogo_bp.route("/modelos")
def listar_modelos():

    return render_template(
        "catalogo/modelos/index.html",
        modelos=ProdutoModeloService.listar()
    )


@catalogo_bp.route(
    "/modelos/novo",
    methods=["GET", "POST"]
)
def novo_modelo():

    if request.method == "POST":

        dados = {
            "produto_id": request.form.get("produto_id"),
            "codigo": request.form.get("codigo"),
            "nome": request.form.get("nome"),
            "descricao": request.form.get("descricao"),
            "ordem": request.form.get("ordem", 0),
            "padrao": bool(request.form.get("padrao")),
            "versao": request.form.get("versao"),
            "ativo": bool(request.form.get("ativo")),
        }

        try:
            ProdutoModeloService.criar(dados)

            flash("Modelo cadastrado com sucesso.", "success")

            return redirect(url_for("catalogo.listar_modelos"))

        except Exception as erro:
            flash(str(erro), "danger")

    return render_template(
        "catalogo/modelos/form.html",
        modelo=None,
        produtos=ProdutoModeloService.listar_produtos(),
        cancel_url=url_for("catalogo.listar_modelos"),
    )


@catalogo_bp.route("/modelos/<int:modelo_id>")
def visualizar_modelo(modelo_id):

    modelo = ProdutoModeloService.buscar(modelo_id)

    if not modelo:
        flash("Modelo não encontrado.", "danger")

        return redirect(url_for("catalogo.listar_modelos"))

    return render_template(
        "catalogo/modelos/view.html",
        modelo=modelo,
    )


@catalogo_bp.route(
    "/modelos/<int:modelo_id>/editar",
    methods=["GET", "POST"]
)
def editar_modelo(modelo_id):

    modelo = ProdutoModeloService.buscar(modelo_id)

    if not modelo:
        flash("Modelo não encontrado.", "danger")

        return redirect(url_for("catalogo.listar_modelos"))

    if request.method == "POST":

        dados = {
            "produto_id": request.form.get("produto_id"),
            "codigo": request.form.get("codigo"),
            "nome": request.form.get("nome"),
            "descricao": request.form.get("descricao"),
            "ordem": request.form.get("ordem", 0),
            "padrao": bool(request.form.get("padrao")),
            "versao": request.form.get("versao"),
            "ativo": bool(request.form.get("ativo")),
        }

        try:
            ProdutoModeloService.atualizar(modelo_id, dados)

            flash("Modelo atualizado com sucesso.", "success")

            return redirect(url_for("catalogo.listar_modelos"))

        except Exception as erro:
            flash(str(erro), "danger")

    return render_template(
        "catalogo/modelos/form.html",
        modelo=modelo,
        produtos=ProdutoModeloService.listar_produtos(),
        cancel_url=url_for("catalogo.listar_modelos"),
    )


@catalogo_bp.route("/modelos/<int:modelo_id>/desativar")
def desativar_modelo(modelo_id):

    try:
        ProdutoModeloService.desativar(modelo_id)

        flash("Modelo desativado com sucesso.", "success")

    except Exception as erro:
        flash(str(erro), "danger")

    return redirect(url_for("catalogo.listar_modelos"))


####################################################################
# FAIXAS
####################################################################

@catalogo_bp.route("/faixas")
def listar_faixas():

    return render_template(
        "catalogo/faixas/index.html",
        faixas=ProdutoFaixaService.listar()
    )


@catalogo_bp.route(
    "/faixas/novo",
    methods=["GET", "POST"]
)
def nova_faixa():

    if request.method == "POST":

        dados = {
            "produto_id": request.form.get("produto_id"),
            "modelo_id": request.form.get("modelo_id"),
            "codigo": request.form.get("codigo"),
            "nome": request.form.get("nome"),
            "usuarios_inicio": request.form.get("usuarios_inicio"),
            "usuarios_fim": request.form.get("usuarios_fim"),
            "descricao": request.form.get("descricao"),
            "ordem": request.form.get("ordem", 0),
            "permite_upgrade_manual": bool(
                request.form.get("permite_upgrade_manual")
            ),
            "ativo": bool(request.form.get("ativo")),
        }

        preco_dados = {
            "valor_mensal": request.form.get("valor_mensal"),
            "valor_setup": request.form.get("valor_setup"),
            "tem_projeto": bool(request.form.get("tem_projeto")),
            "ativo": True,
        }

        try:
            faixa_id = ProdutoFaixaService.criar(dados)
            preco_dados["faixa_id"] = faixa_id
            PrecoCatalogoService.salvar_por_faixa(preco_dados)

            flash("Faixa cadastrada com sucesso.", "success")

            return redirect(url_for("catalogo.listar_faixas"))

        except Exception as erro:
            flash(str(erro), "danger")

    return render_template(
        "catalogo/faixas/form.html",
        faixa=None,
        produtos=ProdutoFaixaService.listar_produtos(),
        modelos=ProdutoFaixaService.listar_modelos(),
        cancel_url=url_for("catalogo.listar_faixas"),
    )


@catalogo_bp.route("/faixas/<int:faixa_id>")
def visualizar_faixa(faixa_id):

    faixa = ProdutoFaixaService.buscar(faixa_id)

    if not faixa:
        flash("Faixa não encontrada.", "danger")

        return redirect(url_for("catalogo.listar_faixas"))

    return render_template(
        "catalogo/faixas/view.html",
        faixa=faixa,
    )


@catalogo_bp.route(
    "/faixas/<int:faixa_id>/editar",
    methods=["GET", "POST"]
)
def editar_faixa(faixa_id):

    faixa = ProdutoFaixaService.buscar(faixa_id)

    if not faixa:
        flash("Faixa não encontrada.", "danger")

        return redirect(url_for("catalogo.listar_faixas"))

    if request.method == "POST":

        dados = {
            "produto_id": request.form.get("produto_id"),
            "modelo_id": request.form.get("modelo_id"),
            "codigo": request.form.get("codigo"),
            "nome": request.form.get("nome"),
            "usuarios_inicio": request.form.get("usuarios_inicio"),
            "usuarios_fim": request.form.get("usuarios_fim"),
            "descricao": request.form.get("descricao"),
            "ordem": request.form.get("ordem", 0),
            "permite_upgrade_manual": bool(
                request.form.get("permite_upgrade_manual")
            ),
            "ativo": bool(request.form.get("ativo")),
        }

        preco_dados = {
            "faixa_id": faixa_id,
            "valor_mensal": request.form.get("valor_mensal"),
            "valor_setup": request.form.get("valor_setup"),
            "tem_projeto": bool(request.form.get("tem_projeto")),
            "ativo": True,
        }

        try:
            ProdutoFaixaService.atualizar(faixa_id, dados)
            PrecoCatalogoService.salvar_por_faixa(preco_dados)

            flash("Faixa atualizada com sucesso.", "success")

            return redirect(url_for("catalogo.listar_faixas"))

        except Exception as erro:
            flash(str(erro), "danger")

    return render_template(
        "catalogo/faixas/form.html",
        faixa=faixa,
        produtos=ProdutoFaixaService.listar_produtos(),
        modelos=ProdutoFaixaService.listar_modelos(faixa["produto_id"]),
        cancel_url=url_for("catalogo.listar_faixas"),
    )


@catalogo_bp.route("/faixas/<int:faixa_id>/desativar")
def desativar_faixa(faixa_id):

    try:
        ProdutoFaixaService.desativar(faixa_id)

        flash("Faixa desativada com sucesso.", "success")

    except Exception as erro:
        flash(str(erro), "danger")

    return redirect(url_for("catalogo.listar_faixas"))


####################################################################
# SERVIDORES
####################################################################

@catalogo_bp.route("/servidores")
def listar_servidores():
    parceiro = request.args.get("parceiro")

    return render_template(
        "catalogo/servidores/index.html",
        servidores=ProdutoServidorService.listar(),
        hardware_base=HardwareParceirosService.listar(parceiro),
        parceiros_hardware=HardwareParceirosService.listar_parceiros(),
        parceiro_selecionado=parceiro,
    )


@catalogo_bp.route(
    "/servidores/novo",
    methods=["GET", "POST"]
)
def novo_servidor():

    if request.method == "POST":

        dados = {
            "produto_id": request.form.get("produto_id"),
            "modelo_id": request.form.get("modelo_id"),
            "faixa_id": request.form.get("faixa_id"),
            "codigo": request.form.get("codigo"),
            "nome": request.form.get("nome"),
            "tipo": request.form.get("tipo"),
            "sistema_operacional": request.form.get("sistema_operacional"),
            "observacoes": request.form.get("observacoes"),
            "ordem": request.form.get("ordem", 0),
            "ativo": bool(request.form.get("ativo")),
        }

        try:
            ProdutoServidorService.criar(dados)

            flash("Servidor cadastrado com sucesso.", "success")

            return redirect(url_for("catalogo.listar_servidores"))

        except Exception as erro:
            flash(str(erro), "danger")

    return render_template(
        "catalogo/servidores/form.html",
        servidor=None,
        produtos=ProdutoServidorService.listar_produtos(),
        modelos=ProdutoServidorService.listar_modelos(),
        faixas=ProdutoServidorService.listar_faixas(),
        tipos=ProdutoServidorService.listar_tipos(),
        cancel_url=url_for("catalogo.listar_servidores"),
    )


@catalogo_bp.route("/servidores/<int:servidor_id>")
def visualizar_servidor(servidor_id):

    servidor = ProdutoServidorService.buscar(servidor_id)

    if not servidor:
        flash("Servidor nao encontrado.", "danger")

        return redirect(url_for("catalogo.listar_servidores"))

    return render_template(
        "catalogo/servidores/view.html",
        servidor=servidor,
    )


@catalogo_bp.route(
    "/servidores/<int:servidor_id>/editar",
    methods=["GET", "POST"]
)
def editar_servidor(servidor_id):

    servidor = ProdutoServidorService.buscar(servidor_id)

    if not servidor:
        flash("Servidor nao encontrado.", "danger")

        return redirect(url_for("catalogo.listar_servidores"))

    if request.method == "POST":

        dados = {
            "produto_id": request.form.get("produto_id"),
            "modelo_id": request.form.get("modelo_id"),
            "faixa_id": request.form.get("faixa_id"),
            "codigo": request.form.get("codigo"),
            "nome": request.form.get("nome"),
            "tipo": request.form.get("tipo"),
            "sistema_operacional": request.form.get("sistema_operacional"),
            "observacoes": request.form.get("observacoes"),
            "ordem": request.form.get("ordem", 0),
            "ativo": bool(request.form.get("ativo")),
        }

        try:
            ProdutoServidorService.atualizar(servidor_id, dados)

            flash("Servidor atualizado com sucesso.", "success")

            return redirect(url_for("catalogo.listar_servidores"))

        except Exception as erro:
            flash(str(erro), "danger")

    return render_template(
        "catalogo/servidores/form.html",
        servidor=servidor,
        produtos=ProdutoServidorService.listar_produtos(),
        modelos=ProdutoServidorService.listar_modelos(servidor["produto_id"]),
        faixas=ProdutoServidorService.listar_faixas(
            servidor["produto_id"],
            servidor["modelo_id"],
        ),
        tipos=ProdutoServidorService.listar_tipos(),
        cancel_url=url_for("catalogo.listar_servidores"),
    )


@catalogo_bp.route("/servidores/<int:servidor_id>/desativar")
def desativar_servidor(servidor_id):

    try:
        ProdutoServidorService.desativar(servidor_id)

        flash("Servidor desativado com sucesso.", "success")

    except Exception as erro:
        flash(str(erro), "danger")

    return redirect(url_for("catalogo.listar_servidores"))


####################################################################
# BASE DE HARDWARE DOS PARCEIROS
####################################################################

@catalogo_bp.route("/servidores/hardware/importar", methods=["POST"])
def importar_hardware_parceiros():
    arquivo = request.files.get("arquivo")
    if not arquivo or not arquivo.filename:
        flash("Selecione um arquivo CSV.", "danger")
        return redirect(url_for("catalogo.listar_servidores"))
    try:
        total = HardwareParceirosService.importar_csv(arquivo.stream)
        flash(f"{total} item(ns) importado(s) para a base de hardware.", "success")
    except Exception as erro:
        flash(str(erro), "danger")
    return redirect(url_for("catalogo.listar_servidores"))


@catalogo_bp.route("/servidores/hardware/novo", methods=["GET", "POST"])
def novo_hardware_parceiro():
    if request.method == "POST":
        try:
            HardwareParceirosService.criar(_dados_hardware_form())
            flash("Item de hardware cadastrado com sucesso.", "success")
            return redirect(url_for("catalogo.listar_servidores"))
        except Exception as erro:
            flash(str(erro), "danger")
    return render_template("catalogo/servidores/hardware_form.html", item=None)


@catalogo_bp.route("/servidores/hardware/<int:item_id>/editar", methods=["GET", "POST"])
def editar_hardware_parceiro(item_id):
    item = HardwareParceirosService.buscar(item_id)
    if not item:
        flash("Item de hardware nao encontrado.", "danger")
        return redirect(url_for("catalogo.listar_servidores"))
    if request.method == "POST":
        try:
            HardwareParceirosService.atualizar(item_id, _dados_hardware_form())
            flash("Item de hardware atualizado com sucesso.", "success")
            return redirect(url_for("catalogo.listar_servidores"))
        except Exception as erro:
            flash(str(erro), "danger")
    return render_template("catalogo/servidores/hardware_form.html", item=item)


@catalogo_bp.route("/servidores/hardware/<int:item_id>/excluir", methods=["POST"])
def excluir_hardware_parceiro(item_id):
    HardwareParceirosService.excluir(item_id)
    flash("Item de hardware excluido com sucesso.", "success")
    return redirect(url_for("catalogo.listar_servidores"))


def _dados_hardware_form():
    return {
        "parceiro": request.form.get("parceiro"),
        "secao": request.form.get("secao"),
        "faixa_usuarios": request.form.get("faixa_usuarios"),
        "memoria": request.form.get("memoria"),
        "processador": request.form.get("processador"),
        "disco": request.form.get("disco"),
        "ordem": request.form.get("ordem", 0),
        "ativo": bool(request.form.get("ativo")),
    }


####################################################################
# TABELA DE PRECOS
####################################################################

@catalogo_bp.route("/tabela-precos")
def listar_tabela_precos():

    return render_template(
        "catalogo/precos/index.html",
        licencas=PrecoCatalogoService.listar_licenciamento(),
        recursos=ProdutoRecursoService.listar(),
    )


@catalogo_bp.route("/tabela-precos/exportar.csv")
def exportar_tabela_precos_csv():

    licencas = PrecoCatalogoService.listar_licenciamento()
    recursos = ProdutoRecursoService.listar()

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=';')

    writer.writerow([
        'tipo',
        'categoria',
        'item',
        'descricao',
        'mensal',
        'minimo_instalacao',
        'qtd_minima',
        'tem_projeto',
    ])

    for licenca in licencas:
        writer.writerow([
            'Licenciamento por Usuario',
            'Licenciamento',
            licenca['software'],
            licenca['descricao'],
            licenca['valor_mensal'],
            licenca['valor_setup'],
            licenca['qtd_minima'],
            'Sim' if licenca['tem_projeto'] else 'Nao',
        ])

    for recurso in recursos:
        writer.writerow([
            'Recurso de Servidor',
            recurso['categoria'],
            recurso['nome'],
            recurso['descricao'],
            recurso['valor_mensal'],
            recurso['valor_instalacao'],
            '',
            '',
        ])

    return Response(
        buffer.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': 'attachment; filename=tabela_precos.csv',
        },
    )


####################################################################
# IMPORTAÇÃO
####################################################################

@catalogo_bp.route("/importar", methods=["GET", "POST"])
def importar_catalogo():

    resumo = None
    modo = None

    if request.method == "POST":
        arquivo = request.files.get("arquivo")
        modo = request.form.get("acao") or "validar"

        if not arquivo or not arquivo.filename:
            flash("Selecione um arquivo CSV para importar.", "danger")
        else:
            try:
                salvo = StorageService.salvar(
                    arquivo,
                    StorageService.TEMPORARIOS,
                )
                caminho = StorageService.caminho(
                    StorageService.TEMPORARIOS,
                    salvo["nome"],
                )

                resultado = Base44Importer().executar(caminho)

                if not resultado:
                    raise ValueError("Falha ao interpretar o arquivo enviado.")

                if modo == "validar":
                    resumo = {
                        "categorias": len(resultado.categorias),
                        "produtos": len(resultado.produtos),
                        "modelos": len(resultado.modelos),
                        "faixas": len(resultado.faixas),
                        "precos": len(resultado.precos),
                        "recursos": len(resultado.recursos),
                        "avisos": list(resultado.avisos),
                        "erros": list(resultado.erros),
                    }
                    flash("Validacao concluida sem gravar dados no banco.", "info")
                else:
                    resumo = ImportCatalogService().importar(resultado)

                    if resumo["erros"]:
                        flash(
                            "Importacao concluida com erros. Verifique o resumo abaixo.",
                            "warning",
                        )
                    else:
                        flash("Importacao concluida com sucesso.", "success")

            except Exception as erro:
                flash(str(erro), "danger")

    return render_template(
        "catalogo/importar.html",
        resumo=resumo,
        modo=modo,
    )
