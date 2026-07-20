from app.parceiros.executivo_service import ParceiroExecutivoService
from app.repositories.contato_repository import ContatoRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.parceiro_executivo_repository import ParceiroExecutivoRepository
from app.repositories.parceiro_repository import ParceiroRepository
from app.utils.telefone import formatar_telefone


TIPO_CONTATO = {
    "COMERCIAL": "Comercial",
    "DECISOR": "Decisor",
    "FINANCEIRO": "Financeiro",
    "TECNICO": "Técnico",
    "USUARIO_CHAVE": "Usuário Chave",
    "OUTRO": "Outro",
}


CANAL_PREFERIDO = {
    "WHATSAPP": "WhatsApp",
    "EMAIL": "E-mail",
    "TELEFONE": "Telefone",
    "REUNIAO": "Reunião",
    "OUTRO": "Outro",
}


class ContatoService:

    repository = ContatoRepository

    @classmethod
    def listar(cls, pesquisa=None, tipo_contato=None, ativo=None, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        ativo_normalizado = cls._normalizar_status_ativo(ativo)

        contatos = cls.repository.listar(
            pesquisa=pesquisa,
            tipo_contato=tipo_contato,
            ativo=ativo_normalizado,
            limit=limit,
            offset=offset,
        )
        total = cls.repository.total(
            pesquisa=pesquisa,
            tipo_contato=tipo_contato,
            ativo=ativo_normalizado,
        )

        return [cls._formatar_contato(contato) for contato in contatos], total

    @classmethod
    def buscar_por_id(cls, contato_id):
        contato = cls.repository.buscar_por_id(contato_id)
        return cls._formatar_contato(contato)

    @classmethod
    def listar_parceiros(cls):
        return ParceiroRepository.listar_todos_ativos()

    @classmethod
    def listar_executivos(cls):
        return ParceiroExecutivoService.listar_todos_ativos()

    @classmethod
    def listar_leads(cls):
        return LeadRepository.listar_todos_ativos()

    @classmethod
    def listar_todos_ativos(cls):
        contatos = cls.repository.listar_todos_ativos()
        return [cls._formatar_contato(contato) for contato in contatos]

    @classmethod
    def criar(cls, dados):
        dados = cls.normalizar(dados)
        cls.validar(dados)
        return cls.repository.inserir(dados)

    @classmethod
    def atualizar(cls, contato_id, dados):
        contato = cls.buscar_por_id(contato_id)

        if not contato:
            raise ValueError("Contato não encontrado.")

        dados = cls.normalizar(dados)
        cls.validar(dados)
        return cls.repository.atualizar(contato_id, dados)

    @classmethod
    def excluir(cls, contato_id):
        return cls.repository.excluir(contato_id)

    @classmethod
    def normalizar(cls, dados):
        dados = dict(dados)
        dados["lead_id"] = cls._normalizar_inteiro(dados.get("lead_id"))
        dados["parceiro_id"] = cls._normalizar_inteiro(dados.get("parceiro_id"))
        dados["executivo_responsavel_id"] = cls._normalizar_inteiro(dados.get("executivo_responsavel_id"))
        dados["empresa"] = (dados.get("empresa") or "").strip()
        dados["nome"] = (dados.get("nome") or "").strip()
        dados["cargo"] = (dados.get("cargo") or "").strip()
        dados["cpf"] = cls._formatar_cpf(dados.get("cpf"))
        dados["email"] = (dados.get("email") or "").strip().lower()
        dados["telefone"] = formatar_telefone(dados.get("telefone"))
        dados["whatsapp"] = formatar_telefone(dados.get("whatsapp"))
        dados["tipo_contato"] = (dados.get("tipo_contato") or "COMERCIAL").strip().upper()
        dados["canal_preferido"] = (dados.get("canal_preferido") or "WHATSAPP").strip().upper()
        dados["cidade"] = (dados.get("cidade") or "").strip()
        dados["uf"] = (dados.get("uf") or "").strip().upper()[:2]
        dados["observacoes"] = (dados.get("observacoes") or "").strip()
        dados["ativo"] = str(dados.get("ativo", "1")) == "1"
        return dados

    @classmethod
    def validar(cls, dados):
        if not dados["nome"]:
            raise ValueError("Nome do contato é obrigatório.")

        if dados["tipo_contato"] not in TIPO_CONTATO:
            raise ValueError("Tipo de contato inválido.")

        if dados["canal_preferido"] not in CANAL_PREFERIDO:
            raise ValueError("Canal preferido inválido.")

        if dados["empresa"] and len(dados["empresa"]) > 150:
            raise ValueError("Empresa deve possuir no máximo 150 caracteres.")

        if len(dados["nome"]) > 150:
            raise ValueError("Nome do contato deve possuir no máximo 150 caracteres.")

        if dados["cargo"] and len(dados["cargo"]) > 120:
            raise ValueError("Cargo deve possuir no máximo 120 caracteres.")

        if dados["cpf"] and len(dados["cpf"]) > 20:
            raise ValueError("CPF deve possuir no máximo 20 caracteres.")

        if dados["email"] and len(dados["email"]) > 150:
            raise ValueError("E-mail deve possuir no máximo 150 caracteres.")

        if dados["telefone"] and len(dados["telefone"]) > 30:
            raise ValueError("Telefone deve possuir no máximo 30 caracteres.")

        if dados["whatsapp"] and len(dados["whatsapp"]) > 30:
            raise ValueError("WhatsApp deve possuir no máximo 30 caracteres.")

        if dados["cidade"] and len(dados["cidade"]) > 120:
            raise ValueError("Cidade deve possuir no máximo 120 caracteres.")

        if dados["uf"] and len(dados["uf"]) != 2:
            raise ValueError("UF deve possuir 2 caracteres.")

        if dados["observacoes"] and len(dados["observacoes"]) > 4000:
            raise ValueError("Observações devem possuir no máximo 4000 caracteres.")

        if dados["lead_id"]:
            lead = LeadRepository.buscar_por_id(dados["lead_id"])
            if not lead:
                raise ValueError("Lead vinculado não encontrado.")

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
    def _formatar_cpf(valor):
        texto = (valor or "").strip()
        digitos = "".join(char for char in texto if char.isdigit())
        if not digitos:
            return ""
        if len(digitos) == 11:
            return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
        return texto

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
    def _formatar_contato(contato):
        if not contato:
            return contato

        contato = dict(contato)
        contato["telefone"] = formatar_telefone(contato.get("telefone"))
        contato["whatsapp"] = formatar_telefone(contato.get("whatsapp"))
        contato["cpf"] = ContatoService._formatar_cpf(contato.get("cpf"))
        return contato
