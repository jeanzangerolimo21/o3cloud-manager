from app.repositories.cliente_repository import ClienteRepository


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
            dados
        )


    @staticmethod
    def excluir(cliente_id):

        ClienteRepository.excluir(cliente_id)


    @staticmethod
    def buscar_por_id(cliente_id):

        return ClienteRepository.buscar_por_id(cliente_id)

    
    @staticmethod
    def atualizar(cliente_id, dados):

        ClienteRepository.atualizar(
            cliente_id,
            dados
        )

        return ClienteRepository.buscar_por_id(
            cliente_id
        )
    @staticmethod
    def sincronizar_omie(dados):

        return ClienteRepository.upsert_omie(
            dados
        )

    @classmethod
    def listar_todos(cls):

        return ClienteRepository.listar_todos()
