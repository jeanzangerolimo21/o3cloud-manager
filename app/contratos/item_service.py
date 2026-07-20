import re
from decimal import Decimal

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

        quantidade_usuarios = Decimal("0")

        for item in itens:

            dados = ContratoItemMapper.from_omie(item)

            dados["contrato_id"] = contrato["id"]
            quantidade_usuarios += cls._quantidade_usuarios_item(dados)

            status = ContratoItemRepository.upsert_omie(dados)

            resultado.append({

                "status": status,

                "codigo_item": dados["codigo_item"],

                "descricao": dados["descricao"]

            })

        ContratoRepository.atualizar_quantidade_usuarios(
            contrato["id"],
            int(quantidade_usuarios) if quantidade_usuarios else None,
        )

        return resultado

    @classmethod
    def _quantidade_usuarios_item(cls, dados):
        descricao = (dados.get("descricao") or "").lower()
        if not cls._item_usuario(descricao):
            return Decimal("0")
        return dados.get("quantidade") or Decimal("0")

    @staticmethod
    def _item_usuario(descricao):
        return bool(
            re.search(r"\busuario(s)?\b|\busuario\b|licenciamento de uso|licen[çc]a", descricao)
        )
