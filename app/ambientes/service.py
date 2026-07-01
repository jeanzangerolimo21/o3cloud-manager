from app.repositories.ambiente_repository import AmbienteRepository


class AmbienteService:

    @staticmethod
    def listar(pesquisa=None, pagina=1):

        limite = 50

        offset = (pagina - 1) * limite

        ambientes = AmbienteRepository.listar(

            pesquisa=pesquisa,

            limit=limite,

            offset=offset

        )

        total = AmbienteRepository.total(

            pesquisa=pesquisa

        )

        return ambientes, total

    @staticmethod
    def buscar(ambiente_id):

        return AmbienteRepository.buscar_por_id(

            ambiente_id

        )

    @staticmethod
    def buscar_por_cliente(cliente_id):

        return AmbienteRepository.buscar_por_cliente(

            cliente_id

        )

    @staticmethod
    def inserir(dados):

        AmbienteRepository.inserir(

            dados

        )

    @staticmethod
    def atualizar(ambiente_id, dados):

        AmbienteRepository.atualizar(

            ambiente_id,

            dados

        )

    @staticmethod
    def excluir(ambiente_id):

        AmbienteRepository.excluir(

            ambiente_id

        )
