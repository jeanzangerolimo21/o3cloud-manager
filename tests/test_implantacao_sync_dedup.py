import pytest

from app.implantacao.service import ImplantacaoService


class RepoImplantacaoFake:
    contratos = []
    por_contrato = {}
    por_cliente = {}
    criadas = []
    limpou_inativos = 0
    limpou_duplicadas = 0

    @classmethod
    def desativar_por_contratos_omie_inativos(cls):
        cls.limpou_inativos += 1
        return 1

    @classmethod
    def desativar_duplicadas_por_cliente(cls):
        cls.limpou_duplicadas += 1
        return 1

    @classmethod
    def listar_contratos_elegiveis(cls):
        return cls.contratos

    @classmethod
    def buscar_por_contrato_id(cls, contrato_id):
        return cls.por_contrato.get(contrato_id)

    @classmethod
    def buscar_por_cliente_id(cls, cliente_id):
        return cls.por_cliente.get(cliente_id)


def setup_function():
    ImplantacaoService.repository = RepoImplantacaoFake
    RepoImplantacaoFake.contratos = []
    RepoImplantacaoFake.por_contrato = {}
    RepoImplantacaoFake.por_cliente = {}
    RepoImplantacaoFake.criadas = []
    RepoImplantacaoFake.limpou_inativos = 0
    RepoImplantacaoFake.limpou_duplicadas = 0


def test_sincronizar_contratos_encaminhados_limpa_e_nao_duplica_cliente(monkeypatch):
    RepoImplantacaoFake.contratos = [
        {"id": 10, "cliente_id": 100},
        {"id": 11, "cliente_id": 200},
    ]
    RepoImplantacaoFake.por_cliente = {100: {"id": 50, "cliente_id": 100}}

    def criar(cls, dados):
        RepoImplantacaoFake.criadas.append(dados.copy())
        return 900 + dados["contrato_id"]

    monkeypatch.setattr(ImplantacaoService, "criar", classmethod(criar))

    criadas = ImplantacaoService.sincronizar_contratos_encaminhados()

    assert RepoImplantacaoFake.limpou_inativos == 1
    assert RepoImplantacaoFake.limpou_duplicadas == 1
    assert RepoImplantacaoFake.criadas == [{"contrato_id": 11, "etapa_kanban": "FILA"}]
    assert criadas == [911]


def test_sincronizar_contratos_encaminhados_nao_duplica_contrato(monkeypatch):
    RepoImplantacaoFake.contratos = [{"id": 10, "cliente_id": 100}]
    RepoImplantacaoFake.por_contrato = {10: {"id": 60, "contrato_id": 10}}

    monkeypatch.setattr(ImplantacaoService, "criar", classmethod(lambda cls, dados: pytest.fail("nao deve criar")))

    assert ImplantacaoService.sincronizar_contratos_encaminhados() == []
