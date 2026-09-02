from flask import Flask
from flask import session

from app.core import access_control


class RepoPermissoesFake:
    usuario = {
        "id": 10,
        "email": "operacao@example.com",
        "status": "ATIVO",
        "perfil_codigo": "OPERACOES",
    }
    permissoes = [
        {"menu_key": "clientes", "nivel_acesso": "LEITURA"},
        {"menu_key": "contatos", "nivel_acesso": "LEITURA"},
    ]

    @classmethod
    def buscar_usuario_por_email_com_perfil(cls, email):
        return cls.usuario if email == "operacao@example.com" else None

    @classmethod
    def listar_menu_keys_usuario(cls, email):
        return cls.permissoes if email == "operacao@example.com" else []


def _app():
    app = Flask(__name__)
    app.secret_key = "teste"
    return app


def test_perfil_leitura_acessa_lista_mas_nao_rotas_de_escrita(monkeypatch):
    monkeypatch.setattr(access_control, "AuthRepository", RepoPermissoesFake)

    with _app().test_request_context("/"):
        session["usuario_email"] = "operacao@example.com"
        session["usuario_perfil"] = "OPERACOES"

        assert access_control.pode_acessar_endpoint("clientes", "clientes.index", "GET") is True
        assert access_control.pode_acessar_endpoint("clientes", "clientes.novo", "GET") is False
        assert access_control.pode_acessar_endpoint("clientes", "clientes.novo", "POST") is False
        assert access_control.pode_acessar_endpoint("contatos", "contatos.index", "GET") is True
        assert access_control.pode_acessar_endpoint("contatos", "contatos.editar", "GET") is False


def test_fallback_acesso_negado_usa_primeira_tela_permitida(monkeypatch):
    monkeypatch.setattr(access_control, "AuthRepository", RepoPermissoesFake)

    with _app().test_request_context("/"):
        session["usuario_email"] = "operacao@example.com"
        session["usuario_perfil"] = "OPERACOES"
        session["usuario_dashboard_principal"] = "financeiro.dashboard"

        assert access_control.endpoint_fallback_acesso("clientes.novo") == "clientes.index"


def test_aso_tem_permissao_independente_do_administrativo(monkeypatch):
    class RepoAdministrativoSemAso(RepoPermissoesFake):
        permissoes = [
            {"menu_key": "administrativo", "nivel_acesso": "EDICAO"},
        ]

    monkeypatch.setattr(access_control, "AuthRepository", RepoAdministrativoSemAso)

    with _app().test_request_context("/"):
        session["usuario_email"] = "operacao@example.com"
        session["usuario_perfil"] = "OPERACOES"

        assert access_control.permissao_endpoint("administrativo.index") == "administrativo"
        assert access_control.permissao_endpoint("administrativo.aso") == "administrativo_aso"
        assert access_control.pode_acessar_endpoint("administrativo", "administrativo.index", "GET") is True
        assert access_control.pode_acessar_endpoint("administrativo_aso", "administrativo.aso", "GET") is False


def test_cofre_senhas_edicao_pode_excluir_anexo_sem_perfil_admin(monkeypatch):
    class RepoOperacoesCofre(RepoPermissoesFake):
        permissoes = [
            {"menu_key": "cofre_senhas", "nivel_acesso": "EDICAO"},
        ]

    monkeypatch.setattr(access_control, "AuthRepository", RepoOperacoesCofre)

    with _app().test_request_context("/"):
        session["usuario_email"] = "operacao@example.com"
        session["usuario_perfil"] = "OPERACOES"

        assert access_control.pode_acessar_endpoint(
            "cofre_senhas",
            "implantacao.excluir_anexo_senha_cofre",
            "POST",
        ) is True
        assert access_control.pode_acessar_endpoint(
            "cofre_senhas",
            "implantacao.excluir_senha_cofre",
            "POST",
        ) is False


def test_cofre_senhas_leitura_nao_pode_excluir_anexo(monkeypatch):
    class RepoOperacoesCofreLeitura(RepoPermissoesFake):
        permissoes = [
            {"menu_key": "cofre_senhas", "nivel_acesso": "LEITURA"},
        ]

    monkeypatch.setattr(access_control, "AuthRepository", RepoOperacoesCofreLeitura)

    with _app().test_request_context("/"):
        session["usuario_email"] = "operacao@example.com"
        session["usuario_perfil"] = "OPERACOES"

        assert access_control.pode_acessar_endpoint(
            "cofre_senhas",
            "implantacao.excluir_anexo_senha_cofre",
            "POST",
        ) is False


def test_configuracoes_operacionais_nao_exigem_admin_na_rota(monkeypatch):
    from app.configuracoes import routes as configuracoes_routes

    def falhar_exigir_admin():
        raise AssertionError("rota nao deve exigir perfil ADMIN alem da permissao de menu")

    monkeypatch.setattr(configuracoes_routes, "_exigir_admin", falhar_exigir_admin)
    monkeypatch.setattr(configuracoes_routes, "render_template", lambda *args, **kwargs: "ok")
    monkeypatch.setattr(configuracoes_routes.BackupSistemaService, "contexto", lambda: {})
    monkeypatch.setattr(configuracoes_routes.CacheRetencaoService, "contexto", lambda: {})
    monkeypatch.setattr(configuracoes_routes.SincronismosAgendadosService, "contexto", lambda: {})

    with _app().test_request_context("/configuracoes/backups"):
        session["usuario_email"] = "infra@example.com"
        session["usuario_perfil"] = "INFRAESTRUTURA"
        assert configuracoes_routes.backups_index() == "ok"

    with _app().test_request_context("/configuracoes/cache"):
        session["usuario_email"] = "infra@example.com"
        session["usuario_perfil"] = "INFRAESTRUTURA"
        assert configuracoes_routes.cache_index() == "ok"

    with _app().test_request_context("/configuracoes/sincronismos"):
        session["usuario_email"] = "infra@example.com"
        session["usuario_perfil"] = "INFRAESTRUTURA"
        assert configuracoes_routes.sincronismos_index() == "ok"
