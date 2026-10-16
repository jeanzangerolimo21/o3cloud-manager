from unittest.mock import Mock

from app.configuracoes.auth_service import AuthConfigService


class ConviteRepositoryFake:
    auditoria = []

    @classmethod
    def buscar_usuario(cls, usuario_id):
        return {
            "id": usuario_id,
            "nome": "Pessoa Convidada",
            "email": "pessoa@example.com",
            "origem": "LOCAL",
            "status": "CONVIDADO",
        }

    @classmethod
    def expirar_convites_usuario(cls, usuario_id):
        return True

    @classmethod
    def inserir_convite(cls, dados):
        return 10

    @classmethod
    def registrar_auditoria(cls, usuario_email, acao, entidade, entidade_id=None, detalhes=None, ip_origem=None, user_agent=None):
        cls.auditoria.append((usuario_email, acao, entidade, entidade_id, detalhes))
        return True


def _preparar(monkeypatch):
    logger = Mock()
    monkeypatch.setattr(AuthConfigService, "repository", ConviteRepositoryFake)
    monkeypatch.setattr("app.configuracoes.auth_service.email_logger", logger)
    monkeypatch.setattr("app.configuracoes.auth_service.url_for", lambda *args, **kwargs: "https://manager.example/convite/token")
    return logger


def test_envio_de_convite_registra_tentativa_e_aceite_smtp(monkeypatch):
    logger = _preparar(monkeypatch)
    monkeypatch.setattr(
        "app.configuracoes.auth_service.EmailService.enviar",
        lambda *args, **kwargs: {"enviado": True, "origem_config": "banco"},
    )

    resultado = AuthConfigService.enviar_convite(7, "admin@example.com")

    assert resultado["email_resultado"]["enviado"] is True
    assert logger.info.call_count == 2
    assert logger.info.call_args_list[0].kwargs["extra"]["operation"] == "CONVITE_EMAIL_TENTATIVA"
    aceite = logger.info.call_args_list[1].kwargs["extra"]
    assert aceite["operation"] == "CONVITE_EMAIL_ACEITO_SMTP"
    assert aceite["recipient"] == "pessoa@example.com"
    assert aceite["smtp_origin"] == "banco"


def test_falha_smtp_do_convite_registra_erro_e_destinatario(monkeypatch):
    logger = _preparar(monkeypatch)

    def falhar(*args, **kwargs):
        raise TimeoutError("SMTP timeout")

    monkeypatch.setattr("app.configuracoes.auth_service.EmailService.enviar", falhar)

    resultado = AuthConfigService.enviar_convite(7, "admin@example.com")

    assert resultado["email_resultado"]["enviado"] is False
    falha = logger.exception.call_args.kwargs["extra"]
    assert falha["operation"] == "CONVITE_EMAIL_FALHA"
    assert falha["recipient"] == "pessoa@example.com"
    assert falha["exception_type"] == "TimeoutError"
    assert falha["failure_reason"] == "SMTP timeout"


def test_resultado_negativo_sem_excecao_tambem_e_registrado(monkeypatch):
    logger = _preparar(monkeypatch)
    monkeypatch.setattr(
        "app.configuracoes.auth_service.EmailService.enviar",
        lambda *args, **kwargs: {"enviado": False, "motivo": "smtp_nao_configurado"},
    )

    AuthConfigService.enviar_convite(7, "admin@example.com")

    falha = logger.warning.call_args.kwargs["extra"]
    assert falha["operation"] == "CONVITE_EMAIL_FALHA"
    assert falha["failure_reason"] == "smtp_nao_configurado"
