from decimal import Decimal

from app.contratos.service import ContratoService


class ClienteRepoFake:
    cliente = {"id": 10, "codigo_externo": 1001, "cnpj": "12345678000190"}

    @classmethod
    def buscar_por_codigo_externo(cls, codigo_externo):
        if codigo_externo == cls.cliente["codigo_externo"]:
            return cls.cliente
        return None


class ContratoRepoFake:
    contrato_por_codigo = {}
    omie_ativo = None
    atualizados = []
    inseridos = []
    duplicados_desativados = []
    ausentes = []

    @classmethod
    def buscar_por_codigo_externo(cls, codigo_externo):
        return cls.contrato_por_codigo.get(codigo_externo)

    @classmethod
    def buscar_manual_por_numero(cls, cliente_id, numero):
        return None

    @classmethod
    def buscar_assinado_sem_codigo_por_cliente_valor(cls, cliente_id, valor_mensal):
        return None

    @classmethod
    def buscar_omie_ativo_por_cliente(cls, cliente_id):
        return cls.omie_ativo

    @classmethod
    def atualizar_sync(cls, contrato_id, dados):
        cls.atualizados.append((contrato_id, dados.copy()))

    @classmethod
    def inserir(cls, dados):
        cls.inseridos.append(dados.copy())
        return 99

    @classmethod
    def desativar_omie_ativos_por_cliente(cls, cliente_id, manter_id):
        cls.duplicados_desativados.append((cliente_id, manter_id))
        return 1

    @classmethod
    def desativar_omie_ativos_ausentes(cls, codigos_externos):
        cls.ausentes.append(set(codigos_externos))
        return 2


class ReajusteFake:
    historicos = []

    @classmethod
    def registrar_historico_valor_se_necessario(cls, contrato_id, dados, origem="SISTEMA"):
        cls.historicos.append((contrato_id, dados.copy(), origem))


def _contrato_omie(codigo=222, cliente=1001, numero="CTR-222"):
    return {
        "cabecalho": {
            "nCodCtr": codigo,
            "nCodCli": cliente,
            "cNumCtr": numero,
            "cCodSit": "10",
            "nValTotMes": "150.00",
        },
        "infAdic": {},
        "observacoes": {},
        "itensContrato": [],
    }


def setup_function():
    import app.contratos.service as service_mod
    import app.financeiro.reajuste_service as reajuste_mod

    service_mod.ClienteRepository = ClienteRepoFake
    service_mod.ContratoRepository = ContratoRepoFake
    reajuste_mod.ReajusteContratoService = ReajusteFake

    ContratoRepoFake.contrato_por_codigo = {}
    ContratoRepoFake.omie_ativo = None
    ContratoRepoFake.atualizados = []
    ContratoRepoFake.inseridos = []
    ContratoRepoFake.duplicados_desativados = []
    ContratoRepoFake.ausentes = []
    ReajusteFake.historicos = []


def test_sincronizar_contrato_reaproveita_omie_ativo_do_mesmo_cliente():
    ContratoRepoFake.omie_ativo = {"id": 55, "cliente_id": 10, "codigo_externo": 111}

    resultado = ContratoService.sincronizar_contrato(_contrato_omie(codigo=222))

    assert resultado["status"] == "UPDATE"
    assert resultado["duplicados_desativados"] == 1
    assert not ContratoRepoFake.inseridos
    assert ContratoRepoFake.atualizados[0][0] == 55
    assert ContratoRepoFake.atualizados[0][1]["codigo_externo"] == 222
    assert ContratoRepoFake.duplicados_desativados == [(10, 55)]
    assert ReajusteFake.historicos[0][0] == 55
    assert ReajusteFake.historicos[0][2] == "OMIE"


def test_desativar_contratos_omie_ausentes_repassa_codigos_vistos():
    total = ContratoService.desativar_contratos_omie_ausentes({111, 222})

    assert total == 2
    assert ContratoRepoFake.ausentes == [{111, 222}]


def test_sincronizar_contrato_preenche_vinculos_comerciais_do_omie():
    chave_vendedor = ContratoService._normalizar_nome_vinculo("VR BH")
    chave_parceiro = ContratoService._normalizar_nome_vinculo("VR SOFTWARE BELO HORIZONTE")
    chave_executivo = ContratoService._normalizar_nome_vinculo("Projeto Alpha")
    vinculos_cache = {
        "vendedores_omie": {chave_vendedor: "VR SOFTWARE BELO HORIZONTE"},
        "parceiros": {chave_parceiro: {"id": 7, "nome": "VR SOFTWARE BELO HORIZONTE"}},
        "executivos": {chave_executivo: {"id": 8, "nome": "Projeto Alpha"}},
    }

    resultado = ContratoService.sincronizar_contrato(
        {
            "cabecalho": {
                "nCodCtr": 333,
                "nCodCli": 1001,
                "cNumCtr": "CTR-333",
                "cCodSit": "10",
                "nValTotMes": "150.00",
            },
            "infAdic": {"nCodVend": 1, "nCodProj": 2},
            "observacoes": {},
            "itensContrato": [],
        },
        vendedores_cache={1: "VR BH"},
        projetos_cache={2: "Projeto Alpha"},
        vinculos_cache=vinculos_cache,
    )

    assert resultado["status"] == "INSERT"
    assert ContratoRepoFake.inseridos[0]["parceiro_id"] == 7
    assert ContratoRepoFake.inseridos[0]["executivo_id"] == 8


def test_resolver_vinculo_vendedor_omie_por_prefixo_da_planilha():
    cache = {
        "vendedores_omie": {
            ContratoService._normalizar_nome_vinculo("JRS SISTEMAS"): "O3 CLOUD"
        },
        "parceiros": {
            ContratoService._normalizar_nome_vinculo("O3 CLOUD"): {"id": 7}
        },
        "executivos": {},
    }

    vinculos = ContratoService._resolver_vinculos_comerciais_omie("JRS", None, cache)

    assert vinculos["parceiro_id"] == 7
    assert vinculos["executivo_id"] is None
