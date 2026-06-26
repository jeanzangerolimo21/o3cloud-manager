class OmieMapper:

    @staticmethod
    def cliente(cliente):

        return {

            "codigo_externo": cliente.get("codigo_cliente_omie"),

            "nome_fantasia": cliente.get("nome_fantasia"),

            "razao_social": cliente.get("razao_social"),

            "cnpj": cliente.get("cnpj_cpf"),

            "email": cliente.get("email", ""),

            "telefone": cliente.get("telefone1_numero", ""),

            "cidade": cliente.get("cidade", ""),

            "estado": cliente.get("estado", "")

        }
