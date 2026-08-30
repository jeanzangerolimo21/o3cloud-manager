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
    contrato_por_id = {
        77: {
            "id": 77,
            "cliente_id": 10,
            "cliente_codigo_externo": 1001,
            "codigo_externo": 222,
            "numero": "CTR-222",
            "data_fechamento": None,
            "inicio_vigencia": None,
        }
    }
    setup_updates = []

    @classmethod
    def buscar_por_codigo_externo(cls, codigo_externo):
        return cls.contrato_por_codigo.get(codigo_externo)

    @classmethod
    def buscar_por_id(cls, contrato_id):
        return cls.contrato_por_id.get(contrato_id)

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

    @classmethod
    def atualizar_setup_omie(cls, contrato_id, dados):
        cls.setup_updates.append((contrato_id, dados.copy()))

    @classmethod
    def listar_para_setup_omie(cls, limit=1000):
        return list(cls.contrato_por_id.values())


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
    ContratoRepoFake.contrato_por_id = {
        77: {
            "id": 77,
            "cliente_id": 10,
            "cliente_codigo_externo": 1001,
            "codigo_externo": 222,
            "numero": "CTR-222",
            "data_fechamento": None,
            "inicio_vigencia": None,
        }
    }
    ContratoRepoFake.setup_updates = []
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


def test_email_adendo_usuarios_nao_expoe_valor_recorrente(monkeypatch):
    envios = []
    monkeypatch.setattr(
        "app.contratos.service.EmailService.enviar",
        lambda assunto, corpo, destinatarios: envios.append((assunto, corpo, destinatarios)) or {"enviado": True},
    )

    resultado = ContratoService._enviar_email_adendo_usuarios(
        {
            "id": 77,
            "numero": "CTR-222",
            "cliente_nome": "Cliente Teste",
            "cliente_cnpj": "12345678000190",
        },
        {
            "titulo": "Adendo usuarios",
            "numero_adendo": "AD-001",
            "valor_recorrente": Decimal("435.00"),
        },
        3,
        "comercial@o3cloud.com.br",
    )

    assert resultado["enviado"] is True
    assert envios[0][2] == ["sac@o3cloud.com.br"]
    assert "Quantidade adicional: 3" in envios[0][1]
    assert "Valor recorrente" not in envios[0][1]
    assert "435.00" not in envios[0][1]


class OmieOSFake:
    def __init__(self, ordens):
        self.ordens = ordens
        self.status_calls = []

    def listar_ordens_servico(self, pagina=1, filtros=None):
        return {"osCadastro": self.ordens, "total_de_paginas": 1}

    def status_ordem_servico(self, codigo_os):
        self.status_calls.append(codigo_os)
        return {"nCodOS": codigo_os, "cFaturada": "S", "dDtFat": "20/08/2026", "nValorTot": 1250.50}


def _os(codigo, numero, descricao, valor="100.00", parcelas=1, faturada="N", cancelada="N"):
    return {
        "Cabecalho": {
            "nCodOS": codigo,
            "cNumOS": numero,
            "nCodCli": 1001,
            "nValorTotal": valor,
            "nQtdeParc": parcelas,
            "cEtapa": "50",
        },
        "InfoCadastro": {"cFaturada": faturada, "cCancelada": cancelada},
        "ServicosPrestados": [{"cDescServ": descricao, "nQtde": 1, "nValUnit": valor}],
    }


def test_sincronizar_setup_omie_marca_nao_encontrado_quando_cliente_sem_os():
    resultado = ContratoService.sincronizar_setup_omie(77, OmieOSFake([]))

    assert resultado["setup_omie_status"] == "NAO_ENCONTRADO"
    assert ContratoRepoFake.setup_updates[0][0] == 77
    assert ContratoRepoFake.setup_updates[0][1]["valor_setup"] is None


def test_sincronizar_setup_omie_atualiza_valor_parcelas_e_status_faturado():
    omie = OmieOSFake([_os(900, "OS-900", "Setup implantacao O3", "1250.50", 3)])

    resultado = ContratoService.sincronizar_setup_omie(77, omie)

    assert resultado["setup_omie_status"] == "FATURADO"
    assert resultado["setup_omie_numero_os"] == "OS-900"
    assert resultado["setup_omie_parcelas"] == 3
    assert resultado["valor_setup"] == Decimal("1250.50")
    assert omie.status_calls == [900]
    assert ContratoRepoFake.setup_updates[0][1]["setup_omie_faturamento_status"] == "FATURADO"


def test_selecionar_ordem_servico_setup_prioriza_descricao_de_setup():
    ordens = [
        _os(901, "OS-901", "Treinamento avulso", "500.00", 1),
        _os(902, "OS-902", "Projeto e instalacao inicial", "1200.00", 2),
    ]

    escolhida = ContratoService._selecionar_ordem_servico_setup(ContratoRepoFake.contrato_por_id[77], ordens)

    assert escolhida["Cabecalho"]["nCodOS"] == 902


def test_sincronizar_setups_omie_processa_lote_com_cache_por_cliente():
    ContratoRepoFake.contrato_por_id = {
        77: ContratoRepoFake.contrato_por_id[77],
        78: {**ContratoRepoFake.contrato_por_id[77], "id": 78, "numero": "CTR-223"},
    }
    omie = OmieOSFake([_os(900, "OS-900", "Setup implantacao O3", "1250.50", 3)])

    resultado = ContratoService.sincronizar_setups_omie(omie_client=omie)

    assert resultado["status"] == "OK"
    assert resultado["processados"] == 2
    assert resultado["atualizados"] == 2
    assert len(ContratoRepoFake.setup_updates) == 2
    assert len(omie.status_calls) == 2
