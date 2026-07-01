from app.core.constants.origens import ORIGEM_OMIE
from html import unescape

class ClienteMapper:

    @staticmethod
    def from_omie(cliente):

        return {

            "codigo_externo": cliente.get("codigo_cliente_omie"),

            "origem": ORIGEM_OMIE,

            "nome_fantasia": unescape(cliente.get("nome_fantasia") or ""),

            "razao_social": unescape(cliente.get("razao_social") or ""),

            "cnpj": cliente.get("cnpj_cpf"),

            "email": cliente.get("email", ""),

            "telefone": cliente.get("telefone1_numero", ""),

            "cidade": cliente.get("cidade", ""),

            "estado": cliente.get("estado", "")

        }
