from datetime import datetime, timedelta

from flask import Flask

from app.infraestrutura.alertas_operacao_service import AlertasOperacaoService


class RepoAlertasFake:
    usuarios = []
    marcados = []

    @classmethod
    def listar_usuarios_habilitados(cls):
        return cls.usuarios

    @classmethod
    def marcar_envio_usuario(cls, usuario_id):
        cls.marcados.append(usuario_id)
        return True


def _app():
    app = Flask(__name__)
    app.config["PUBLIC_BASE_URL"] = "https://o3.example.com"
    return app


def test_usuario_deve_receber_respeita_horario_periodicidade_diaria():
    agora = datetime(2026, 8, 14, 8, 30)
    usuario = {
        "alertas_operacao_periodicidade": "DIARIA",
        "alertas_operacao_horario": "08:00",
        "alertas_operacao_ultimo_envio_em": datetime(2026, 8, 13, 9, 0),
    }

    assert AlertasOperacaoService._usuario_deve_receber(usuario, agora) is True

    usuario["alertas_operacao_ultimo_envio_em"] = datetime(2026, 8, 14, 8, 5)
    assert AlertasOperacaoService._usuario_deve_receber(usuario, agora) is False

    usuario["alertas_operacao_horario"] = "09:00"
    usuario["alertas_operacao_ultimo_envio_em"] = datetime(2026, 8, 13, 9, 0)
    assert AlertasOperacaoService._usuario_deve_receber(usuario, agora) is False


def test_usuario_deve_receber_respeita_periodicidade_semanal():
    agora = datetime(2026, 8, 14, 10, 0)
    usuario = {
        "alertas_operacao_periodicidade": "SEMANAL",
        "alertas_operacao_horario": "08:00",
        "alertas_operacao_ultimo_envio_em": agora - timedelta(days=6, hours=23),
    }

    assert AlertasOperacaoService._usuario_deve_receber(usuario, agora) is False

    usuario["alertas_operacao_ultimo_envio_em"] = agora - timedelta(days=7)
    assert AlertasOperacaoService._usuario_deve_receber(usuario, agora) is True


def test_processar_pendentes_envia_alerta_e_marca_usuario(monkeypatch):
    RepoAlertasFake.usuarios = [{
        "id": 3,
        "nome": "Operacao",
        "email": "ops@example.com",
        "alertas_operacao_periodicidade": "DIARIA",
        "alertas_operacao_horario": "08:00",
        "alertas_operacao_ultimo_envio_em": None,
    }]
    RepoAlertasFake.marcados = []
    envios = []
    monkeypatch.setattr(AlertasOperacaoService, "repository", RepoAlertasFake)
    monkeypatch.setattr(AlertasOperacaoService, "resumo_alertas", classmethod(lambda cls: {
        "zabbix": [{"host": "srv01", "nome": "CPU alta"}],
        "pbs": [],
        "truenas": [],
        "total_alertas": 1,
        "links": {"zabbix": "/z", "pbs": "/p", "truenas": "/t"},
        "gerado_em": datetime(2026, 8, 14, 8, 0),
    }))
    monkeypatch.setattr("app.infraestrutura.alertas_operacao_service.EmailService.enviar", lambda assunto, corpo, destinatarios, corpo_html=None: envios.append((assunto, corpo, destinatarios, corpo_html)) or {"enviado": True})

    with _app().app_context():
        resultados = AlertasOperacaoService.processar_pendentes(agora=datetime(2026, 8, 14, 8, 5))

    assert resultados[0].startswith("OK usuario #3")
    assert RepoAlertasFake.marcados == [3]
    assert "1 alerta" in envios[0][0]
    assert "CPU alta" in envios[0][1]


def test_processar_pendentes_nao_envia_sem_alertas(monkeypatch):
    RepoAlertasFake.usuarios = [{"id": 3, "email": "ops@example.com"}]
    RepoAlertasFake.marcados = []
    monkeypatch.setattr(AlertasOperacaoService, "repository", RepoAlertasFake)
    monkeypatch.setattr(AlertasOperacaoService, "resumo_alertas", classmethod(lambda cls: {
        "zabbix": [], "pbs": [], "truenas": [], "total_alertas": 0, "links": {}, "gerado_em": datetime.now()
    }))

    resultados = AlertasOperacaoService.processar_pendentes()

    assert resultados == ["Nenhum alerta operacional critico para enviar."]
    assert RepoAlertasFake.marcados == []
