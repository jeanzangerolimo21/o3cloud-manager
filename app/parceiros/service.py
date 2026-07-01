from app.repositories.parceiro_repository import ParceiroRepository


class ParceiroService:

    @classmethod
    def listar(cls, pesquisa=None, pagina=1):

        limit = 50

        offset = (pagina - 1) * limit

        parceiros = ParceiroRepository.listar(
            pesquisa=pesquisa,
            limit=limit,
            offset=offset
        )

        total = ParceiroRepository.total(
            pesquisa=pesquisa
        )

        return parceiros, total


    @classmethod
    def buscar_por_id(cls, parceiro_id):

        return ParceiroRepository.buscar_por_id(
            parceiro_id
        )


    @classmethod
    def criar(cls, dados):

        ParceiroRepository.inserir(
            dados
        )


    @classmethod
    def atualizar(cls, parceiro_id, dados):

        ParceiroRepository.atualizar(
            parceiro_id,
            dados
        )


    @classmethod
    def excluir(cls, parceiro_id):

        ParceiroRepository.excluir(
            parceiro_id
        )
