from app.infraestrutura.zabbix_service import ZabbixMonitoramentoService


def test_normalizar_evento_com_recuperacao_fica_resolvido():
    evento = {
        "eventid": "75574241",
        "clock": "1787078880",
        "value": "1",
        "r_eventid": "75574299",
        "severity": "4",
        "name": "Sup Popular | VR Cotacao Indisponivel",
        "hosts": [{"name": "ZBX-O3CLOUD"}],
        "acknowledged": "0",
    }

    alarme = ZabbixMonitoramentoService._normalizar_evento(evento, {"nome": "Zabbix - O3Cloud"})

    assert alarme["aberto"] is False
    assert alarme["status_label"] == "Resolvido"
    assert alarme["status_classe"] == "success"


def test_normalizar_evento_fora_dos_problemas_ativos_fica_resolvido():
    evento = {
        "eventid": "75574242",
        "clock": "1787078820",
        "value": "1",
        "r_eventid": "0",
        "severity": "4",
        "name": "Emporio Gael | VR Cotacao Indisponivel",
        "hosts": [{"name": "ZBX-O3CLOUD"}],
        "acknowledged": "0",
    }

    alarme = ZabbixMonitoramentoService._normalizar_evento(
        evento,
        {"nome": "Zabbix - O3Cloud"},
        ativo_no_zabbix=False,
    )

    assert alarme["aberto"] is False
    assert alarme["status_label"] == "Resolvido"


def test_normalizar_evento_ativo_usa_estado_atual_do_zabbix():
    evento = {
        "eventid": "75574243",
        "clock": "1787078900",
        "value": "1",
        "severity": "4",
        "name": "CPU alta",
        "hosts": [{"name": "host-antigo"}],
        "acknowledged": "0",
    }
    problema_ativo = {
        "eventid": "75574243",
        "objectid": "9988",
        "severity": "4",
        "acknowledged": "1",
        "name": "CPU media",
    }
    trigger_atual = {
        "triggerid": "9988",
        "priority": "2",
        "description": "CPU media",
        "hosts": [{"name": "host-atual"}],
    }

    alarme = ZabbixMonitoramentoService._normalizar_evento(
        evento,
        {"nome": "Zabbix - O3Cloud"},
        problema_ativo=problema_ativo,
        trigger_atual=trigger_atual,
        ativo_no_zabbix=True,
    )

    assert alarme["aberto"] is True
    assert alarme["severidade"] == 2
    assert alarme["severidade_label"] == "Média"
    assert alarme["acknowledged"] is True
    assert alarme["host"] == "host-atual"


def test_problem_get_nao_usa_parametros_rejeitados_pelo_zabbix(monkeypatch):
    payloads = []

    def fake_post(self, payload):
        payloads.append(payload)
        return []

    from app.integracoes.zabbix.client import ZabbixClient

    monkeypatch.setattr(ZabbixClient, "_post", fake_post)
    ZabbixClient("https://zabbix.example.com", "token").problemas_ativos()

    params = payloads[0]["params"]
    assert "selectHosts" not in params
    assert "selectRelatedObject" not in params
