"""
Service de Produtos do Catálogo Técnico.

Responsável pelas regras de negócio.

Não conhece banco de dados.
Não conhece Flask.
Não conhece HTML.

Toda persistência é feita pelo ProdutoRepository.
"""

from app.catalogo.produtos.repository import ProdutoRepository


class ProdutoService:

    repository = ProdutoRepository

    TIPOS_RECURSO = (
        "VM",
        "LXC",
        "CPU",
        "RAM",
        "DISCO",
        "STORAGE",
        "BACKUP",
        "LICENCA",
        "SERVICO",
        "OUTRO",
    )

    ####################################################################
    # CONSULTAS
    ####################################################################

    @classmethod
    def listar(cls):

        return cls.repository.listar()

    @classmethod
    def buscar(cls, produto_id):

        return cls.repository.buscar(produto_id)

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

        dados = cls.normalizar(dados)

        cls.validar(dados)

        if cls.repository.existe(dados["codigo"]):

            raise ValueError(
                "Já existe um produto com este código."
            )

        produto = cls.buscar_por_nome(dados["nome"])

        if produto:

            raise ValueError(
                "Já existe um produto com este nome."
            )

        return cls.repository.inserir(dados)

    ####################################################################
    # ALTERAÇÃO
    ####################################################################

    @classmethod
    def atualizar(cls, produto_id, dados):

        produto = cls.buscar(produto_id)

        if not produto:

            raise ValueError(
                "Produto não encontrado."
            )

        dados = cls.normalizar(dados)

        cls.validar(dados)

        produto_codigo = cls.buscar_por_codigo(
            dados["codigo"]
        )

        if produto_codigo and produto_codigo["id"] != produto_id:

            raise ValueError(
                "Já existe outro produto com este código."
            )

        produto_nome = cls.buscar_por_nome(
            dados["nome"]
        )

        if produto_nome and produto_nome["id"] != produto_id:

            raise ValueError(
                "Já existe outro produto com este nome."
            )

        return cls.repository.atualizar(
            produto_id,
            dados
        )

    ####################################################################
    # DESATIVAÇÃO
    ####################################################################

    @classmethod
    def desativar(cls, produto_id):

        produto = cls.buscar(produto_id)

        if not produto:

            raise ValueError(
                "Produto não encontrado."
            )

        return cls.repository.desativar(produto_id)

    ####################################################################
    # REATIVAÇÃO
    ####################################################################

    @classmethod
    def reativar(cls, produto_id):

        produto = cls.buscar(produto_id)

        if not produto:

            raise ValueError(
                "Produto não encontrado."
            )

        return cls.repository.reativar(produto_id)

    ####################################################################
    # LISTAS AUXILIARES
    ####################################################################

    @classmethod
    def listar_categorias(cls):

        return cls.repository.listar_categorias()

    @classmethod
    def listar_parceiros(cls):

        return cls.repository.listar_parceiros()

    @classmethod
    def listar_tipos_recurso(cls):

        return cls.repository.listar_tipos_recurso()

    ####################################################################
    # NORMALIZAÇÃO
    ####################################################################

    @classmethod
    def normalizar(cls, dados):

        dados = dict(dados)

        dados["categoria_id"] = int(dados["categoria_id"])
        dados["parceiro_id"] = cls._normalizar_inteiro(dados.get("parceiro_id"))

        dados["codigo"] = dados["codigo"].strip().upper()

        dados["nome"] = dados["nome"].strip()

        dados["descricao"] = (
            dados.get("descricao") or ""
        ).strip()

        dados["codigo_externo"] = (
            dados.get("codigo_externo") or ""
        ).strip()

        dados["unidade"] = dados["unidade"].strip().upper()

        dados["tipo_recurso"] = (
            dados.get("tipo_recurso") or "SERVICO"
        ).strip().upper()

        dados["origem"] = (
            dados.get("origem") or "MANUAL"
        ).strip().upper()

        dados["valor_venda"] = float(
            str(
                dados.get("valor_venda", 0)
            ).replace(",", ".")
        )

        dados["valor_custo"] = float(
            str(
                dados.get("valor_custo", 0)
            ).replace(",", ".")
        )

        dados["ativo"] = bool(
            dados.get("ativo", True)
        )

        return dados

    ####################################################################
    # VALIDAÇÕES
    ####################################################################

    @classmethod
    def validar(cls, dados):

        if not dados["categoria_id"]:

            raise ValueError(
                "Categoria é obrigatória."
            )

        if not dados["codigo"]:

            raise ValueError(
                "Código é obrigatório."
            )

        if not dados["nome"]:

            raise ValueError(
                "Nome é obrigatório."
            )

        if not dados["unidade"]:

            raise ValueError(
                "Unidade é obrigatória."
            )

        if dados["tipo_recurso"] not in cls.TIPOS_RECURSO:

            raise ValueError(
                "Tipo de recurso inválido."
            )

        if len(dados["codigo"]) > 30:

            raise ValueError(
                "Código deve possuir no máximo 30 caracteres."
            )

        if len(dados["nome"]) > 150:

            raise ValueError(
                "Nome deve possuir no máximo 150 caracteres."
            )

        return True

    @staticmethod
    def _normalizar_inteiro(valor, default=None):
        if valor in (None, ""):
            return default

        try:
            return int(valor)
        except (TypeError, ValueError):
            return default
