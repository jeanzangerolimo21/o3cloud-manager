"""
Catálogo Técnico Comercial

Service responsável pelas regras de negócio do Catálogo Técnico.

Toda persistência é realizada através do CatalogoRepository.
"""

from app.repositories.catalogo_repository import CatalogoRepository


class CatalogoService:

    repository = CatalogoRepository()

    ####################################################################
    # DASHBOARD
    ####################################################################

    @classmethod
    def dashboard(cls):

        return cls.repository.dashboard()


    ####################################################################
    # PRODUTOS
    ####################################################################

    @classmethod
    def listar_produtos(cls):

        return cls.repository.listar_produtos()

    @classmethod
    def buscar_produto(cls, produto_id):

        return cls.repository.buscar_produto(produto_id)

    @classmethod
    def criar_produto(cls, dados):

        cls.validar_produto(dados)

        return cls.repository.criar_produto(dados)

    @classmethod
    def atualizar_produto(cls, produto_id, dados):

        cls.validar_produto(dados)

        return cls.repository.atualizar_produto(
            produto_id,
            dados
        )

    ####################################################################
    # CATEGORIAS
    ####################################################################

    @classmethod
    def listar_categorias(cls):

        return cls.repository.listar_categorias()

    @classmethod
    def criar_categoria(cls, dados):

        return cls.repository.criar_categoria(dados)

    ####################################################################
    # MODELOS
    ####################################################################

    @classmethod
    def listar_modelos(cls):

        return cls.repository.listar_modelos()

    @classmethod
    def criar_modelo(cls, dados):

        return cls.repository.criar_modelo(dados)

    ####################################################################
    # FAIXAS
    ####################################################################

    @classmethod
    def listar_faixas(cls):

        return cls.repository.listar_faixas()

    @classmethod
    def criar_faixa(cls, dados):

        return cls.repository.criar_faixa(dados)

    ####################################################################
    # SERVIDORES
    ####################################################################

    @classmethod
    def listar_servidores(cls):

        return cls.repository.listar_servidores()

    @classmethod
    def criar_servidor(cls, dados):

        return cls.repository.criar_servidor(dados)

    ####################################################################
    # RECURSOS
    ####################################################################

    @classmethod
    def listar_recursos(cls):

        return cls.repository.listar_recursos()

    @classmethod
    def criar_recurso(cls, dados):

        return cls.repository.criar_recurso(dados)

    ####################################################################
    # VALIDAÇÕES
    ####################################################################

    @staticmethod
    def validar_produto(dados):

        if not dados.get("codigo"):

            raise ValueError("Código obrigatório.")

        if not dados.get("nome"):

            raise ValueError("Nome obrigatório.")

        if not dados.get("categoria_id"):

            raise ValueError("Categoria obrigatória.")




