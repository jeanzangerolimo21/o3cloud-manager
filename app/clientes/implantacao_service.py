from app.repositories.implantacao_repository import ImplantacaoRepository


class ImplantacaoService:

    @staticmethod
    def buscar(cliente_id):

        dados = ImplantacaoRepository.buscar_por_cliente(
            cliente_id
        )

        if not dados:

            ImplantacaoRepository.inserir(
                cliente_id
            )

            dados = ImplantacaoRepository.buscar_por_cliente(
                cliente_id
            )

        return dados


    @staticmethod
    def salvar(cliente_id, dados):

        ImplantacaoRepository.salvar(
            cliente_id,
            dados
        )
