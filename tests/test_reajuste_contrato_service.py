from datetime import date, datetime
from decimal import Decimal

from werkzeug.datastructures import MultiDict

from app.financeiro.reajuste_service import ReajusteContratoService


class RepoReajustesFake:
    contratos = []
    historicos = {}
    faturamentos = {}
    ultimo = {}
    alertas = {}
    inseridos = []
    usuarios = []
    usuarios_configurados = []
    config = {
        "id": 1,
        "ativo": 1,
        "alerta_30_dias": 1,
        "alerta_15_dias": 1,
        "alerta_7_dias": 1,
        "enviar_email": 0,
    }

    @classmethod
    def configuracao(cls):
        return cls.config

    @classmethod
    def listar_contratos_monitoramento(cls, filtros=None, limit=500):
        return cls.contratos[:limit]

    @classmethod
    def total_contratos_monitoramento(cls):
        return len(cls.contratos)

    @classmethod
    def primeiro_faturamento_contrato(cls, contrato_id):
        return cls.faturamentos.get(contrato_id)

    @classmethod
    def historico_contrato(cls, contrato_id):
        return cls.historicos.get(contrato_id, [])

    @classmethod
    def ultimo_historico(cls, contrato_id):
        return cls.ultimo.get(contrato_id)

    @classmethod
    def inserir_historico(cls, contrato_id, dados, origem="SISTEMA"):
        cls.inseridos.append((contrato_id, dados, origem))
        cls.ultimo[contrato_id] = {**dados, "origem": origem}
        return len(cls.inseridos)

    @classmethod
    def alerta_existente(cls, contrato_id, aniversario, antecedencia):
        return cls.alertas.get((contrato_id, aniversario, antecedencia))

    @classmethod
    def inserir_alerta(cls, contrato_id, aniversario, antecedencia, status, exibido=True):
        cls.alertas[(contrato_id, aniversario, antecedencia)] = {
            "contrato_id": contrato_id,
            "aniversario_referencia": aniversario,
            "antecedencia_dias": antecedencia,
            "status": status,
            "email_enviado_em": None,
        }
        return len(cls.alertas)

    @classmethod
    def usuarios_notificacao(cls, config_id=None):
        return cls.usuarios

    @classmethod
    def usuarios_disponiveis(cls):
        return cls.usuarios

    @classmethod
    def salvar_configuracao(cls, dados):
        cls.config = {**cls.config, **dados}
        return cls.config.get("id")

    @classmethod
    def substituir_usuarios_configuracao(cls, config_id, usuario_ids):
        cls.usuarios_configurados = usuario_ids


    @classmethod
    def marcar_email_alerta(cls, contrato_id, aniversario, antecedencia):
        cls.alertas[(contrato_id, aniversario, antecedencia)]["email_enviado_em"] = datetime.now()
        return True


def _contrato(**extra):
    dados = {
        "id": 1,
        "numero": "2025/001",
        "status": "ATIVO",
        "inicio_vigencia": date(2025, 9, 15),
        "valor_mensal": Decimal("1000.00"),
        "valor_servicos_bruto": None,
        "valor_descontos": None,
        "valor_servicos_liquido": None,
        "cliente_nome": "Cliente A",
    }
    dados.update(extra)
    return dados


def setup_function():
    ReajusteContratoService.repository = RepoReajustesFake
    RepoReajustesFake.contratos = []
    RepoReajustesFake.historicos = {}
    RepoReajustesFake.faturamentos = {}
    RepoReajustesFake.ultimo = {}
    RepoReajustesFake.alertas = {}
    RepoReajustesFake.inseridos = []
    RepoReajustesFake.usuarios = []
    RepoReajustesFake.usuarios_configurados = []
    RepoReajustesFake.config = {
        "id": 1,
        "ativo": 1,
        "alerta_30_dias": 1,
        "alerta_15_dias": 1,
        "alerta_7_dias": 1,
        "enviar_email": 0,
    }


def test_calcula_proximo_aniversario_para_varios_anos():
    inicio = date(2022, 9, 15)

    assert ReajusteContratoService.calcular_proximo_aniversario(inicio, date(2026, 8, 14)) == date(2026, 9, 15)
    assert ReajusteContratoService.calcular_proximo_aniversario(inicio, date(2026, 9, 15)) == date(2026, 9, 15)
    assert ReajusteContratoService.calcular_proximo_aniversario(inicio, date(2026, 9, 16)) == date(2027, 9, 15)


def test_janelas_de_alerta_30_15_7():
    assert ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=date(2025, 9, 13)), hoje=date(2026, 8, 14))["situacao"] == "REAJUSTE_PROXIMO"
    assert ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=date(2025, 8, 29)), hoje=date(2026, 8, 14))["dias_para_reajuste"] == 15
    assert ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=date(2025, 8, 21)), hoje=date(2026, 8, 14))["dias_para_reajuste"] == 7


def test_sem_data_e_suspenso_nao_geram_alerta_operacional():
    assert ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=None), hoje=date(2026, 8, 14))["situacao"] == "SEM_DATA_VIGENCIA"
    assert ReajusteContratoService.analisar_contrato(_contrato(status="SUSPENSO"), hoje=date(2026, 8, 14))["situacao"] == "IGNORADO"


def test_contrato_vencido_sem_historico_fica_sem_base_comparacao():
    item = ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=date(2025, 8, 13)), hoje=date(2026, 8, 14))

    assert item["situacao"] == "SEM_BASE_COMPARACAO"


def test_contrato_sem_valor_positivo_fica_sem_base_comparacao():
    item = ReajusteContratoService.analisar_contrato(_contrato(valor_mensal=Decimal("0.00")), hoje=date(2026, 8, 14))

    assert item["situacao"] == "SEM_BASE_COMPARACAO"


def test_sem_base_informa_tempo_sem_alteracao_detectada_desde_vigencia():
    item = ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=date(2020, 3, 1)), hoje=date(2026, 8, 14))

    assert item["situacao"] == "SEM_BASE_COMPARACAO"
    assert item["tempo_sem_alteracao_meses"] == 77
    assert item["tempo_sem_alteracao_label"] == "6 ano(s) e 5 mes(es)"
    assert item["sem_base_investigar"] is True
    assert item["situacao_label"] == "Sem base - investigar"
    assert item["situacao_class"] == "danger"


def test_faturamento_inicial_igual_ao_atual_detecta_sem_reajuste():
    RepoReajustesFake.faturamentos = {
        1: {"valor_original": Decimal("541.94"), "data_recebimento": date(2026, 3, 1)}
    }

    item = ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=date(2020, 3, 1), valor_mensal=Decimal("541.94")), hoje=date(2026, 8, 14))

    assert item["situacao"] == "SEM_REAJUSTE_DETECTADO"
    assert item["valor_referencia"] == Decimal("541.94")
    assert item["valor_referencia_origem"] == "FATURAMENTO_INICIAL"
    assert item["percentual_variacao"] == Decimal("0.00")


def test_faturamento_inicial_menor_que_atual_detecta_reajuste():
    RepoReajustesFake.faturamentos = {
        1: {"valor_original": Decimal("1000.00"), "data_recebimento": date(2026, 3, 1)}
    }

    item = ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=date(2020, 3, 1), valor_mensal=Decimal("1100.00")), hoje=date(2026, 8, 14))

    assert item["situacao"] == "REAJUSTADO"
    assert item["percentual_variacao"] == Decimal("10.00")


def test_faturamento_inicial_maior_que_atual_tambem_detecta_alteracao():
    RepoReajustesFake.faturamentos = {
        1: {"valor_original": Decimal("1000.00"), "data_recebimento": date(2026, 3, 1)}
    }

    item = ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=date(2020, 3, 1), valor_mensal=Decimal("900.00")), hoje=date(2026, 8, 14))

    assert item["situacao"] == "REAJUSTADO"
    assert item["percentual_variacao"] == Decimal("-10.00")


def test_faturamento_anterior_ao_corte_de_marco_2026_e_ignorado():
    RepoReajustesFake.faturamentos = {
        1: {"valor_original": Decimal("1000.00"), "data_recebimento": date(2026, 2, 28)}
    }

    item = ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=date(2020, 3, 1), valor_mensal=Decimal("1000.00")), hoje=date(2026, 8, 14))

    assert item["situacao"] == "SEM_BASE_COMPARACAO"
    assert item["valor_referencia_origem"] == "VALOR_CONTRATO_INICIAL"


def test_historico_com_aumento_detecta_reajustado():
    RepoReajustesFake.historicos = {
        1: [
            {"detectado_em": datetime(2026, 8, 1), "valor_mensal": Decimal("1000.00")},
            {"detectado_em": datetime(2026, 8, 14), "valor_mensal": Decimal("1050.00")},
        ]
    }

    item = ReajusteContratoService.analisar_contrato(_contrato(inicio_vigencia=date(2025, 8, 10)), hoje=date(2026, 8, 14))

    assert item["situacao"] == "REAJUSTADO"
    assert item["percentual_variacao"] == Decimal("5.00")


def test_registra_historico_somente_quando_valor_muda():
    RepoReajustesFake.ultimo = {1: {"valor_mensal": Decimal("1000.00"), "valor_servicos_bruto": None, "valor_descontos": None, "valor_servicos_liquido": None}}

    assert ReajusteContratoService.registrar_historico_valor_se_necessario(1, _contrato(), origem="OMIE") is None
    assert ReajusteContratoService.registrar_historico_valor_se_necessario(1, _contrato(valor_mensal=Decimal("1100.00")), origem="OMIE") == 1


def test_salvar_configuracao_grava_somente_usuarios_selecionados():
    dados = MultiDict([
        ("ativo", "1"),
        ("alerta_30_dias", "1"),
        ("alerta_15_dias", "1"),
        ("alerta_7_dias", "1"),
        ("enviar_email", "1"),
        ("usuario_ids", "3"),
        ("usuario_ids", "7"),
    ])

    ReajusteContratoService.salvar_configuracao(dados, "financeiro@example.com")

    assert RepoReajustesFake.usuarios_configurados == [3, 7]


def test_contexto_expoe_total_monitorado_independente_do_filtro_de_situacao():
    RepoReajustesFake.contratos = [
        _contrato(id=1, inicio_vigencia=date(2020, 3, 1)),
        _contrato(id=2, inicio_vigencia=date(2026, 12, 1)),
    ]

    contexto = ReajusteContratoService.contexto({"situacao": "SEM_BASE_COMPARACAO"}, hoje=date(2026, 8, 14))

    assert contexto["total_monitorados"] == 2
    assert len(contexto["itens"]) == 1


def test_processar_alertas_nao_duplica_mesmo_aniversario():
    contrato = _contrato(inicio_vigencia=date(2025, 9, 13))
    RepoReajustesFake.contratos = [contrato]

    primeiro = ReajusteContratoService.processar_alertas(hoje=date(2026, 8, 14))
    segundo = ReajusteContratoService.processar_alertas(hoje=date(2026, 8, 14))

    assert primeiro["criados"] == 1
    assert segundo["criados"] == 0
    assert len(RepoReajustesFake.alertas) == 1
