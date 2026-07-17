from app.repositories.cliente_repository import ClienteRepository
from app.utils.telefone import formatar_telefone


class ClienteService:

    @staticmethod
    def listar(pesquisa=None, ativo=None, origem=None, pagina=1):

        limite = 50

        offset = (pagina - 1) * limite

        clientes = ClienteRepository.listar(

            pesquisa=pesquisa,
            limit=limite,
            origem=origem,
            ativo=ativo,
            offset=offset

        )

        clientes = [ClienteService._formatar_telefone(cliente) for cliente in clientes]

        total = ClienteRepository.total(
            pesquisa=pesquisa,
            ativo=ativo,
            origem=origem
        )

        return clientes,total

    @staticmethod
    def buscar(codigo_externo):

        return ClienteRepository.buscar_por_codigo_externo(
            codigo_externo
        )

    @staticmethod
    def criar(dados):

        return ClienteRepository.inserir(
            ClienteService._normalizar_dados(dados)
        )


    @staticmethod
    def excluir(cliente_id):

        ClienteRepository.excluir(cliente_id)


    @staticmethod
    def buscar_por_id(cliente_id):

        cliente = ClienteRepository.buscar_por_id(cliente_id)
        return ClienteService._formatar_telefone(cliente)


    @staticmethod
    def atualizar(cliente_id, dados):

        ClienteRepository.atualizar(
            cliente_id,
            ClienteService._normalizar_dados(dados)
        )

        cliente = ClienteRepository.buscar_por_id(
            cliente_id
        )
        return ClienteService._formatar_telefone(cliente)

    @staticmethod
    def sincronizar_omie(dados):

        return ClienteRepository.upsert_omie(
            ClienteService._normalizar_dados(dados)
        )

    @classmethod
    def listar_todos(cls):

        return ClienteRepository.listar_todos()

    @classmethod
    def listar_para_importacao(cls):

        clientes = ClienteRepository.listar_para_importacao()
        return [cls._formatar_telefone(cliente) for cliente in clientes]

    @staticmethod
    def _normalizar_dados(dados):
        dados = dict(dados)
        dados["telefone"] = formatar_telefone(dados.get("telefone"))
        return dados

    @staticmethod
    def _formatar_telefone(cliente):
        if not cliente:
            return cliente

        cliente = dict(cliente)
        cliente["telefone"] = formatar_telefone(cliente.get("telefone"))
        return cliente
