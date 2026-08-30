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

    assert "pe_omie.nome_normalizado = UPPER(TRIM(c.projeto_nome))" in sql
    assert "LEFT JOIN parceiros_executivos pe_manual" in sql
    assert "pe_manual.id = c.executivo_id" in sql
    assert "COALESCE(pe_omie.id, pe_manual.id) AS executivo_premiacao_id" in sql
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
    assert "UPPER(TRIM(pe_omie.nome)) COLLATE utf8mb4_unicode_ci = UPPER(TRIM(c.projeto_nome)) COLLATE utf8mb4_unicode_ci" in sql
    assert "AND pa.adendo_id = %s" in sql
    assert params == ("financeiro@o3cloud.com.br", 99)




def test_pagamento_campanhas_a_receber_filtra_apenas_lancado():
    sqls = []

    class RepoFake(FinanceiroRepository):
        @classmethod
        def fetch_all(cls, sql, params=()):
            sqls.append((sql, params))
            return []

    RepoFake.listar_pagamento_campanhas_itens({"status_manual": "A_RECEBER"})

    sql, params = sqls[0]
    assert "base.status_manual = 'LANCADO'" in sql
    assert "base.status_manual IN ('ABERTO', 'LANCADO')" not in sql
    assert params == (1000,)


def test_pagamento_campanhas_pago_filtra_pago_para_conferencia():
    sqls = []

    class RepoFake(FinanceiroRepository):
        @classmethod
        def fetch_all(cls, sql, params=()):
            sqls.append((sql, params))
            return []

    RepoFake.listar_pagamento_campanhas_itens({"status_manual": "PAGO"})

    sql, params = sqls[0]
    assert "base.status_manual = %s" in sql
    assert params == ("PAGO", 1000)


def test_pagamento_campanhas_agrupa_por_campanha_e_parceiro():
    itens = [
        {"campanha_id": 1, "campanha_nome": "Q1", "parceiro_id": 10, "parceiro_nome": "Parceiro", "valor_base": 100, "valor_premiacao_parceiro": 10, "valor_premiacao_executivo": 5, "valor_total_premiacao": 15},
        {"campanha_id": 2, "campanha_nome": "Q2", "parceiro_id": 10, "parceiro_nome": "Parceiro", "valor_base": 200, "valor_premiacao_parceiro": 20, "valor_premiacao_executivo": 10, "valor_total_premiacao": 30},
    ]

    grupos = FinanceiroService._agrupar_pagamentos_campanhas(itens)

    assert len(grupos) == 2
    assert {grupo["campanha_nome"] for grupo in grupos} == {"Q1", "Q2"}



def test_gerar_relatorio_pagamento_campanhas_pdf(monkeypatch):
    itens = [{
        "origem": "CONTRATO",
        "contrato_id": 1,
        "contrato_numero": "2026/001",
        "cliente_nome": "Cliente & Teste",
        "data_recebimento": "2026-08-30",
        "data_ativacao": "2026-08-01",
        "campanha_id": 7,
        "campanha_nome": "Q2",
        "status_manual": "LANCADO",
        "parceiro_id": 10,
        "parceiro_nome": "Parceiro",
        "executivo_id": 20,
        "executivo_nome": "Executivo",
        "valor_base": 100,
        "valor_premiacao_parceiro": 10,
        "valor_premiacao_executivo": 5,
        "valor_total_premiacao": 15,
    }]
    monkeypatch.setattr(
        "app.financeiro.service.FinanceiroRepository.listar_pagamento_campanhas_itens",
        lambda filtros: itens,
    )

    pdf = FinanceiroService.gerar_relatorio_pagamento_campanhas_pdf({"status_manual": "A_RECEBER"})

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000



def test_sql_pagamento_campanhas_usa_projeto_omie_case_insensitive_e_fallback_manual():
    sql = FinanceiroRepository._pagamento_campanhas_contratos_sql()

    assert "UPPER(TRIM(nome)) COLLATE utf8mb4_unicode_ci AS nome_normalizado" in sql
    assert "pe_omie.nome_normalizado = UPPER(TRIM(c.projeto_nome))" in sql
    assert "COALESCE(pe_omie.id, pe_manual.id) AS executivo_id" in sql
    assert "COALESCE(pe_omie.nome, pe_manual.nome) AS executivo_nome" in sql
    assert "CASE WHEN COALESCE(pe_omie.id, pe_manual.id) IS NOT NULL" in sql


def test_relatorios_gerais_ignoram_filtros_de_entidade():
    filtros = FinanceiroService.filtros_relatorio_geral_pagamento_campanhas({
        "q": "VR Interior Paulista",
        "campanha_id": 2,
        "parceiro_id": 10,
        "executivo_id": 20,
        "data_de": "2026-08-01",
        "data_ate": "2026-08-31",
    })

    assert filtros["q"] is None
    assert filtros["campanha_id"] is None
    assert filtros["parceiro_id"] is None
    assert filtros["executivo_id"] is None
    assert filtros["data_de"] == "2026-08-01"
    assert filtros["data_ate"] == "2026-08-31"


def test_corpo_email_preserva_variavel_desconhecida():
    corpo = FinanceiroService._aplicar_variaveis_email_pagamento(
        "Olá {parceiro}. Campo {personalizado}.",
        {"parceiro_nome": "Parceiro", "total_premiacao": 10},
        {},
    )

    assert corpo == "Olá Parceiro. Campo {personalizado}."


def test_filtros_pagamento_campanhas_reconhece_checkbox_marcado_com_campo_oculto():
    class DadosComValoresRepetidos(dict):
        def getlist(self, chave):
            return ["0", "1"] if chave == "incluir_adendos" else []

    filtros = FinanceiroService.filtros_pagamento_campanhas(DadosComValoresRepetidos())

    assert filtros["incluir_adendos"] == "1"


def test_filtros_pagamento_campanhas_mantem_checkbox_desmarcado():
    class DadosComCampoOculto(dict):
        def getlist(self, chave):
            return ["0"] if chave == "incluir_adendos" else []

    filtros = FinanceiroService.filtros_pagamento_campanhas(DadosComCampoOculto())

    assert filtros["incluir_adendos"] == "0"
