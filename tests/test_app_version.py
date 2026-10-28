from types import SimpleNamespace

from app.core import version


def test_versao_configurada_por_ambiente_tem_prioridade(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "v9.8.7")

    assert version.obter_versao_aplicacao() == "v9.8.7"


def test_versao_e_obtida_da_tag_git(monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    monkeypatch.setattr(
        version.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout="v1.2.7\n"),
    )

    assert version.obter_versao_aplicacao() == "v1.2.7"


def test_versao_possui_fallback_quando_git_indisponivel(monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)

    def falhar(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(version.subprocess, "run", falhar)

    assert version.obter_versao_aplicacao() == "versão não identificada"
