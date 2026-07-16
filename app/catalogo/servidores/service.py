"""Regras de negocio de Servidores do Catalogo Tecnico."""

from app.catalogo.faixas.service import ProdutoFaixaService
from app.catalogo.modelos.service import ProdutoModeloService
from app.catalogo.produtos.service import ProdutoService
from app.catalogo.servidores.repository import ProdutoServidorRepository


class ProdutoServidorService:
    """Coordena validacoes e persistencia de produto_servidores."""

    repository = ProdutoServidorRepository
    TIPOS_PADRAO = [
        {"codigo": "BANCO", "nome": "Banco"},
        {"codigo": "APLICACAO", "nome": "Aplicacao"},
        {"codigo": "SM", "nome": "Session Manager"},
        {"codigo": "STORE", "nome": "Store"},
        {"codigo": "ACESSO", "nome": "Acesso"},
        {"codigo": "TERMINAL", "nome": "Terminal"},
        {"codigo": "WEB", "nome": "Web"},
        {"codigo": "OUTRO", "nome": "Outro"},
    ]

    @classmethod
    def listar(cls):
        return cls.repository.listar()

    @classmethod
    def buscar(cls, servidor_id):
        return cls.repository.buscar(servidor_id)

    @classmethod
    def buscar_por_codigo(cls, faixa_id, codigo):
        return cls.repository.buscar_por_codigo(faixa_id, codigo)

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
    def listar_faixas(cls, produto_id=None, modelo_id=None):
        return cls.repository.listar_faixas(produto_id, modelo_id)

    @classmethod
    def listar_tipos(cls):
        tipos = cls.repository.listar_tipos()
        return tipos or cls.TIPOS_PADRAO

    @classmethod
    def criar(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)
        cls.validar_unicidade(dados)

        return cls.repository.inserir(dados)

    @classmethod
    def atualizar(cls, servidor_id, dados):
        servidor = cls.buscar(servidor_id)

        if not servidor:
            raise ValueError("Servidor nao encontrado.")

        dados = cls.normalizar(dados)
        cls.validar(dados)
        cls.validar_unicidade(dados, servidor_id)

        return cls.repository.atualizar(servidor_id, dados)

    @classmethod
    def desativar(cls, servidor_id):
        servidor = cls.buscar(servidor_id)

        if not servidor:
            raise ValueError("Servidor nao encontrado.")

        return cls.repository.desativar(servidor_id)

    @classmethod
    def reativar(cls, servidor_id):
        servidor = cls.buscar(servidor_id)

        if not servidor:
            raise ValueError("Servidor nao encontrado.")

        return cls.repository.reativar(servidor_id)

    @classmethod
    def normalizar(cls, dados):
        dados = dict(dados)

        dados["produto"] = (dados.get("produto") or "").strip()
        dados["modelo"] = (dados.get("modelo") or "").strip()
        dados["codigo"] = (dados.get("codigo") or "").strip().upper()
        dados["nome"] = (dados.get("nome") or "").strip()
        dados["tipo"] = (dados.get("tipo") or "").strip().upper()
        dados["sistema_operacional"] = (
            dados.get("sistema_operacional") or ""
        ).strip()
        dados["observacoes"] = (dados.get("observacoes") or "").strip()

        dados["produto_id"] = cls._normalizar_inteiro(dados.get("produto_id"))
        dados["modelo_id"] = cls._normalizar_inteiro(dados.get("modelo_id"))
        dados["faixa_id"] = cls._normalizar_inteiro(dados.get("faixa_id"))
        dados["ordem"] = cls._normalizar_inteiro(dados.get("ordem"), default=0)
        dados["ativo"] = bool(dados.get("ativo", True))

        cls.resolver_relacionamentos(dados)

        return dados

    @classmethod
    def validar(cls, dados):
        if not dados["produto_id"]:
            raise ValueError("Produto e obrigatorio.")

        if not dados["modelo_id"]:
            raise ValueError("Modelo e obrigatorio.")

        if not dados["faixa_id"]:
            raise ValueError("Faixa e obrigatoria.")

        if not dados["codigo"]:
            raise ValueError("Codigo e obrigatorio.")

        if not dados["nome"]:
            raise ValueError("Nome e obrigatorio.")

        if not dados["tipo"]:
            raise ValueError("Tipo e obrigatorio.")

        if dados["ordem"] is None or dados["ordem"] < 0:
            raise ValueError("Ordem nao pode ser negativa.")

        if len(dados["codigo"]) > 30:
            raise ValueError("Codigo deve possuir no maximo 30 caracteres.")

        if len(dados["nome"]) > 100:
            raise ValueError("Nome deve possuir no maximo 100 caracteres.")

        if len(dados["sistema_operacional"]) > 100:
            raise ValueError(
                "Sistema operacional deve possuir no maximo 100 caracteres."
            )

        tipos_validos = {tipo["codigo"] for tipo in cls.listar_tipos()}
        if dados["tipo"] not in tipos_validos:
            raise ValueError("Tipo de servidor invalido.")

        modelo = ProdutoModeloService.buscar(dados["modelo_id"])
        if not modelo:
            raise ValueError("Modelo nao encontrado.")

        if modelo["produto_id"] != dados["produto_id"]:
            raise ValueError("Modelo informado nao pertence ao produto.")

        faixa = ProdutoFaixaService.buscar(dados["faixa_id"])
        if not faixa:
            raise ValueError("Faixa nao encontrada.")

        if faixa["modelo_id"] != dados["modelo_id"]:
            raise ValueError("Faixa informada nao pertence ao modelo.")

        return True

    @classmethod
    def validar_unicidade(cls, dados, servidor_id=None):
        servidor_codigo = cls.buscar_por_codigo(
            dados["faixa_id"],
            dados["codigo"],
        )

        if servidor_codigo and servidor_codigo["id"] != servidor_id:
            raise ValueError(
                "Ja existe um servidor com este codigo para a faixa."
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

        if dados["faixa_id"]:
            faixa = ProdutoFaixaService.buscar(dados["faixa_id"])

            if not faixa:
                raise ValueError("Faixa nao encontrada.")

            if not dados["modelo_id"]:
                dados["modelo_id"] = faixa["modelo_id"]

            if not dados["produto_id"]:
                dados["produto_id"] = faixa["produto_id"]

    @staticmethod
    def _normalizar_inteiro(valor, default=None):
        if valor in (None, ""):
            return default

        try:
            return int(valor)
        except (TypeError, ValueError):
            return default
