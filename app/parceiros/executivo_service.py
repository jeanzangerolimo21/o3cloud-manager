from app.repositories.parceiro_executivo_repository import ParceiroExecutivoRepository
from app.repositories.parceiro_repository import ParceiroRepository
from app.utils.telefone import formatar_telefone


class ParceiroExecutivoService:

    repository = ParceiroExecutivoRepository

    @classmethod
    def listar(cls, pesquisa=None, ativo=None, parceiro_id=None, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_status(ativo)

        executivos = cls.repository.listar(
            pesquisa=pesquisa,
            ativo=ativo_normalizado,
            parceiro_id=parceiro_id,
            limit=limit,
            offset=offset,
        )
        total = cls.repository.total(
            pesquisa=pesquisa,
            ativo=ativo_normalizado,
            parceiro_id=parceiro_id,
        )

        return [cls._formatar_telefone(executivo) for executivo in executivos], total

    @classmethod
    def listar_todos_ativos(cls):
        executivos = cls.repository.listar_todos_ativos()
        return [cls._formatar_telefone(executivo) for executivo in executivos]

    @classmethod
    def buscar_por_id(cls, executivo_id):
        executivo = cls.repository.buscar_por_id(executivo_id)
        return cls._formatar_telefone(executivo)

    @classmethod
    def contar_por_parceiro(cls, parceiro_id):
        return cls.repository.contar_por_parceiro(parceiro_id)

    @classmethod
    def listar_parceiros(cls):
        return ParceiroRepository.listar_todos_ativos()

    @classmethod
    def criar(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)
        return cls.repository.inserir(dados)

    @classmethod
    def atualizar(cls, executivo_id, dados):
        executivo = cls.buscar_por_id(executivo_id)

        if not executivo:
            raise ValueError("Executivo não encontrado.")

        dados = cls.normalizar(dados)
        cls.validar(dados)
        return cls.repository.atualizar(executivo_id, dados)

    @classmethod
    def normalizar(cls, dados):
        dados = dict(dados)
        dados["nome"] = (dados.get("nome") or "").strip()
        dados["email"] = (dados.get("email") or "").strip().lower()
        dados["telefone"] = formatar_telefone(dados.get("telefone"))
        dados["chave_pix"] = (dados.get("chave_pix") or "").strip()
        dados["informacoes_pagamento"] = ((dados.get("informacoes_pagamento") or "").strip())
        dados["parceiro_id"] = cls._normalizar_inteiro(dados.get("parceiro_id"))
        dados["ativo"] = str(dados.get("ativo", "1")) == "1"
        return dados

    @classmethod
    def validar(cls, dados):
        if not dados["nome"]:
            raise ValueError("Nome completo é obrigatório.")

        if len(dados["nome"]) > 150:
            raise ValueError("Nome completo deve possuir no máximo 150 caracteres.")

        if dados["email"] and len(dados["email"]) > 150:
            raise ValueError("E-mail deve possuir no máximo 150 caracteres.")

        if dados["telefone"] and len(dados["telefone"]) > 30:
            raise ValueError("WhatsApp deve possuir no máximo 30 caracteres.")

        if dados["chave_pix"] and len(dados["chave_pix"]) > 120:
            raise ValueError("Chave Pix deve possuir no máximo 120 caracteres.")

        if dados["informacoes_pagamento"] and len(dados["informacoes_pagamento"]) > 2000:
            raise ValueError("Informações de pagamento devem possuir no máximo 2000 caracteres.")

        if dados["parceiro_id"]:
            parceiro = ParceiroRepository.buscar_por_id(dados["parceiro_id"])
            if not parceiro:
                raise ValueError("Parceiro vinculado não encontrado.")

        return True

    @staticmethod
    def _normalizar_status(valor):
        if valor in (None, ""):
            return None
        if str(valor) == "1":
            return 1
        if str(valor) == "0":
            return 0
        return None

    @staticmethod
    def _normalizar_inteiro(valor):
        if valor in (None, ""):
            return None
        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _formatar_telefone(executivo):
        if not executivo:
            return executivo

        executivo = dict(executivo)
        executivo["telefone"] = formatar_telefone(executivo.get("telefone"))
        return executivo
