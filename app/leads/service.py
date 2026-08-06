from app.parceiros.executivo_service import ParceiroExecutivoService
from app.repositories.lead_repository import LeadRepository
from app.repositories.parceiro_executivo_repository import ParceiroExecutivoRepository
from app.repositories.parceiro_repository import ParceiroRepository
from app.utils.telefone import formatar_telefone


STATUS_LEAD = {
    "NOVO": "Novo",
    "QUALIFICACAO": "Qualificação",
    "CONTATO_REALIZADO": "Contato Realizado",
    "PROPOSTA": "Proposta",
    "GANHO": "Ganho",
    "PERDIDO": "Perdido",
}


ORIGEM_LEAD = {
    "SITE": "Site",
    "INDICACAO": "Indicação",
    "PARCEIRO": "Parceiro",
    "EVENTO": "Evento",
    "OUTBOUND": "Outbound",
    "OUTRO": "Outro",
}


class LeadService:

    repository = LeadRepository

    @classmethod
    def listar(cls, pesquisa=None, status=None, origem=None, ativo=None, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_status_ativo(ativo)

        leads = cls.repository.listar(
            pesquisa=pesquisa,
            status=status,
            origem=origem,
            ativo=ativo_normalizado,
            limit=limit,
            offset=offset,
        )
        total = cls.repository.total(
            pesquisa=pesquisa,
            status=status,
            origem=origem,
            ativo=ativo_normalizado,
        )

        return [cls._formatar_lead(lead) for lead in leads], total

    @classmethod
    def buscar_por_id(cls, lead_id):
        lead = cls.repository.buscar_por_id(lead_id)
        return cls._formatar_lead(lead)

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
    def atualizar(cls, lead_id, dados):
        lead = cls.buscar_por_id(lead_id)

        if not lead:
            raise ValueError("Lead não encontrado.")

        dados = cls.normalizar(dados)
        cls.validar(dados)
        return cls.repository.atualizar(lead_id, dados)

    @classmethod
    def excluir(cls, lead_id):
        return cls.repository.excluir(lead_id)

    @classmethod
    def excluir_em_massa(cls, lead_ids):
        return cls.repository.excluir_em_massa(lead_ids)

    @classmethod
    def normalizar(cls, dados):
        dados = dict(dados)
        dados["empresa"] = (dados.get("empresa") or "").strip()
        dados["nome_contato"] = (dados.get("nome_contato") or "").strip()
        dados["cargo"] = (dados.get("cargo") or "").strip()
        dados["email"] = (dados.get("email") or "").strip().lower()
        dados["telefone"] = formatar_telefone(dados.get("telefone"))
        dados["origem"] = (dados.get("origem") or "OUTRO").strip().upper()
        dados["interesse"] = (dados.get("interesse") or "").strip()
        dados["status"] = (dados.get("status") or "NOVO").strip().upper()
        dados["cidade"] = (dados.get("cidade") or "").strip()
        dados["uf"] = (dados.get("uf") or "").strip().upper()[:2]
        dados["observacoes"] = (dados.get("observacoes") or "").strip()
        dados["parceiro_id"] = cls._normalizar_inteiro(dados.get("parceiro_id"))
        dados["executivo_responsavel_id"] = cls._normalizar_inteiro(dados.get("executivo_responsavel_id"))
        dados["ativo"] = str(dados.get("ativo", "1")) == "1"
        return dados

    @classmethod
    def validar(cls, dados):
        if not dados["empresa"]:
            raise ValueError("Empresa é obrigatória.")

        if not dados["nome_contato"]:
            raise ValueError("Nome do contato é obrigatório.")

        if dados["origem"] not in ORIGEM_LEAD:
            raise ValueError("Origem do lead inválida.")

        if dados["status"] not in STATUS_LEAD:
            raise ValueError("Status do lead inválido.")

        if dados["empresa"] and len(dados["empresa"]) > 150:
            raise ValueError("Empresa deve possuir no máximo 150 caracteres.")

        if dados["nome_contato"] and len(dados["nome_contato"]) > 150:
            raise ValueError("Nome do contato deve possuir no máximo 150 caracteres.")

        if dados["cargo"] and len(dados["cargo"]) > 120:
            raise ValueError("Cargo deve possuir no máximo 120 caracteres.")

        if dados["email"] and len(dados["email"]) > 150:
            raise ValueError("E-mail deve possuir no máximo 150 caracteres.")

        if dados["telefone"] and len(dados["telefone"]) > 30:
            raise ValueError("Telefone deve possuir no máximo 30 caracteres.")

        if dados["interesse"] and len(dados["interesse"]) > 200:
            raise ValueError("Interesse deve possuir no máximo 200 caracteres.")

        if dados["cidade"] and len(dados["cidade"]) > 120:
            raise ValueError("Cidade deve possuir no máximo 120 caracteres.")

        if dados["uf"] and len(dados["uf"]) != 2:
            raise ValueError("UF deve possuir 2 caracteres.")

        if dados["observacoes"] and len(dados["observacoes"]) > 4000:
            raise ValueError("Observações devem possuir no máximo 4000 caracteres.")

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
    def _formatar_lead(lead):
        if not lead:
            return lead

        lead = dict(lead)
        lead["telefone"] = formatar_telefone(lead.get("telefone"))
        return lead
