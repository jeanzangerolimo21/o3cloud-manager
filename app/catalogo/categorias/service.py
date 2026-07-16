"""
Service de Categorias do Catálogo Técnico.

Responsável pelas regras de negócio.

Não conhece banco de dados.
Não conhece Flask.
Não conhece HTML.

Toda persistência é feita pelo CategoriaRepository.
"""

from app.catalogo.categorias.repository import CategoriaRepository


class CategoriaService:

    repository = CategoriaRepository

    ####################################################################
    # CONSULTAS
    ####################################################################

    @classmethod
    def listar(cls):

        return cls.repository.listar()

    @classmethod
    def buscar(cls, categoria_id):

        return cls.repository.buscar(categoria_id)

    @classmethod
    def buscar_por_codigo(cls, codigo):

        return cls.repository.buscar_por_codigo(codigo)

    @classmethod
    def buscar_por_nome(cls, nome):

        return cls.repository.buscar_por_nome(nome)

    @classmethod
    def contar(cls):

        return cls.repository.contar()

    ####################################################################
    # CADASTRO
    ####################################################################

    @classmethod
    def criar(cls, dados):

        cls.validar(dados)

        if cls.repository.existe(dados["codigo"]):

            raise ValueError(
                "Já existe uma categoria com este código."
            )

        categoria = cls.buscar_por_nome(dados["nome"])

        if categoria:

            raise ValueError(
                "Já existe uma categoria com este nome."
            )

        return cls.repository.inserir(dados)

    ####################################################################
    # ALTERAÇÃO
    ####################################################################

    @classmethod
    def atualizar(cls, categoria_id, dados):

        categoria = cls.buscar(categoria_id)

        if not categoria:

            raise ValueError(
                "Categoria não encontrada."
            )

        cls.validar(dados)

        categoria_codigo = cls.buscar_por_codigo(

            dados["codigo"]

        )

        if categoria_codigo and categoria_codigo["id"] != categoria_id:

            raise ValueError(
                "Já existe outra categoria com este código."
            )

        categoria_nome = cls.buscar_por_nome(

            dados["nome"]

        )

        if categoria_nome and categoria_nome["id"] != categoria_id:

            raise ValueError(
                "Já existe outra categoria com este nome."
            )

        return cls.repository.atualizar(

            categoria_id,

            dados

        )

    ####################################################################
    # EXCLUSÃO
    ####################################################################

    @classmethod
    def excluir(cls, categoria_id):

        categoria = cls.buscar(categoria_id)

        if not categoria:

            raise ValueError(
                "Categoria não encontrada."
            )

        #
        # Sprint futura:
        # Verificar se existem produtos vinculados.
        #

        return cls.repository.excluir(categoria_id)

    ####################################################################
    # DESATIVAÇÃO
    ####################################################################

    @classmethod
    def desativar(cls, categoria_id):

        categoria = cls.buscar(categoria_id)

        if not categoria:

            raise ValueError(
                "Categoria não encontrada."
            )

        return cls.repository.desativar(categoria_id)


    ####################################################################
    # REATIVAÇÃO
    ####################################################################

    @classmethod
    def reativar(cls, categoria_id):

        categoria = cls.buscar(categoria_id)

        if not categoria:

            raise ValueError(
                "Categoria não encontrada."
            )

        return cls.repository.reativar(categoria_id)


    ####################################################################
    # VALIDAÇÕES
    ####################################################################

    @staticmethod
    def validar(dados):

        if not dados.get("codigo"):

            raise ValueError(
                "Código é obrigatório."
            )

        if not dados.get("nome"):

            raise ValueError(
                "Nome é obrigatório."
            )

        if len(dados["codigo"]) > 30:

            raise ValueError(
                "Código deve possuir no máximo 30 caracteres."
            )

        if len(dados["nome"]) > 100:

            raise ValueError(
                "Nome deve possuir no máximo 100 caracteres."
            )

        return True
