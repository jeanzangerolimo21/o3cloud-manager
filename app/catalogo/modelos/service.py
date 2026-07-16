"""Regras de negócio de Modelos do Catálogo Técnico."""

from app.catalogo.modelos.repository import ProdutoModeloRepository


class ProdutoModeloService:
    """Coordena validações e persistência de produto_modelos."""

    repository = ProdutoModeloRepository

    @classmethod
    def listar(cls):
        return cls.repository.listar()

    @classmethod
    def buscar(cls, modelo_id):
        return cls.repository.buscar(modelo_id)

    @classmethod
    def buscar_por_codigo(cls, produto_id, codigo):
        return cls.repository.buscar_por_codigo(produto_id, codigo)

    @classmethod
    def buscar_por_nome(cls, produto_id, nome):
        return cls.repository.buscar_por_nome(produto_id, nome)

    @classmethod
    def contar(cls):
        return cls.repository.contar()

    @classmethod
    def listar_produtos(cls):
        return cls.repository.listar_produtos()

    @classmethod
    def criar(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)
        cls.validar_unicidade(dados)
        cls.validar_modelo_padrao(dados)

        return cls.repository.inserir(dados)

    @classmethod
    def atualizar(cls, modelo_id, dados):
        modelo = cls.buscar(modelo_id)

        if not modelo:
            raise ValueError("Modelo não encontrado.")

        dados = cls.normalizar(dados)
        cls.validar(dados)
        cls.validar_unicidade(dados, modelo_id)
        cls.validar_modelo_padrao(dados, modelo_id)

        return cls.repository.atualizar(modelo_id, dados)

    @classmethod
    def desativar(cls, modelo_id):
        modelo = cls.buscar(modelo_id)

        if not modelo:
            raise ValueError("Modelo não encontrado.")

        return cls.repository.desativar(modelo_id)

    @classmethod
    def reativar(cls, modelo_id):
        modelo = cls.buscar(modelo_id)

        if not modelo:
            raise ValueError("Modelo não encontrado.")

        return cls.repository.reativar(modelo_id)

    @classmethod
    def normalizar(cls, dados):
        dados = dict(dados)

        try:
            dados["produto_id"] = int(dados.get("produto_id"))
        except (TypeError, ValueError):
            raise ValueError("Produto é obrigatório.")

        try:
            dados["ordem"] = int(dados.get("ordem") or 0)
        except (TypeError, ValueError):
            raise ValueError("Ordem deve ser um número inteiro.")

        dados["codigo"] = (dados.get("codigo") or "").strip().upper()
        dados["nome"] = (dados.get("nome") or "").strip()
        dados["descricao"] = (dados.get("descricao") or "").strip()
        dados["versao"] = (dados.get("versao") or "").strip()
        dados["padrao"] = bool(dados.get("padrao", False))
        dados["ativo"] = bool(dados.get("ativo", True))

        return dados

    @classmethod
    def validar(cls, dados):
        if not dados["produto_id"]:
            raise ValueError("Produto é obrigatório.")

        if not dados["codigo"]:
            raise ValueError("Código é obrigatório.")

        if not dados["nome"]:
            raise ValueError("Nome é obrigatório.")

        if dados["ordem"] < 0:
            raise ValueError("Ordem não pode ser negativa.")

        if len(dados["codigo"]) > 30:
            raise ValueError("Código deve possuir no máximo 30 caracteres.")

        if len(dados["nome"]) > 100:
            raise ValueError("Nome deve possuir no máximo 100 caracteres.")

        if len(dados["versao"]) > 20:
            raise ValueError("Versão deve possuir no máximo 20 caracteres.")

        return True

    @classmethod
    def validar_unicidade(cls, dados, modelo_id=None):
        modelo_codigo = cls.buscar_por_codigo(
            dados["produto_id"],
            dados["codigo"],
        )

        if modelo_codigo and modelo_codigo["id"] != modelo_id:
            raise ValueError("Já existe um modelo com este código para o produto.")

        modelo_nome = cls.buscar_por_nome(
            dados["produto_id"],
            dados["nome"],
        )

        if modelo_nome and modelo_nome["id"] != modelo_id:
            raise ValueError("Já existe um modelo com este nome para o produto.")

    @classmethod
    def validar_modelo_padrao(cls, dados, modelo_id=None):
        if not dados["padrao"]:
            return

        for modelo in cls.listar():
            if (
                modelo["produto_id"] == dados["produto_id"]
                and modelo["padrao"]
                and modelo["id"] != modelo_id
            ):
                raise ValueError("Já existe um modelo padrão para este produto.")
