from app.implantacao.service import ImplantacaoService


IMPLANTACAO = {"id": 7, "titulo": "Projeto", "cliente_nome": "Cliente"}


def _patch_fluxo(monkeypatch, notificacoes, atualizacoes):
    monkeypatch.setattr(ImplantacaoService, "buscar_por_id", classmethod(lambda cls, implantacao_id: IMPLANTACAO))
    monkeypatch.setattr(ImplantacaoService, "_validar_anexos_comentario", classmethod(lambda cls, arquivos: None))
    monkeypatch.setattr(ImplantacaoService, "_registrar_historico", classmethod(lambda cls, *args, **kwargs: 99))
    monkeypatch.setattr(
        ImplantacaoService,
        "_salvar_anexos_comentario",
        classmethod(lambda cls, implantacao_id, historico_id, arquivos: [{"nome": "evidencia.pdf", "caminho": "/tmp/evidencia.pdf"}] if arquivos else []),
    )
    monkeypatch.setattr(
        ImplantacaoService,
        "_notificar_comentario",
        classmethod(lambda cls, implantacao, comentario, autor=None, anexos=None: notificacoes.append(list(anexos or [])) or {"enviado": True}),
    )

    class RepoFake:
        @classmethod
        def atualizar_email_historico(cls, historico_id, email_enviado=False, email_resultado=None):
            atualizacoes.append((historico_id, email_enviado, email_resultado))

    monkeypatch.setattr(ImplantacaoService, "repository", RepoFake)


def test_comentario_envia_anexos_no_email_quando_opcao_marcada(monkeypatch):
    notificacoes = []
    atualizacoes = []
    _patch_fluxo(monkeypatch, notificacoes, atualizacoes)

    email = ImplantacaoService.adicionar_comentario(
        7,
        {"comentario": "Segue evidência", "enviar_email": "on", "anexar_arquivos_email": "on"},
        arquivos=[object()],
    )

    assert email["enviado"] is True
    assert notificacoes == [[{"nome": "evidencia.pdf", "caminho": "/tmp/evidencia.pdf"}]]
    assert atualizacoes and atualizacoes[0][0] == 99


def test_comentario_nao_envia_anexos_no_email_quando_opcao_desmarcada(monkeypatch):
    notificacoes = []
    atualizacoes = []
    _patch_fluxo(monkeypatch, notificacoes, atualizacoes)

    ImplantacaoService.adicionar_comentario(
        7,
        {"comentario": "Segue evidência", "enviar_email": "on"},
        arquivos=[object()],
    )

    assert notificacoes == [[]]
    assert atualizacoes and atualizacoes[0][0] == 99


def test_comentario_com_anexo_sem_email_nao_notifica(monkeypatch):
    notificacoes = []
    atualizacoes = []
    _patch_fluxo(monkeypatch, notificacoes, atualizacoes)

    email = ImplantacaoService.adicionar_comentario(
        7,
        {"comentario": "Somente histórico", "anexar_arquivos_email": "on"},
        arquivos=[object()],
    )

    assert email is None
    assert notificacoes == []
    assert atualizacoes == []
