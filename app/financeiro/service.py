from app.financeiro.repository import FinanceiroRepository


class FinanceiroService:

    @staticmethod
    def dashboard():

        return FinanceiroRepository.dashboard_executivo()


    @staticmethod
    def listar_clientes():

        return FinanceiroRepository.listar_clientes()

    @staticmethod
    def buscar_cliente(cliente_id):

        return FinanceiroRepository.buscar_cliente(cliente_id)
