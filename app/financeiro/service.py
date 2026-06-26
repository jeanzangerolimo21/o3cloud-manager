from app.financeiro.repository import FinanceiroRepository


class FinanceiroService:

    @staticmethod
    def dashboard():

        return {

            "clientes": FinanceiroRepository.total_clientes(),

            "contratos": FinanceiroRepository.total_contratos(),

            "produtos": FinanceiroRepository.total_produtos(),

            "receita": FinanceiroRepository.receita_total()

        }


    @staticmethod
    def listar_clientes():

        return FinanceiroRepository.listar_clientes()

    @staticmethod
    def buscar_cliente(cliente_id):

        return FinanceiroRepository.buscar_cliente(cliente_id)
