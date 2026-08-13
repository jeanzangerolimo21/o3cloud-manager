from app.repositories.parceiro_repository import ParceiroRepository
from app.utils.telefone import formatar_telefone


class ParceiroService:

    @classmethod
    def listar(cls, pesquisa=None, status_negociacao=None, ativo=None, executivo_id=None, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit

        parceiros = ParceiroRepository.listar(
            pesquisa=pesquisa,
            status_negociacao=status_negociacao,
            ativo=ativo,
            executivo_id=executivo_id,
            limit=limit,
            offset=offset
        )

        total = ParceiroRepository.total(
            pesquisa=pesquisa,
            status_negociacao=status_negociacao,
            ativo=ativo,
            executivo_id=executivo_id
        )

        return [cls._formatar_telefones(parceiro) for parceiro in parceiros], total

    @classmethod
    def listar_todos_ativos(cls):
        return ParceiroRepository.listar_todos_ativos()

    @classmethod
    def buscar_por_id(cls, parceiro_id):
        parceiro = ParceiroRepository.buscar_por_id(parceiro_id)
        return cls._formatar_telefones(parceiro)

    @classmethod
    def criar(cls, dados):
        ParceiroRepository.inserir(cls._normalizar_dados(dados))

    @classmethod
    def atualizar(cls, parceiro_id, dados):
        ParceiroRepository.atualizar(parceiro_id, cls._normalizar_dados(dados))

    @classmethod
    def excluir(cls, parceiro_id):
        ParceiroRepository.excluir(parceiro_id)

    @classmethod
    def _normalizar_dados(cls, dados):
        dados = dict(dados)
        dados["telefone"] = formatar_telefone(dados.get("telefone"))
        dados["contato_1_telefone"] = formatar_telefone(dados.get("contato_1_telefone"))
        dados["contato_2_telefone"] = formatar_telefone(dados.get("contato_2_telefone"))
        dados["contato_3_telefone"] = formatar_telefone(dados.get("contato_3_telefone"))
        dados["sigla"] = (dados.get("sigla") or "").strip().upper() or None
        dados["premiacao_ativa"] = str(dados.get("premiacao_ativa", "0")) in ("1", "true", "True", "on")
        return dados

    @classmethod
    def _formatar_telefones(cls, parceiro):
        if not parceiro:
            return parceiro

        parceiro = dict(parceiro)
        parceiro["telefone"] = formatar_telefone(parceiro.get("telefone"))
        parceiro["telefone_exibicao"] = formatar_telefone(parceiro.get("telefone_exibicao"))
        parceiro["contato_1_telefone"] = formatar_telefone(parceiro.get("contato_1_telefone"))
        parceiro["contato_2_telefone"] = formatar_telefone(parceiro.get("contato_2_telefone"))
        parceiro["contato_3_telefone"] = formatar_telefone(parceiro.get("contato_3_telefone"))
        return parceiro
