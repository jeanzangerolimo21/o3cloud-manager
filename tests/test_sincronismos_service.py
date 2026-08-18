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
