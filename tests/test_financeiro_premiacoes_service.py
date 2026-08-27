from app.financeiro.service import FinanceiroService


def test_atualizar_status_premiacao_manual_grava_quando_recebido(monkeypatch):
    gravados = []

    monkeypatch.setattr(
        FinanceiroService,
        "buscar_comissao_contrato",
        lambda contrato_id, campanha_id=None: {
            "contrato_id": contrato_id,
            "campanha_id": campanha_id,
            "premiacao_liberada": 1,
            "status_pagamento": "RECEBIDO",
        },
    )
    monkeypatch.setattr(
        "app.financeiro.service.FinanceiroRepository.salvar_status_premiacao_manual",
        lambda contrato_id, campanha_id, status, usuario_email=None: gravados.append((contrato_id, campanha_id, status, usuario_email)),
    )

    resultado = FinanceiroService.atualizar_status_premiacao_manual(10, 4, "PAGO", "financeiro@example.com")

    assert resultado == {"status": "PAGO", "label": "Pago"}
    assert gravados == [(10, 4, "PAGO", "financeiro@example.com")]


def test_atualizar_status_premiacao_manual_recusa_sem_recebimento(monkeypatch):
    monkeypatch.setattr(
        FinanceiroService,
        "buscar_comissao_contrato",
        lambda contrato_id, campanha_id=None: {
            "contrato_id": contrato_id,
            "campanha_id": campanha_id,
            "premiacao_liberada": 1,
            "status_pagamento": "ATRASADO",
        },
    )

    try:
        FinanceiroService.atualizar_status_premiacao_manual(10, 4, "LANCADO", "financeiro@example.com")
    except ValueError as erro:
        assert "após o recebimento" in str(erro)
    else:
        raise AssertionError("deveria recusar atualização sem status RECEBIDO")


def test_atualizar_status_premiacao_manual_recusa_status_invalido(monkeypatch):
    try:
        FinanceiroService.atualizar_status_premiacao_manual(10, 4, "FECHADO", "financeiro@example.com")
    except ValueError as erro:
        assert "inválido" in str(erro)
    else:
        raise AssertionError("deveria recusar status manual inválido")
