"""Regras de negocio de Faixas do Catalogo Tecnico."""

from app.catalogo.faixas.repository import ProdutoFaixaRepository
from app.catalogo.modelos.service import ProdutoModeloService
from app.catalogo.produtos.service import ProdutoService


class ProdutoFaixaService:
    """Coordena validacoes e persistencia de produto_faixas."""

    repository = ProdutoFaixaRepository

    @classmethod
    def listar(cls):
        return cls.repository.listar()

    @classmethod
    def buscar(cls, faixa_id):
        return cls.repository.buscar(faixa_id)

    @classmethod
    def buscar_por_intervalo(cls, modelo_id, usuarios_inicio, usuarios_fim):
        return cls.repository.buscar_por_intervalo(
            modelo_id,
            usuarios_inicio,
            usuarios_fim,
        )

    @classmethod
    def buscar_por_codigo(cls, modelo_id, codigo):
        return cls.repository.buscar_por_codigo(modelo_id, codigo)

    @classmethod
    def contar(cls):
        return cls.repository.contar()

    @classmethod
    def listar_produtos(cls):
        return cls.repository.listar_produtos()

    @classmethod
    def listar_modelos(cls, produto_id=None):
        return cls.repository.listar_modelos(produto_id)

    @classmethod
    def criar(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)
        cls.validar_unicidade(dados)

        return cls.repository.inserir(dados)

    @classmethod
    def atualizar(cls, faixa_id, dados):
        faixa = cls.buscar(faixa_id)

        if not faixa:
            raise ValueError("Faixa nao encontrada.")

        dados = cls.normalizar(dados)
        cls.validar(dados)
        cls.validar_unicidade(dados, faixa_id)

        return cls.repository.atualizar(faixa_id, dados)

    @classmethod
    def desativar(cls, faixa_id):
        faixa = cls.buscar(faixa_id)

        if not faixa:
            raise ValueError("Faixa nao encontrada.")

        return cls.repository.desativar(faixa_id)

    @classmethod
    def reativar(cls, faixa_id):
        faixa = cls.buscar(faixa_id)

        if not faixa:
            raise ValueError("Faixa nao encontrada.")

        return cls.repository.reativar(faixa_id)

    @classmethod
    def normalizar(cls, dados):
        dados = dict(dados)

        dados["produto"] = (dados.get("produto") or "").strip()
        dados["modelo"] = (dados.get("modelo") or "").strip()
        dados["codigo"] = (dados.get("codigo") or "").strip().upper()
        dados["nome"] = (dados.get("nome") or "").strip()
        dados["descricao"] = (dados.get("descricao") or "").strip()

        dados["produto_id"] = cls._normalizar_inteiro(dados.get("produto_id"))
        dados["modelo_id"] = cls._normalizar_inteiro(dados.get("modelo_id"))
        dados["usuarios_inicio"] = cls._normalizar_inteiro(dados.get("usuarios_inicio"))
        dados["usuarios_fim"] = cls._normalizar_inteiro(dados.get("usuarios_fim"))
        dados["ordem"] = cls._normalizar_inteiro(dados.get("ordem"), default=0)
        dados["permite_upgrade_manual"] = bool(
            dados.get("permite_upgrade_manual", True)
        )
        dados["ativo"] = bool(dados.get("ativo", True))

        cls.resolver_relacionamentos(dados)

        return dados

    @classmethod
    def validar(cls, dados):
        if not dados["produto_id"]:
            raise ValueError("Produto e obrigatorio.")

        if not dados["modelo_id"]:
            raise ValueError("Modelo e obrigatorio.")

        if not dados["codigo"]:
            raise ValueError("Codigo e obrigatorio.")

        if not dados["nome"]:
            raise ValueError("Nome e obrigatorio.")

        if dados["usuarios_inicio"] is None:
            raise ValueError("Usuario inicial da faixa e obrigatorio.")

        if dados["usuarios_fim"] is None:
            raise ValueError("Usuario final da faixa e obrigatorio.")

        if dados["usuarios_inicio"] < 0:
            raise ValueError("Usuario inicial nao pode ser negativo.")

        if dados["usuarios_fim"] < dados["usuarios_inicio"]:
            raise ValueError("Usuario final nao pode ser menor que o inicial.")

        if dados["ordem"] is None or dados["ordem"] < 0:
            raise ValueError("Ordem nao pode ser negativa.")

        if len(dados["codigo"]) > 30:
            raise ValueError("Codigo deve possuir no maximo 30 caracteres.")

        if len(dados["nome"]) > 100:
            raise ValueError("Nome deve possuir no maximo 100 caracteres.")

        modelo = ProdutoModeloService.buscar(dados["modelo_id"])

        if not modelo:
            raise ValueError("Modelo nao encontrado.")

        if modelo["produto_id"] != dados["produto_id"]:
            raise ValueError("Modelo informado nao pertence ao produto.")

        return True

    @classmethod
    def validar_unicidade(cls, dados, faixa_id=None):
        faixa_intervalo = cls.buscar_por_intervalo(
            dados["modelo_id"],
            dados["usuarios_inicio"],
            dados["usuarios_fim"],
        )

        if faixa_intervalo and faixa_intervalo["id"] != faixa_id:
            raise ValueError(
                "Ja existe uma faixa com este intervalo para o modelo."
            )

        faixa_codigo = cls.buscar_por_codigo(
            dados["modelo_id"],
            dados["codigo"],
        )

        if faixa_codigo and faixa_codigo["id"] != faixa_id:
            raise ValueError(
                "Ja existe uma faixa com este codigo para o modelo."
            )

    @classmethod
    def resolver_relacionamentos(cls, dados):
        if not dados["produto_id"] and dados["produto"]:
            produto = ProdutoService.buscar_por_nome(dados["produto"])

            if not produto:
                raise ValueError("Produto nao encontrado.")

            dados["produto_id"] = produto["id"]

        if not dados["modelo_id"] and dados["modelo"] and dados["produto_id"]:
            modelo = ProdutoModeloService.buscar_por_nome(
                dados["produto_id"],
                dados["modelo"],
            )

            if not modelo:
                raise ValueError("Modelo nao encontrado.")

            dados["modelo_id"] = modelo["id"]

        if dados["modelo_id"]:
            modelo = ProdutoModeloService.buscar(dados["modelo_id"])

            if not modelo:
                raise ValueError("Modelo nao encontrado.")

            if not dados["produto_id"]:
                dados["produto_id"] = modelo["produto_id"]

    @staticmethod
    def _normalizar_inteiro(valor, default=None):
        if valor in (None, ""):
            return default

        try:
            return int(valor)
        except (TypeError, ValueError):
            return default
