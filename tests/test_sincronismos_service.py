from datetime import timedelta

import pytest

from app.configuracoes.sincronismos_service import SincronismosAgendadosService


def test_horario_execucao_e_formatado():
    horario = SincronismosAgendadosService._normalizar_horario("02:30")
    assert horario.hour == 2
    assert horario.minute == 30
    assert SincronismosAgendadosService._formatar_horario(timedelta(hours=2, minutes=30)) == "02:30"


def test_horario_execucao_invalido():
    with pytest.raises(ValueError):
        SincronismosAgendadosService._normalizar_horario("25:90")


def test_tipo_omie_setup_contratos_tem_handler():
    handler = SincronismosAgendadosService._handler("OMIE_SETUP_CONTRATOS")

    assert handler == SincronismosAgendadosService._sincronizar_omie_setup_contratos
    assert SincronismosAgendadosService.TIPOS["OMIE_SETUP_CONTRATOS"]["nome"] == "Omie - Setup dos Contratos"


class RepositoryFake:
    comandos = []
    agendamento = None

    @classmethod
    def generate_uuid(cls):
        return "uuid-teste"

    @classmethod
    def execute(cls, sql, params=None):
        cls.comandos.append((sql, params))

    @classmethod
    def fetch_one(cls, sql, params=None):
        return cls.agendamento


def test_salvar_cria_agendamento_quando_migration_ainda_nao_foi_aplicada(monkeypatch):
    RepositoryFake.comandos = []
    monkeypatch.setattr(SincronismosAgendadosService, "repository", RepositoryFake)

    SincronismosAgendadosService.salvar(
        "OMIE_FATURAMENTO_PREVISOES",
        {"ativo": "1", "frequencia_minutos": "1440", "horario_execucao": "02:30"},
        "admin@example.com",
    )

    sql, params = RepositoryFake.comandos[0]
    assert "INSERT INTO config_sincronismos_agendados" in sql
    assert "ON DUPLICATE KEY UPDATE" in sql
    assert params[1:5] == ("OMIE_FATURAMENTO_PREVISOES", "Omie - Faturamento e Previsoes", 1, 1440)


def test_execucao_manual_por_tipo_cria_agendamento_ausente(monkeypatch):
    RepositoryFake.comandos = []
    RepositoryFake.agendamento = {
        "id": 42,
        "tipo": "OMIE_FATURAMENTO_PREVISOES",
        "ativo": 0,
        "frequencia_minutos": 1440,
        "horario_execucao": None,
    }
    monkeypatch.setattr(SincronismosAgendadosService, "repository", RepositoryFake)
    monkeypatch.setattr(
        SincronismosAgendadosService,
        "_executar",
        classmethod(lambda cls, agendamento, usuario_email, manual=False: "executado"),
    )

    resultado = SincronismosAgendadosService.executar_manual_por_tipo(
        "OMIE_FATURAMENTO_PREVISOES", "admin@example.com"
    )

    assert resultado == "executado"
    assert "INSERT INTO config_sincronismos_agendados" in RepositoryFake.comandos[0][0]
