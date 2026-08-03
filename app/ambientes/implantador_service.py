from app.repositories.implantador_repository import ImplantadorRepository
from app.utils.telefone import formatar_telefone


class ImplantadorService:
    repository = ImplantadorRepository

    @classmethod
    def listar(cls, pesquisa=None, pagina=1):
        limite = 50
        offset = (pagina - 1) * limite
        return (
            cls.repository.listar(pesquisa=pesquisa, limit=limite, offset=offset),
            cls.repository.total(pesquisa=pesquisa),
        )

    @classmethod
    def listar_para_select(cls):
        return cls.repository.listar(limit=1000, offset=0)

    @classmethod
    def buscar_por_id(cls, implantador_id):
        return cls.repository.buscar_por_id(implantador_id)

    @classmethod
    def criar(cls, dados):
        return cls.repository.inserir(cls._normalizar(dados))

    @classmethod
    def atualizar(cls, implantador_id, dados):
        cls.repository.atualizar(implantador_id, cls._normalizar(dados))

    @classmethod
    def inativar(cls, implantador_id):
        cls.repository.inativar(implantador_id)

    @staticmethod
    def _normalizar(dados):
        nome = (dados.get("nome") or "").strip()
        if not nome:
            raise ValueError("Nome do implantador é obrigatório.")
        return {
            "nome": nome,
            "email": (dados.get("email") or "").strip().lower() or None,
            "telefone": formatar_telefone(dados.get("telefone")),
            "ativo": str(dados.get("ativo", "1")) != "0",
            "observacoes": (dados.get("observacoes") or "").strip() or None,
        }
