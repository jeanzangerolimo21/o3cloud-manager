"""
Import Service

Responsavel por importar um catalogo tecnico para o O3Cloud Manager.
Recebe um ResultadoImportacao normalizado e grava os modulos suportados.
"""

from app.catalogo.categorias.service import CategoriaService
from app.catalogo.faixas.service import ProdutoFaixaService
from app.catalogo.modelos.service import ProdutoModeloService
from app.catalogo.precos.service import PrecoCatalogoService
from app.catalogo.produtos.service import ProdutoService
from app.catalogo.recursos.service import ProdutoRecursoService


class ImportCatalogService:

    def __init__(self):
        self.categorias = CategoriaService
        self.produtos = ProdutoService
        self.modelos = ProdutoModeloService
        self.faixas = ProdutoFaixaService
        self.precos = PrecoCatalogoService
        self.recursos = ProdutoRecursoService

    def importar(self, resultado):
        resumo = {
            "categorias": 0,
            "produtos": 0,
            "modelos": 0,
            "faixas": 0,
            "precos": 0,
            "recursos": 0,
            "avisos": list(resultado.avisos),
            "erros": [],
        }

        categorias_por_codigo = {}
        produtos_por_codigo = {}

        for categoria in resultado.categorias:
            try:
                existente = self.categorias.buscar_por_codigo(categoria["codigo"])
                if existente:
                    categorias_por_codigo[categoria["codigo"]] = existente
                    continue

                categoria_id = self.categorias.criar(categoria)
                categorias_por_codigo[categoria["codigo"]] = self.categorias.buscar(categoria_id)
                resumo["categorias"] += 1
            except Exception as erro:
                resumo["erros"].append(f"Categoria {categoria.get('nome')}: {erro}")

        for produto in resultado.produtos:
            try:
                categoria = categorias_por_codigo.get(produto["categoria_codigo"])
                if not categoria:
                    categoria = self.categorias.buscar_por_codigo(produto["categoria_codigo"])

                if not categoria:
                    raise ValueError("Categoria relacionada nao encontrada.")

                existente = self.produtos.buscar_por_codigo(produto["codigo"])
                if existente:
                    produtos_por_codigo[produto["codigo"]] = existente
                    continue

                dados = dict(produto)
                dados["categoria_id"] = categoria["id"]
                produto_id = self.produtos.criar(dados)
                produtos_por_codigo[produto["codigo"]] = self.produtos.buscar(produto_id)
                resumo["produtos"] += 1
            except Exception as erro:
                resumo["erros"].append(f"Produto {produto.get('nome')}: {erro}")

        for modelo in resultado.modelos:
            try:
                produto = produtos_por_codigo.get(modelo["produto_codigo"])
                if not produto:
                    produto = self.produtos.buscar_por_codigo(modelo["produto_codigo"])

                if not produto:
                    raise ValueError("Produto relacionado nao encontrado.")

                if self.modelos.buscar_por_codigo(produto["id"], modelo["codigo"]):
                    continue

                dados = dict(modelo)
                dados["produto_id"] = produto["id"]
                self.modelos.criar(dados)
                resumo["modelos"] += 1
            except Exception as erro:
                resumo["erros"].append(f"Modelo {modelo.get('nome')}: {erro}")

        for faixa in resultado.faixas:
            try:
                produto = produtos_por_codigo.get(faixa["produto_codigo"])
                if not produto:
                    produto = self.produtos.buscar_por_codigo(faixa["produto_codigo"])

                if not produto:
                    raise ValueError("Produto relacionado nao encontrado.")

                modelo = self.modelos.buscar_por_codigo(produto["id"], faixa["modelo_codigo"])
                if not modelo:
                    raise ValueError("Modelo relacionado nao encontrado.")

                if self.faixas.buscar_por_intervalo(
                    modelo["id"],
                    faixa["usuarios_inicio"],
                    faixa["usuarios_fim"],
                ):
                    continue

                dados = dict(faixa)
                dados["produto_id"] = produto["id"]
                dados["modelo_id"] = modelo["id"]
                self.faixas.criar(dados)
                resumo["faixas"] += 1
            except Exception as erro:
                resumo["erros"].append(f"Faixa {faixa.get('nome')}: {erro}")

        for preco in resultado.precos:
            try:
                produto = produtos_por_codigo.get(preco["produto_codigo"])
                if not produto:
                    produto = self.produtos.buscar_por_codigo(preco["produto_codigo"])

                if not produto:
                    raise ValueError("Produto relacionado nao encontrado.")

                modelo = self.modelos.buscar_por_codigo(produto["id"], preco["modelo_codigo"])
                if not modelo:
                    raise ValueError("Modelo relacionado nao encontrado.")

                faixa = self.faixas.buscar_por_intervalo(
                    modelo["id"],
                    preco["usuarios_inicio"],
                    preco["usuarios_fim"],
                )
                if not faixa:
                    raise ValueError("Faixa relacionada nao encontrada para o preco.")

                self.precos.salvar_por_faixa({
                    "faixa_id": faixa["id"],
                    "valor_mensal": preco["valor_mensal"],
                    "valor_setup": preco["valor_setup"],
                    "tem_projeto": preco["tem_projeto"],
                    "ativo": True,
                })
                resumo["precos"] += 1
            except Exception as erro:
                resumo["erros"].append(
                    f"Preco faixa {preco.get('produto_codigo')}/{preco.get('modelo_codigo')} ({preco.get('usuarios_inicio')} a {preco.get('usuarios_fim')}): {erro}"
                )

        for recurso in resultado.recursos:
            try:
                existente = self.recursos.buscar_por_codigo(recurso["codigo"])
                dados = dict(recurso)

                if existente:
                    self.recursos.atualizar(existente["id"], dados)
                else:
                    self.recursos.criar(dados)

                resumo["recursos"] += 1
            except Exception as erro:
                resumo["erros"].append(f"Recurso {recurso.get('nome')}: {erro}")

        return resumo

    @staticmethod
    def imprimir_resumo(resumo):
        print()
        print("=" * 60)
        print("IMPORTACAO DO CATALOGO")
        print("=" * 60)
        print(f"Categorias : {resumo['categorias']}")
        print(f"Produtos   : {resumo['produtos']}")
        print(f"Modelos    : {resumo['modelos']}")
        print(f"Faixas     : {resumo['faixas']}")
        print(f"Precos     : {resumo['precos']}")
        print(f"Recursos   : {resumo['recursos']}")
        print(f"Avisos     : {len(resumo['avisos'])}")
        print(f"Erros      : {len(resumo['erros'])}")

        if resumo["avisos"]:
            print()
            print("Lista de avisos:")
            for aviso in resumo["avisos"]:
                print(f" - {aviso}")

        if resumo["erros"]:
            print()
            print("Lista de erros:")
            for erro in resumo["erros"]:
                print(f" - {erro}")

        print("=" * 60)
