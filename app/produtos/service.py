"""
Produto Service

Responsável pelas regras de negócio do catálogo técnico.
"""

from app.repositories.produto_repository import ProdutoRepository


class ProdutoService:

    ####################################################################
    # CONSULTAS
    ####################################################################

    @staticmethod
    def listar():

        return ProdutoRepository.listar()

    @staticmethod
    def buscar(produto_id):

        return ProdutoRepository.buscar(produto_id)

    @staticmethod
    def buscar_por_codigo(codigo):

        return ProdutoRepository.buscar_por_codigo(codigo)

    @staticmethod
    def buscar_por_nome(nome):

        return ProdutoRepository.buscar_por_nome(nome)

    ####################################################################
    # CADASTRO
    ####################################################################

    @staticmethod
    def salvar(dados):

        existente = ProdutoRepository.buscar_por_codigo(

            dados["codigo"]

        )

        if existente:

            raise ValueError(

                "Já existe um produto com este código."

            )

        return ProdutoRepository.inserir(dados)

    ####################################################################
    # ALTERAÇÃO
    ####################################################################

    @staticmethod
    def atualizar(produto_id, dados):

        return ProdutoRepository.atualizar(

            produto_id,

            dados

        )

    ####################################################################
    # IMPORTAÇÃO
    ####################################################################

    @staticmethod
    def importar(resultado):

        resumo = {

            "criados": 0,

            "atualizados": 0,

            "ignorados": 0,

            "erros": 0,

        }

        for produto in resultado.produtos:

            codigo = produto.upper().replace(" ", "_")

            existente = ProdutoRepository.buscar_por_codigo(

                codigo

            )

            if existente:

                resumo["ignorados"] += 1

                continue

            ProdutoRepository.inserir({

                "categoria_id": 1,

                "codigo": codigo,

                "nome": produto,

                "descricao": produto,

                "origem": "MANUAL",

                "ativo": True,

            })

            resumo["criados"] += 1

        return resumo

    ####################################################################
    # VALIDAÇÃO
    ####################################################################

    @staticmethod
    def validar(dados):

        erros = []

        if not dados.get("codigo"):

            erros.append(

                "Código obrigatório."

            )

        if not dados.get("nome"):

            erros.append(

                "Nome obrigatório."

            )

        return erros
