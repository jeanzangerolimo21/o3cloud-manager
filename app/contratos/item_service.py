from app.integracoes.omie.contrato_item_mapper import ContratoItemMapper

from app.repositories.contrato_repository import ContratoRepository
from app.repositories.contrato_item_repository import (
    ContratoItemRepository
)


class ContratoItemService:
    """
    Regras de negócio dos itens dos contratos.
    """

    @classmethod
    def sincronizar_itens(cls, contrato_omie):

        cabecalho = contrato_omie.get("cabecalho", {})

        codigo_contrato = cabecalho.get("nCodCtr")

        contrato = ContratoRepository.buscar_por_codigo_externo(
            codigo_contrato
        )

        if not contrato:

            return {
                "status": "IGNORADO",
                "motivo": "Contrato não encontrado"
            }

        resultado = []

        itens = contrato_omie.get("itensContrato", [])

        for item in itens:

            dados = ContratoItemMapper.from_omie(item)

            dados["contrato_id"] = contrato["id"]
            
            print("=" * 80)
            print(dados["descricao"])
            print(len(dados["descricao"]))
            print("=" * 80)

            status = ContratoItemRepository.upsert_omie(dados)

            resultado.append({

                "status": status,

                "codigo_item": dados["codigo_item"],

                "descricao": dados["descricao"]

            })

        return resultado
