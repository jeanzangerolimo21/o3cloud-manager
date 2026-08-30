from decimal import Decimal

from app.propostas.service import PropostaService


def _dados_base(**extra):
    dados = {
        "cliente_id": "1",
        "codigo_proposta": "PROP-1",
        "titulo": "O3 Cloud",
        "status": "RASCUNHO",
        "setup_dias": "7",
        "mensalidade_dias": "30",
        "prazo_contratual_meses": "24",
        "parametrizacao_sistema": "100.00",
        "setup_ambiente_cloud": "100.00",
        "instalacao_servidores": "300.00",
        "licencas_snapshot": "[]",
        "servidores_snapshot": "[]",
        "ativo": "1",
    }
    dados.update(extra)
    return dados


def test_normalizar_proposta_omite_instalacao_recursos_por_padrao():
    dados = PropostaService.normalizar(_dados_base())

    assert dados["incluir_instalacao_recursos"] is False
    assert dados["instalacao_servidores"] == Decimal("0.00")
    assert dados["total_instalacao"] == Decimal("200.00")
    assert dados["valor_total"] == Decimal("200.00")


def test_normalizar_proposta_inclui_instalacao_recursos_quando_marcado():
    dados = PropostaService.normalizar(_dados_base(incluir_instalacao_recursos="1"))

    assert dados["incluir_instalacao_recursos"] is True
    assert dados["instalacao_servidores"] == Decimal("300.00")
    assert dados["total_instalacao"] == Decimal("500.00")
    assert dados["valor_total"] == Decimal("500.00")


def test_decorar_proposta_antiga_remove_instalacao_oculta_do_total():
    proposta = PropostaService._decorar_proposta(_dados_base(valor_total="500.00", total_instalacao="500.00"))

    assert proposta["incluir_instalacao_recursos"] is False
    assert proposta["instalacao_servidores"] == Decimal("0.00")
    assert proposta["total_instalacao"] == Decimal("200.00")
    assert proposta["valor_total"] == Decimal("200.00")
