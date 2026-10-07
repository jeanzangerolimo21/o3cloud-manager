from decimal import Decimal

from app.implantacao.service import ImplantacaoService
from app.repositories.implantacao_workflow_repository import ImplantacaoWorkflowRepository


class RepositoryFake:
    existente = None
    payload = None
    percentual = None

    @classmethod
    def buscar_por_adendo_id(cls, adendo_id):
        return cls.existente

    @classmethod
    def inserir(cls, dados):
        cls.payload = dados
        return 321

    @classmethod
    def atualizar_percentual(cls, implantacao_id):
        cls.percentual = implantacao_id


def _adendo():
    return {
        "id": 55,
        "contrato_id": 10,
        "cliente_id": 20,
        "cliente_nome": "Cliente Exemplo",
        "titulo": "Novo servidor ERP",
        "numero_adendo": "AD-009",
        "valor_setup": Decimal("1500.00"),
        "observacoes": "Provisionar servidor adicional.",
    }


def _contrato():
    return {
        "id": 10,
        "ativo": 1,
        "cliente_id": 20,
        "cliente_nome": "Cliente Exemplo",
        "numero": "CT-100",
        "proposta_id": None,
        "executivo_id": 3,
        "parceiro_id": 4,
    }


def test_iniciar_por_adendo_cria_card_na_fila_sem_alterar_contrato(monkeypatch):
    RepositoryFake.existente = None
    RepositoryFake.payload = None
    RepositoryFake.percentual = None
    historicos = []
    monkeypatch.setattr(ImplantacaoService, "repository", RepositoryFake)
    monkeypatch.setattr("app.implantacao.service.ContratoAdendoRepository.buscar_por_id", lambda adendo_id: _adendo())
    monkeypatch.setattr("app.implantacao.service.ContratoRepository.buscar_por_id", lambda contrato_id: _contrato())
    monkeypatch.setattr("app.implantacao.service.InadimplenciaService.validar_operacao_cliente", lambda cliente_id: None)
    monkeypatch.setattr(ImplantacaoService, "kanban_labels", classmethod(lambda cls: {"FILA": "Fila"}))
    monkeypatch.setattr(ImplantacaoService, "_criar_checklist_padrao", classmethod(lambda cls, implantacao_id: None))
    monkeypatch.setattr(ImplantacaoService, "_registrar_historico", classmethod(lambda cls, *args, **kwargs: historicos.append((args, kwargs))))

    implantacao_id, criada = ImplantacaoService.iniciar_por_adendo(55, {
        "titulo": "Implantar novo ERP",
        "prioridade": "ALTA",
        "data_prevista_entrega": "2026-11-15",
    })

    assert (implantacao_id, criada) == (321, True)
    assert RepositoryFake.payload["contrato_id"] == 10
    assert RepositoryFake.payload["adendo_id"] == 55
    assert RepositoryFake.payload["origem"] == "ADENDO"
    assert RepositoryFake.payload["etapa_kanban"] == "FILA"
    assert RepositoryFake.payload["status"] == "AGUARDANDO_INICIO"
    assert RepositoryFake.payload["prioridade"] == "ALTA"
    assert "1500.00" in RepositoryFake.payload["provisionamento_notas"]
    assert RepositoryFake.percentual == 321
    assert historicos


def test_iniciar_por_adendo_reutiliza_implantacao_existente(monkeypatch):
    RepositoryFake.existente = {"id": 999}
    monkeypatch.setattr(ImplantacaoService, "repository", RepositoryFake)
    monkeypatch.setattr("app.implantacao.service.ContratoAdendoRepository.buscar_por_id", lambda adendo_id: _adendo())

    assert ImplantacaoService.iniciar_por_adendo(55, {}) == (999, False)


def test_migration_remove_unicidade_por_contrato_e_cria_vinculo_adendo():
    sql = open("database/migrations/136_implantacao_por_adendo.sql", encoding="utf-8").read()

    assert "DROP INDEX IF EXISTS uk_implantacoes_contrato_ativo" in sql
    assert "ADD COLUMN IF NOT EXISTS adendo_id" in sql
    assert "uk_implantacoes_adendo (adendo_id)" in sql
    assert "GENERATED ALWAYS" not in sql
    assert "ADD COLUMN IF NOT EXISTS valor_setup" in sql


def test_repository_insere_origem_e_adendo(monkeypatch):
    capturado = {}

    def inserir(cls, sql, params=None):
        capturado.update({"sql": sql, "params": params})
        return 44

    monkeypatch.setattr(ImplantacaoWorkflowRepository, "execute_insert", classmethod(inserir))
    monkeypatch.setattr(ImplantacaoWorkflowRepository, "generate_uuid", staticmethod(lambda: "uuid-teste"))

    resultado = ImplantacaoWorkflowRepository.inserir({
        "contrato_id": 10,
        "adendo_id": 55,
        "origem": "ADENDO",
        "cliente_id": 20,
        "titulo": "Novo servidor",
        "status": "AGUARDANDO_INICIO",
        "etapa_kanban": "FILA",
        "prioridade": "NORMAL",
        "provisionamento_status": "NAO_PLANEJADO",
    })

    assert resultado == 44
    assert "adendo_id, origem" in capturado["sql"]
    assert capturado["params"][1:4] == (10, 55, "ADENDO")
    assert capturado["sql"].count("%s") == len(capturado["params"])


def test_busca_principal_por_cliente_ignora_cards_de_adendo(monkeypatch):
    capturado = {}

    def buscar(cls, sql, params=None):
        capturado["sql"] = sql
        return None

    monkeypatch.setattr(ImplantacaoWorkflowRepository, "fetch_one", classmethod(buscar))

    ImplantacaoWorkflowRepository.buscar_por_cliente_id(20)

    assert "i.adendo_id IS NULL" in capturado["sql"]
