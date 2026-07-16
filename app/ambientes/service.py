from app.repositories.ambiente_repository import AmbienteRepository
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.parceiro_repository import ParceiroRepository
from app.repositories.contrato_repository import ContratoRepository

FORM_LIMIT = 1000

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
    def buscar_por_id(ambiente_id):

        return AmbienteRepository.buscar_por_id(

            ambiente_id

        )

    @staticmethod
    def buscar_por_cliente(cliente_id):

        return AmbienteRepository.buscar_por_cliente(

            cliente_id

        )

    @staticmethod
    def criar( dados):

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

    @staticmethod
    def carregar_dependencias_formulario():

            clientes = ClienteRepository.listar(
                limit=FORM_LIMIT,
                offset=0
            )

            parceiros = ParceiroRepository.listar(
                limit=FORM_LIMIT,
                offset=0
            )

            contratos = ContratoRepository.listar(
                status="ATIVO",    
                limit=FORM_LIMIT,
                offset=0
            )

            return {

                "clientes": clientes,

                "parceiros": parceiros,

                "contratos": contratos,

                # Sprint 7
                "clusters": [],

                # Sprint 7
                "nodes": [],

                # Sprint 8
                "storage": [],

                # Sprint 8
                "equipes": []

            }
