from werkzeug.datastructures import MultiDict

from app.implantacao.faixas_rede_service import FaixaRedeService


CLIENTE = {"id": 10, "nome_fantasia": "Cliente Teste", "razao_social": "", "cnpj": "123"}


def _dados(**extra):
    dados = {
        "rede": "10.10.10.0/29",
        "quantidade_servidores": "5",
        "fw_wan": "10.100.100.120",
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


def test_sugerir_proxima_por_ultima_usa_proxima_rede_contigua(monkeypatch):
    monkeypatch.setattr(
        "app.implantacao.faixas_rede_service.FaixaRedeRepository.ultima_ativa_cadastrada",
        lambda: {"rede": "10.200.101.192/29", "fw_wan": "10.100.100.120", "porta_fim": 10010},
    )
    monkeypatch.setattr(
        "app.implantacao.faixas_rede_service.FaixaRedeRepository.listar_ativas",
        lambda: [{"rede": "10.200.101.192/29"}],
    )

    sugestao = FaixaRedeService.sugerir_proxima_por_ultima("5")

    assert sugestao["rede"] == "10.200.101.200/29"
    assert sugestao["mascara"] == 29
    assert sugestao["quantidade_servidores"] == 5
    assert sugestao["fw_lan"] == "10.200.101.201"
    assert sugestao["pve"] == "10.200.101.202, 10.200.101.203, 10.200.101.204, 10.200.101.205, 10.200.101.206"
    assert sugestao["fw_wan"] == "10.100.100.121"
    assert sugestao["porta_inicio"] == 10011
    assert sugestao["porta_fim"] == 10016


def test_sugerir_proxima_por_ultima_respeita_quantidade_maior(monkeypatch):
    monkeypatch.setattr(
        "app.implantacao.faixas_rede_service.FaixaRedeRepository.ultima_ativa_cadastrada",
        lambda: {"rede": "10.200.101.192/29", "fw_wan": "10.100.100.120", "porta_fim": 10010},
    )
    monkeypatch.setattr(
        "app.implantacao.faixas_rede_service.FaixaRedeRepository.listar_ativas",
        lambda: [{"rede": "10.200.101.192/29"}],
    )

    sugestao = FaixaRedeService.sugerir_proxima_por_ultima("8")

    assert sugestao["rede"] == "10.200.101.208/28"
    assert sugestao["mascara"] == 28
    assert sugestao["quantidade_servidores"] == 8
    assert sugestao["fw_lan"] == "10.200.101.209"
    assert sugestao["porta_inicio"] == 10011
    assert sugestao["porta_fim"] == 10016


def test_proximo_ipv4_recusa_valor_invalido():
    assert FaixaRedeService._proximo_ipv4("fw-01") == ""
    assert FaixaRedeService._proximo_ipv4("") == ""
