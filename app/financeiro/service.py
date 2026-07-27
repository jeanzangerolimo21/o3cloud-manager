from app.financeiro.repository import FinanceiroRepository


class FinanceiroService:

    @staticmethod
    def dashboard(filtros=None):

        return FinanceiroRepository.dashboard_executivo(filtros)

    @staticmethod
    def filtros_dashboard(dados):

        return {
            "data_de": FinanceiroService._texto(dados.get("data_de")),
            "data_ate": FinanceiroService._texto(dados.get("data_ate")),
            "parceiro_id": FinanceiroService._inteiro(dados.get("parceiro_id")),
            "executivo_id": FinanceiroService._inteiro(dados.get("executivo_id")),
            "status_comercial": FinanceiroService._texto(dados.get("status_comercial")),
            "status_contrato": FinanceiroService._texto(dados.get("status_contrato")),
            "status_implantacao": FinanceiroService._texto(dados.get("status_implantacao")),
        }

    @staticmethod
    def contexto_dashboard():

        return {
            "parceiros": FinanceiroRepository.listar_parceiros_dashboard(),
            "executivos": FinanceiroRepository.listar_executivos_dashboard(),
        }


    @staticmethod
    def listar_clientes():

        return FinanceiroRepository.listar_clientes()

    @staticmethod
    def buscar_cliente(cliente_id):

        return FinanceiroRepository.buscar_cliente(cliente_id)
    @staticmethod
    def _texto(valor):

        return (valor or "").strip() or None

    @staticmethod
    def _inteiro(valor):

        try:
            return int(valor or 0) or None
        except (TypeError, ValueError):
            return None

