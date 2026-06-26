from decimal import Decimal


class ContratoItemMapper:
    """
    Converte um item de contrato retornado pela API do OMIE
    para o formato utilizado pelo O3Cloud Manager.
    """

    @staticmethod
    def from_omie(item: dict) -> dict:

        cabecalho = item.get("itemCabecalho", {})
        descricao = item.get("itemDescrServ", {})

        return {

            "codigo_item": cabecalho.get("codItem"),

            "codigo_servico": cabecalho.get("codServico"),

            "descricao": descricao.get("descrCompleta"),

            "quantidade": ContratoItemMapper._decimal(
                cabecalho.get("quant")
            ),

            "valor_unitario": ContratoItemMapper._decimal(
                cabecalho.get("valorUnit")
            ),

            "valor_total": ContratoItemMapper._decimal(
                cabecalho.get("valorTotal")
            ),

            "desconto": ContratoItemMapper._decimal(
                cabecalho.get("valorDesconto")
            ),

            "acrescimo": ContratoItemMapper._decimal(
                cabecalho.get("valorAcrescimo")
            ),

            "sequencia": cabecalho.get("seq")

        }

    @staticmethod
    def _decimal(valor):

        if valor in (None, ""):
            return Decimal("0.00")

        return Decimal(str(valor))
