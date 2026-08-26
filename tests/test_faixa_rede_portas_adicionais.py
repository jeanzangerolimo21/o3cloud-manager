from werkzeug.datastructures import MultiDict

from app.implantacao.faixas_rede_service import FaixaRedeService


CLIENTE = {"id": 10, "nome_fantasia": "Cliente Teste", "razao_social": "", "cnpj": "123"}


def _dados(**extra):
    dados = {
        "rede": "10.10.10.0/29",
        "quantidade_servidores": "5",
        "fw_wan": "200.200.200.1",
        "fw_lan": "10.10.10.1",
        "cliente_id": "10",
        "vpn": "vpn-01",
        "porta_inicio": "10000",
        "porta_fim": "10010",
        "ativo": "1",
    }
    dados.update(extra)
    return MultiDict(dados)


def _patch_cliente(monkeypatch):
    monkeypatch.setattr("app.implantacao.faixas_rede_service.ClienteService.buscar_por_id", lambda cliente_id: CLIENTE)


def test_normalizar_faixa_rede_com_ranges_adicionais(monkeypatch):
    _patch_cliente(monkeypatch)
    dados = _dados()
    dados.setlist("porta_inicio_adicional", ["10100", "10200"])
    dados.setlist("porta_fim_adicional", ["10110", "10210"])

    payload = FaixaRedeService._normalizar(dados)

    assert payload["porta_inicio"] == 10000
    assert payload["porta_fim"] == 10010
    assert payload["portas"] == "10000-10010"
    assert payload["portas_adicionais"] == [
        {"porta_inicio": 10100, "porta_fim": 10110, "portas": "10100-10110"},
        {"porta_inicio": 10200, "porta_fim": 10210, "portas": "10200-10210"},
    ]


def test_normalizar_faixa_rede_recusa_ranges_sobrepostos(monkeypatch):
    _patch_cliente(monkeypatch)
    dados = _dados(porta_inicio="10000", porta_fim="10050")
    dados.setlist("porta_inicio_adicional", ["10040"])
    dados.setlist("porta_fim_adicional", ["10060"])

    try:
        FaixaRedeService._normalizar(dados)
    except ValueError as erro:
        assert "sobrepõem" in str(erro)
    else:
        raise AssertionError("deveria recusar ranges sobrepostos")
