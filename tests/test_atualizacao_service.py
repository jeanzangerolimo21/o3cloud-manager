from app.configuracoes.atualizacao_service import AtualizacaoSistemaService


def test_estado_instalado_monta_dados_git(monkeypatch):
    respostas = {
        ("rev-parse", "--abbrev-ref", "HEAD"): "beta",
        ("rev-parse", "HEAD"): "abcdef123456",
        ("rev-parse", "--short", "HEAD"): "abcdef1",
        ("describe", "--tags", "--exact-match"): "v0.9.0-beta.1",
        ("describe", "--tags", "--abbrev=0"): "v0.9.0-beta.1",
        ("show", "-s", "--format=%cI", "HEAD"): "2026-08-11T13:00:00-03:00",
        ("show", "-s", "--format=%s", "HEAD"): "Release beta",
        ("config", "--get", "remote.origin.url"): "git@github.com:o3/o3cloud-manager.git",
        ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"): "origin/beta",
        ("rev-list", "--left-right", "--count", "@{upstream}...HEAD"): "0\t1",
        ("status", "--short"): "",
        ("tag", "--sort=-creatordate"): "v0.9.0-beta.1\nv0.8.0",
    }
    monkeypatch.setattr(AtualizacaoSistemaService, "_git", classmethod(lambda cls, args: respostas.get(tuple(args))))

    estado = AtualizacaoSistemaService.estado_instalado()

    assert estado["branch"] == "beta"
    assert estado["commit_curto"] == "abcdef1"
    assert estado["tag_atual"] == "v0.9.0-beta.1"
    assert estado["divergencia"]["ahead"] == 1
    assert estado["worktree_limpa"] is True
    assert estado["tags_recentes"] == ["v0.9.0-beta.1", "v0.8.0"]


def test_estado_instalado_detecta_worktree_com_alteracoes(monkeypatch):
    def fake_git(cls, args):
        if args == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return "HEAD"
        if args == ["status", "--short"]:
            return " M app.py\n?? novo.txt"
        return None

    monkeypatch.setattr(AtualizacaoSistemaService, "_git", classmethod(fake_git))

    estado = AtualizacaoSistemaService.estado_instalado()

    assert estado["detached"] is True
    assert estado["branch"] is None
    assert estado["worktree_limpa"] is False
    assert estado["alteracoes"] == [" M app.py", "?? novo.txt"]
