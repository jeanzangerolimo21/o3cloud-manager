from app.implantacao.service import ImplantacaoService
from werkzeug.datastructures import MultiDict


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
        classmethod(lambda cls, implantacao, comentario, autor=None, anexos=None, destinatarios=None: notificacoes.append({"anexos": list(anexos or []), "destinatarios": destinatarios}) or {"enviado": True}),
    )

    class RepoFake:
        preferencias = []

        @classmethod
        def atualizar_email_historico(cls, historico_id, email_enviado=False, email_resultado=None):
            atualizacoes.append((historico_id, email_enviado, email_resultado))

        @classmethod
        def atualizar_emails_excluidos_interacoes(cls, implantacao_id, emails_excluidos):
            cls.preferencias.append((implantacao_id, emails_excluidos))

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
    assert notificacoes == [{"anexos": [{"nome": "evidencia.pdf", "caminho": "/tmp/evidencia.pdf"}], "destinatarios": None}]
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

    assert notificacoes == [{"anexos": [], "destinatarios": None}]
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


def test_comentario_envia_somente_para_destinatarios_selecionados(monkeypatch):
    notificacoes = []
    atualizacoes = []
    implantacao = {
        **IMPLANTACAO,
        "cliente_email": "financeiro@cliente.com",
        "contato_email": "tecnico@cliente.com",
        "emails_adicionais": "projetos@o3cloud.com.br",
    }
    _patch_fluxo(monkeypatch, notificacoes, atualizacoes)
    monkeypatch.setattr(ImplantacaoService, "buscar_por_id", classmethod(lambda cls, implantacao_id: implantacao))

    ImplantacaoService.adicionar_comentario(
        7,
        MultiDict([
            ("comentario", "Atualização técnica"),
            ("enviar_email", "on"),
            ("destinatarios_email_informados", "1"),
            ("destinatarios_email", "tecnico@cliente.com"),
            ("destinatarios_email", "projetos@o3cloud.com.br"),
        ]),
    )

    assert notificacoes[0]["destinatarios"] == ["tecnico@cliente.com", "projetos@o3cloud.com.br"]
    assert ImplantacaoService.repository.preferencias == [(7, "financeiro@cliente.com")]


def test_destinatario_desmarcado_permanece_desmarcado_nos_proximos_comentarios():
    implantacao = {
        **IMPLANTACAO,
        "cliente_email": "financeiro@cliente.com",
        "contato_email": "tecnico@cliente.com",
        "emails_excluidos_interacoes": "financeiro@cliente.com",
    }

    destinatarios = ImplantacaoService._destinatarios_interacoes(implantacao)

    assert destinatarios == [
        {"email": "tecnico@cliente.com", "origens": ["Contato do contrato"], "selecionado": True},
        {"email": "financeiro@cliente.com", "origens": ["Cadastro do cliente"], "selecionado": False},
    ]


def test_comentario_rejeita_destinatario_que_nao_pertence_ao_projeto(monkeypatch):
    notificacoes = []
    atualizacoes = []
    implantacao = {**IMPLANTACAO, "cliente_email": "cliente@example.com"}
    _patch_fluxo(monkeypatch, notificacoes, atualizacoes)
    monkeypatch.setattr(ImplantacaoService, "buscar_por_id", classmethod(lambda cls, implantacao_id: implantacao))

    try:
        ImplantacaoService.adicionar_comentario(
            7,
            MultiDict([
                ("comentario", "Teste"),
                ("enviar_email", "on"),
                ("destinatarios_email_informados", "1"),
                ("destinatarios_email", "intruso@example.com"),
            ]),
        )
        assert False, "Era esperado erro de validação"
    except ValueError as erro:
        assert "Selecione ao menos um destinatário" in str(erro)

    assert notificacoes == []
