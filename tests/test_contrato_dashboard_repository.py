from decimal import Decimal

from app.repositories.contrato_repository import ContratoRepository


def test_sql_agrupamento_adendos_soma_recorrencia():
    class CursorFake:
        def __init__(self):
            self.sql = None
            self.params = None

        def execute(self, sql, params=()):
            self.sql = sql
            self.params = params

        def fetchall(self):
            return []

    cursor = CursorFake()

    ContratoRepository._agrupar_adendos(cursor, "FROM contratos_adendos a", "WHERE a.ativo = 1", ["x"], "nome")

    assert "COALESCE(SUM(COALESCE(a.valor_recorrente, 0)), 0) AS total_recorrencia_adendos" in cursor.sql
    assert cursor.params == ("x",)


def test_filtros_adendos_dashboard_usam_data_do_adendo():
    where, params = ContratoRepository._filtros_adendos_dashboard(
        pesquisa="URCA",
        status="ATIVO",
        origem="OMIE",
        data_de="2026-08-01",
        data_ate="2026-08-31",
    )
    sql = "\n".join(where)

    assert "COALESCE(a.data_adendo, DATE(a.created_at)) >= %s" in sql
    assert "a.ativo = 1" in sql
    assert "COALESCE(a.data_adendo, DATE(a.created_at)) <= %s" in sql
    assert "c.status = %s" in sql
    assert "c.origem = %s" in sql
    assert params[-4:] == ["ATIVO", "OMIE", "2026-08-01", "2026-08-31"]


def test_combinar_resumo_dashboard_soma_adendos_separado():
    resumo = ContratoRepository._combinar_resumo_dashboard(
        {"total_contratos": 2, "total_recorrencia": Decimal("1000.00"), "total_usuarios": 10},
        {"total_adendos": 3, "total_recorrencia_adendos": Decimal("250.50"), "total_usuarios_adendos": 4},
    )

    assert resumo["total_contratos_principais"] == 2
    assert resumo["total_adendos"] == 3
    assert resumo["total_itens_contratos"] == 5
    assert resumo["total_recorrencia_contratos"] == Decimal("1000.00")
    assert resumo["total_recorrencia_adendos"] == Decimal("250.50")
    assert resumo["total_recorrencia"] == Decimal("1250.50")
    assert resumo["total_usuarios_contratos"] == 10
    assert resumo["total_usuarios_adendos"] == 4
    assert resumo["total_usuarios"] == 14


def test_combinar_agrupamento_dashboard_mescla_contratos_e_adendos():
    combinado = ContratoRepository._combinar_agrupamento_dashboard(
        [{"nome": "Executivo A", "total_contratos": 1, "total_recorrencia": Decimal("1000.00")}],
        [
            {"nome": "Executivo A", "total_adendos": 2, "total_recorrencia_adendos": Decimal("200.00")},
            {"nome": "Executivo B", "total_adendos": 1, "total_recorrencia_adendos": Decimal("300.00")},
        ],
    )

    assert combinado[0]["nome"] == "Executivo A"
    assert combinado[0]["total_contratos"] == 1
    assert combinado[0]["total_adendos"] == 2
    assert combinado[0]["total_itens_contratos"] == 3
    assert combinado[0]["total_recorrencia"] == Decimal("1200.00")
    assert combinado[1]["nome"] == "Executivo B"
    assert combinado[1]["total_contratos"] == 0
    assert combinado[1]["total_adendos"] == 1
