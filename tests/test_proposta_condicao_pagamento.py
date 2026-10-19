from decimal import Decimal

import pytest

from app.propostas.service import CONDICOES_PAGAMENTO
from app.propostas.service import PropostaService


def test_preparar_form_payload_preserva_condicao_pagamento():
    proposta = PropostaService.preparar_form_payload({"condicao_pagamento": "Entrada + 3x"})

    assert proposta["condicao_pagamento"] == "Entrada + 3x"


def test_validar_rejeita_condicao_pagamento_fora_das_opcoes():
    dados = {
        "cliente_nome": "Cliente Teste",
        "titulo": "Solução Teste",
        "status": "RASCUNHO",
        "clicksign_status": "NAO_ENVIADO",
        "semaforo_fechamento": "FRIO",
        "licencas_items": [{"software": "Teste"}],
        "servidores_items": [],
        "prazo_contratual_meses": 24,
        "condicao_pagamento": "60 dias",
        "total_mensal": 0,
        "parametrizacao_sistema": 0,
        "setup_ambiente_cloud": 0,
        "instalacao_servidores": 0,
        "total_instalacao": 0,
        "valor_total": 0,
    }

    with pytest.raises(ValueError, match="Condição de pagamento inválida"):
        PropostaService.validar(dados)


def test_opcoes_de_condicao_pagamento_sao_as_definidas():
    assert CONDICOES_PAGAMENTO == (
        "À vista",
        "7 / 21 / 35 dias",
        "7 / 14 / 21 dias",
        "7 / 28 / 42 / 57 dias",
        "7 / 14 / 21 / 28 / 35 dias",
        "Entrada + 30",
        "Entrada + 2x",
        "Entrada + 3x",
        "Entrada + 4x",
    )


@pytest.mark.parametrize(
    ("condicao", "prazos"),
    [
        ("À vista", ["À vista"]),
        ("7 / 21 / 35 dias", ["7 dias", "21 dias", "35 dias"]),
        ("Entrada + 30", ["Entrada", "30 dias"]),
        ("Entrada + 3x", ["Entrada", "30 dias", "60 dias", "90 dias"]),
    ],
)
def test_calcular_parcelas_pagamento(condicao, prazos):
    parcelas = PropostaService.calcular_parcelas_pagamento(condicao, Decimal("100.00"))

    assert [parcela["vencimento"] for parcela in parcelas] == prazos
    assert sum(parcela["valor"] for parcela in parcelas) == Decimal("100.00")


def test_calcular_parcelas_ajusta_centavos_na_ultima():
    parcelas = PropostaService.calcular_parcelas_pagamento("7 / 21 / 35 dias", Decimal("100.00"))

    assert [parcela["valor"] for parcela in parcelas] == [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]
