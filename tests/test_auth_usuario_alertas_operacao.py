from werkzeug.datastructures import MultiDict

from app.configuracoes.auth_service import AuthConfigService


def test_normalizar_usuario_com_alertas_operacao_e_perfil():
    dados = MultiDict({
        "nome": "Usuario Operacao",
        "email": "ops@example.com",
        "login": "ops@example.com",
        "origem": "LOCAL",
        "perfil_id": "5",
        "status": "ATIVO",
        "receber_alertas_operacao": "1",
        "alertas_operacao_periodicidade": "SEMANAL",
        "alertas_operacao_horario": "07:30",
        "two_factor_metodo": "EMAIL",
    })

    payload = AuthConfigService._normalizar_usuario(dados)

    assert payload["perfil_id"] == 5
    assert payload["receber_alertas_operacao"] is True
    assert payload["alertas_operacao_periodicidade"] == "SEMANAL"
    assert payload["alertas_operacao_horario"] == "07:30"


def test_normalizar_usuario_alertas_operacao_usa_padrao_quando_horario_invalido():
    dados = MultiDict({
        "nome": "Usuario Operacao",
        "email": "ops@example.com",
        "login": "ops@example.com",
        "origem": "LOCAL",
        "perfil_id": "5",
        "status": "ATIVO",
        "alertas_operacao_periodicidade": "MENSAL",
        "alertas_operacao_horario": "8:00:",
        "two_factor_metodo": "EMAIL",
    })

    payload = AuthConfigService._normalizar_usuario(dados)

    assert payload["receber_alertas_operacao"] is False
    assert payload["alertas_operacao_periodicidade"] == "DIARIA"
    assert payload["alertas_operacao_horario"] == "08:00"
