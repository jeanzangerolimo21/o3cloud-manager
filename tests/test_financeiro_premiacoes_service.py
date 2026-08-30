from app.financeiro.repository import FinanceiroRepository
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


def test_sql_comissoes_usa_executivo_manual_quando_projeto_omie_vazio():
    sql, _ = FinanceiroRepository._comissoes_sql({})

    assert "pe_omie.nome_normalizado = LOWER(TRIM(c.projeto_nome))" in sql
    assert "LEFT JOIN parceiros_executivos pe_manual" in sql
    assert "pe_manual.id = c.executivo_id" in sql
    assert "WHEN COALESCE(TRIM(c.projeto_nome), '') <> '' THEN pe_omie.id" in sql
    assert "ELSE pe_manual.id" in sql
    assert "LOWER(TRIM(c.vendedor_nome)) COLLATE utf8mb4_unicode_ci," not in sql


def test_regularizar_premiacoes_adendos_vinculo_manual_chama_repositorio(monkeypatch):
    chamadas = []
    monkeypatch.setattr(
        "app.financeiro.service.FinanceiroRepository.atualizar_premiacoes_adendos_sem_executivo_por_vinculo_manual",
        lambda usuario_email="sistema", adendo_id=None: chamadas.append((usuario_email, adendo_id)) or 4,
    )

    total = FinanceiroService.regularizar_premiacoes_adendos_vinculo_manual("financeiro@o3cloud.com.br", 99)

    assert total == 4
    assert chamadas == [("financeiro@o3cloud.com.br", 99)]


def test_sql_regularizacao_adendos_atualiza_executivo_e_valores_do_vinculo_manual():
    sqls = []

    class RepoFake(FinanceiroRepository):
        @classmethod
        def execute(cls, sql, params=()):
            sqls.append((sql, params))
            return 4

    total = RepoFake.atualizar_premiacoes_adendos_sem_executivo_por_vinculo_manual("financeiro@o3cloud.com.br", 99)

    sql, params = sqls[0]
    assert total == 4
    assert "UPDATE financeiro_premiacoes_adendos pa" in sql
    assert "pe_manual.id = c.executivo_id" in sql
    assert "pa.executivo_id = pe_manual.id" in sql
    assert "pa.valor_premiacao_executivo = ROUND(pa.valor_base * COALESCE(rc.percentual_executivo, 0) / 100, 2)" in sql
    assert "COALESCE(TRIM(c.projeto_nome), '') = ''" in sql
    assert "AND pa.adendo_id = %s" in sql
    assert params == ("financeiro@o3cloud.com.br", 99)

