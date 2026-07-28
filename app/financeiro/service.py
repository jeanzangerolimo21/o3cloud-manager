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
    def filtros_produtos_clientes(dados):

        return {
            "q": FinanceiroService._texto(dados.get("q")),
            "status": FinanceiroService._texto(dados.get("status")),
            "origem": FinanceiroService._texto(dados.get("origem")),
            "situacao": FinanceiroService._texto(dados.get("situacao")),
        }

    @staticmethod
    def produtos_clientes(filtros=None):

        return FinanceiroRepository.produtos_clientes(filtros)

    @staticmethod
    def contexto_dashboard():

        return {
            "parceiros": FinanceiroRepository.listar_parceiros_dashboard(),
            "executivos": FinanceiroRepository.listar_executivos_dashboard(),
        }

    @staticmethod
    def links_dashboard(filtros):
        filtros = filtros or {}

        contratos_base = FinanceiroService._limpar_params({
            "status": filtros.get("status_contrato"),
            "data_de": filtros.get("data_de"),
            "data_ate": filtros.get("data_ate"),
        })
        implantacoes_base = FinanceiroService._limpar_params({
            "status": filtros.get("status_implantacao"),
        })
        propostas_base = FinanceiroService._limpar_params({
            "status": filtros.get("status_comercial"),
        })

        return {
            "propostas_index": propostas_base,
            "propostas_assinatura": FinanceiroService._limpar_params({
                **propostas_base,
                "clicksign_status": "AGUARDANDO_ASSINATURAS",
            }),
            "contratos_dashboard": contratos_base,
            "contratos_index": contratos_base,
            "contratos_ativos": FinanceiroService._limpar_params({
                **contratos_base,
                "status": "ATIVO",
            }),
            "contratos_a_iniciar": FinanceiroService._limpar_params({
                **contratos_base,
                "status": filtros.get("status_contrato") or "ENCAMINHADO_PROJETO",
            }),
            "implantacoes_index": implantacoes_base,
            "implantacoes_atrasadas": FinanceiroService._limpar_params({
                **implantacoes_base,
                "prazo": "atrasadas",
            }),
            "implantacoes_vence_7": FinanceiroService._limpar_params({
                **implantacoes_base,
                "prazo": "vence_7",
            }),
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

    @staticmethod
    def _limpar_params(params):

        return {chave: valor for chave, valor in params.items() if valor not in (None, "")}

