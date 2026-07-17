from decimal import Decimal
from decimal import InvalidOperation

from app.clientes.service import ClienteService
from app.contatos.service import ContatoService
from app.parceiros.executivo_service import ParceiroExecutivoService
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.contato_repository import ContatoRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.oportunidade_repository import OportunidadeRepository
from app.repositories.parceiro_executivo_repository import ParceiroExecutivoRepository
from app.repositories.parceiro_repository import ParceiroRepository


STATUS_OPORTUNIDADE = {
    "NOVA": "Nova",
    "QUALIFICACAO": "Qualificação",
    "LEVANTAMENTO": "Levantamento",
    "DIMENSIONAMENTO": "Dimensionamento",
    "PRECIFICACAO": "Precificação",
    "PROPOSTA": "Proposta",
    "NEGOCIACAO": "Negociação",
    "GANHA": "Ganha",
    "PERDIDA": "Perdida",
}


class OportunidadeService:

    repository = OportunidadeRepository

    @classmethod
    def listar(cls, pesquisa=None, status=None, ativo=None, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_status_ativo(ativo)

        oportunidades = cls.repository.listar(
            pesquisa=pesquisa,
            status=status,
            ativo=ativo_normalizado,
            limit=limit,
            offset=offset,
        )
        total = cls.repository.total(
            pesquisa=pesquisa,
            status=status,
            ativo=ativo_normalizado,
        )

        return oportunidades, total

    @classmethod
    def buscar_por_id(cls, oportunidade_id):
        return cls.repository.buscar_por_id(oportunidade_id)

    @classmethod
    def listar_leads(cls):
        return LeadRepository.listar_todos_ativos()

    @classmethod
    def listar_contatos(cls):
        return ContatoService.listar_todos_ativos()

    @classmethod
    def listar_clientes(cls):
        return ClienteService.listar_para_importacao()

    @classmethod
    def listar_parceiros(cls):
        return ParceiroRepository.listar_todos_ativos()

    @classmethod
    def listar_executivos(cls):
        return ParceiroExecutivoService.listar_todos_ativos()

    @classmethod
    def criar(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)
        return cls.repository.inserir(dados)

    @classmethod
    def atualizar(cls, oportunidade_id, dados):
        oportunidade = cls.buscar_por_id(oportunidade_id)

        if not oportunidade:
            raise ValueError("Oportunidade não encontrada.")

        dados = cls.normalizar(dados)
        cls.validar(dados)
        return cls.repository.atualizar(oportunidade_id, dados)

    @classmethod
    def excluir(cls, oportunidade_id):
        return cls.repository.excluir(oportunidade_id)

    @classmethod
    def normalizar(cls, dados):
        dados = dict(dados)
        dados["lead_id"] = cls._normalizar_inteiro(dados.get("lead_id"))
        dados["contato_id"] = cls._normalizar_inteiro(dados.get("contato_id"))
        dados["cliente_id"] = cls._normalizar_inteiro(dados.get("cliente_id"))
        dados["parceiro_id"] = cls._normalizar_inteiro(dados.get("parceiro_id"))
        dados["executivo_responsavel_id"] = cls._normalizar_inteiro(dados.get("executivo_responsavel_id"))
        dados["titulo"] = (dados.get("titulo") or "").strip()
        dados["empresa"] = (dados.get("empresa") or "").strip()
        dados["erp"] = (dados.get("erp") or "").strip()
        dados["quantidade_usuarios"] = cls._normalizar_inteiro(dados.get("quantidade_usuarios"))
        dados["valor_estimado"] = cls._decimal(dados.get("valor_estimado"))
        dados["probabilidade"] = cls._normalizar_inteiro(dados.get("probabilidade"))
        dados["status"] = (dados.get("status") or "NOVA").strip().upper()
        dados["observacoes"] = (dados.get("observacoes") or "").strip()
        dados["ativo"] = str(dados.get("ativo", "1")) == "1"
        return dados

    @classmethod
    def validar(cls, dados):
        if not dados["titulo"]:
            raise ValueError("Título da oportunidade é obrigatório.")

        if dados["status"] not in STATUS_OPORTUNIDADE:
            raise ValueError("Status da oportunidade inválido.")

        if len(dados["titulo"]) > 180:
            raise ValueError("Título da oportunidade deve possuir no máximo 180 caracteres.")

        if dados["empresa"] and len(dados["empresa"]) > 150:
            raise ValueError("Empresa deve possuir no máximo 150 caracteres.")

        if dados["erp"] and len(dados["erp"]) > 120:
            raise ValueError("ERP deve possuir no máximo 120 caracteres.")

        if dados["quantidade_usuarios"] is not None and dados["quantidade_usuarios"] < 0:
            raise ValueError("Quantidade de usuários não pode ser negativa.")

        if dados["probabilidade"] is not None and not 0 <= dados["probabilidade"] <= 100:
            raise ValueError("Probabilidade deve estar entre 0 e 100.")

        if dados["observacoes"] and len(dados["observacoes"]) > 4000:
            raise ValueError("Observações devem possuir no máximo 4000 caracteres.")

        if dados["lead_id"]:
            lead = LeadRepository.buscar_por_id(dados["lead_id"])
            if not lead:
                raise ValueError("Lead vinculado não encontrado.")

        if dados["contato_id"]:
            contato = ContatoRepository.buscar_por_id(dados["contato_id"])
            if not contato:
                raise ValueError("Contato vinculado não encontrado.")

        if dados["cliente_id"]:
            cliente = ClienteRepository.buscar_por_id(dados["cliente_id"])
            if not cliente:
                raise ValueError("Cliente vinculado não encontrado.")

        if dados["parceiro_id"]:
            parceiro = ParceiroRepository.buscar_por_id(dados["parceiro_id"])
            if not parceiro:
                raise ValueError("Parceiro vinculado não encontrado.")

        if dados["executivo_responsavel_id"]:
            executivo = ParceiroExecutivoRepository.buscar_por_id(dados["executivo_responsavel_id"])
            if not executivo:
                raise ValueError("Executivo responsável não encontrado.")

        return True

    @staticmethod
    def _normalizar_inteiro(valor):
        if valor in (None, ""):
            return None
        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalizar_status_ativo(valor):
        if valor in (None, ""):
            return None
        if str(valor) == "1":
            return 1
        if str(valor) == "0":
            return 0
        return None

    @staticmethod
    def _decimal(valor):
        if valor in (None, ""):
            return None
        try:
            valor = str(valor).replace('.', '').replace(',', '.').strip()
            return Decimal(valor)
        except InvalidOperation:
            raise ValueError("Valor estimado inválido.")
