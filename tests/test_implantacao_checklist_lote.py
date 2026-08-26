from werkzeug.datastructures import MultiDict

from app.implantacao.service import ImplantacaoService


class RepoChecklistFake:
    itens = {
        11: {"id": 11, "implantacao_id": 5},
        12: {"id": 12, "implantacao_id": 5},
        99: {"id": 99, "implantacao_id": 8},
    }
    atualizados = []
    percentual = []

    @classmethod
    def reset(cls):
        cls.atualizados = []
        cls.percentual = []

    @classmethod
    def buscar_por_id(cls, implantacao_id):
        return {"id": implantacao_id} if implantacao_id == 5 else None

    @classmethod
    def buscar_item_checklist(cls, item_id):
        return cls.itens.get(item_id)

    @classmethod
    def atualizar_item_checklist(cls, item_id, dados):
        cls.atualizados.append((item_id, dados))

    @classmethod
    def atualizar_percentual(cls, implantacao_id):
        cls.percentual.append(implantacao_id)


def test_atualizar_itens_checklist_salva_somente_selecionados(monkeypatch):
    RepoChecklistFake.reset()
    monkeypatch.setattr(ImplantacaoService, "repository", RepoChecklistFake)
    dados = MultiDict([
        ("item_ids", "11"),
        ("item_ids", "12"),
        ("status_11", "CONCLUIDO"),
        ("responsavel_11", " Ana "),
        ("evidencia_11", " OK "),
        ("status_12", "NAO_APLICAVEL"),
        ("responsavel_12", ""),
        ("evidencia_12", "Sem escopo"),
    ])

    total = ImplantacaoService.atualizar_itens_checklist(5, dados)

    assert total == 2
    assert RepoChecklistFake.atualizados == [
        (11, {"status": "CONCLUIDO", "responsavel": "Ana", "evidencia": "OK"}),
        (12, {"status": "NAO_APLICAVEL", "responsavel": None, "evidencia": "Sem escopo"}),
    ]
    assert RepoChecklistFake.percentual == [5]


def test_atualizar_itens_checklist_recusa_item_de_outra_implantacao(monkeypatch):
    RepoChecklistFake.reset()
    monkeypatch.setattr(ImplantacaoService, "repository", RepoChecklistFake)
    dados = MultiDict([("item_ids", "99"), ("status_99", "CONCLUIDO")])

    try:
        ImplantacaoService.atualizar_itens_checklist(5, dados)
    except ValueError as erro:
        assert "inválido" in str(erro)
    else:
        raise AssertionError("deveria recusar item de outra implantação")

    assert RepoChecklistFake.atualizados == []
    assert RepoChecklistFake.percentual == []
