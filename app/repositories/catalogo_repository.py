"""
Repository do Catálogo Técnico.

Este repository funciona como um Facade para todas as tabelas do
catálogo técnico do O3Cloud Manager.
"""

from app.catalogo.categorias.repository import CategoriaRepository
from app.catalogo.faixas.repository import ProdutoFaixaRepository
from app.catalogo.modelos.repository import ProdutoModeloRepository
from app.catalogo.servidores.repository import ProdutoServidorRepository
from app.repositories.produto_repository import ProdutoRepository


class CatalogoRepository:

    ####################################################################
    # PRODUTOS
    ####################################################################

    @staticmethod
    def listar_produtos():

        return ProdutoRepository.listar()

    @staticmethod
    def buscar_produto(produto_id):

        return ProdutoRepository.buscar(produto_id)

    @staticmethod
    def buscar_produto_por_codigo(codigo):

        return ProdutoRepository.buscar_por_codigo(codigo)

    @staticmethod
    def buscar_produto_por_nome(nome):

        return ProdutoRepository.buscar_por_nome(nome)

    @staticmethod
    def criar_produto(dados):

        return ProdutoRepository.inserir(dados)

    @staticmethod
    def atualizar_produto(produto_id, dados):

        return ProdutoRepository.atualizar(

            produto_id,

            dados

        )

    ####################################################################
    # CATEGORIAS
    ####################################################################

    @staticmethod
    def listar_categorias():

        return CategoriaRepository.listar()

    @staticmethod
    def criar_categoria(dados):

        return CategoriaRepository.inserir(dados)

    ####################################################################
    # MODELOS
    ####################################################################

    @staticmethod
    def listar_modelos():

        return ProdutoModeloRepository.listar()

    @staticmethod
    def criar_modelo(dados):

        return ProdutoModeloRepository.inserir(dados)

    ####################################################################
    # FAIXAS
    ####################################################################

    @staticmethod
    def listar_faixas():

        return ProdutoFaixaRepository.listar()

    @staticmethod
    def criar_faixa(dados):

        return ProdutoFaixaRepository.inserir(dados)

    ####################################################################
    # SERVIDORES
    ####################################################################

    @staticmethod
    def listar_servidores():

        return ProdutoServidorRepository.listar()

    @staticmethod
    def criar_servidor(dados):

        return ProdutoServidorRepository.inserir(dados)

    ####################################################################
    # RECURSOS
    ####################################################################

    @staticmethod
    def listar_recursos():

        """
        TODO:
        Será implementado posteriormente.
        """
        return []

    @staticmethod
    def criar_recurso(dados):

        """
        TODO:
        Será implementado posteriormente.
        """
        return None

    ####################################################################
    # DASHBOARD
    ####################################################################

    @classmethod
    def dashboard(cls):

        return {

            "total_produtos": len(cls.listar_produtos()),

            "total_categorias": len(cls.listar_categorias()),

            "total_modelos": len(cls.listar_modelos()),

            "total_faixas": len(cls.listar_faixas()),

            "total_servidores": len(cls.listar_servidores())

        }
