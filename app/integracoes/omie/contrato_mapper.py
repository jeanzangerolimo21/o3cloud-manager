from datetime import datetime
from decimal import Decimal
from app.core.constants.origens import ORIGEM_OMIE


class ContratoMapper:
    """
    Converte um contrato retornado pela API do OMIE
    para o formato utilizado pelo O3Cloud Manager.
    """
    STATUS_MAP = {
        "00": "ENCAMINHADO_PROJETO",
        "10": "ATIVO",
        "20": "SUSPENSO",
        "30": "EM_IMPLANTACAO",
        "40": "ENCERRADO",
        "50": "CANCELADO",
        "90": "SUSPENSO",
        "99": "CANCELADO",
        "WAIG": "SUSPENSO"
    }

    @staticmethod
    def from_omie(item: dict) -> dict:

        cabecalho = item.get("cabecalho", {})
        inf_adic = item.get("infAdic", {})
        observacoes = item.get("observacoes", {})
        codigo_status = str(cabecalho.get("cCodSit") or "").strip().upper()
        totais_servicos = ContratoMapper._totais_servicos(
            item.get("itensContrato", [])
        )

        if codigo_status not in ContratoMapper.STATUS_MAP:

            print("=" * 80)
            print("STATUS OMIE NÃO MAPEADO")
            print("Contrato :", cabecalho.get("cNumCtr"))
            print("Código   :", codigo_status)
            print(cabecalho)
            print("=" * 80)

        status = ContratoMapper.STATUS_MAP.get(
            codigo_status,
            "SUSPENSO"
        )

        return {

            "codigo_externo": cabecalho.get("nCodCtr"),

            "cliente_codigo_externo": cabecalho.get("nCodCli"),

            "numero": cabecalho.get("cNumCtr"),

            "status": status,

            "ativo": status != "CANCELADO",

            "tipo_faturamento": cabecalho.get("cTipoFat"),

            "inicio_vigencia": ContratoMapper._converter_data(
                cabecalho.get("dVigInicial")
            ),

            "fim_vigencia": ContratoMapper._converter_data(
                cabecalho.get("dVigFinal")
            ),

            "dia_faturamento": cabecalho.get("nDiaFat"),

            "valor_mensal": ContratoMapper._decimal(
                cabecalho.get("nValTotMes")
            ),

            "codigo_vendedor": inf_adic.get("nCodVend"),

            "codigo_projeto": inf_adic.get("nCodProj"),

            "codigo_cc": inf_adic.get("nCodCC"),

            "observacoes": observacoes.get("cObsContrato"),

            "observacao_contrato": observacoes.get("cObsContrato"),

            "valor_servicos_bruto": totais_servicos["bruto"],

            "valor_descontos": totais_servicos["descontos"],

            "valor_servicos_liquido": totais_servicos["liquido"],

            "origem": ORIGEM_OMIE

        }

    @staticmethod
    def _converter_data(data):

        if not data:
            return None

        return datetime.strptime(
            data,
            "%d/%m/%Y"
        ).date()

    @staticmethod
    def _decimal(valor):

        if valor in (None, ""):
            return Decimal("0.00")

        return Decimal(str(valor))

    @staticmethod
    def _totais_servicos(itens):

        bruto = Decimal("0.00")
        descontos = Decimal("0.00")

        for item in itens or []:
            cabecalho = item.get("itemCabecalho", {})
            quantidade = ContratoMapper._decimal(cabecalho.get("quant"))
            valor_unitario = ContratoMapper._decimal(cabecalho.get("valorUnit"))
            bruto += quantidade * valor_unitario
            descontos += ContratoMapper._decimal(cabecalho.get("valorDesconto"))

        liquido = bruto - descontos

        return {
            "bruto": bruto.quantize(Decimal("0.01")),
            "descontos": descontos.quantize(Decimal("0.01")),
            "liquido": liquido.quantize(Decimal("0.01")),
        }
