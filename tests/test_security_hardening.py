from pathlib import Path

import pytest
from flask import Flask
from flask import render_template_string

from app.autenticacao.routes import _destino_interno
from app.configuracoes.auth_service import AuthConfigService
from app.core.security import init_security
from app.core.security import POST_FORM_RE


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("destino", ["https://evil.test", "//evil.test", "/\\evil", "javascript:alert(1)"])
def test_redirecionamento_externo_e_rejeitado(destino):
    assert _destino_interno(destino) == ""


def test_redirecionamento_interno_e_permitido():
    assert _destino_interno("/propostas/?status=ENVIADA") == "/propostas/?status=ENVIADA"


def test_injetor_csrf_identifica_formularios_post():
    html = '<form class="x" method="POST"><button>Salvar</button></form>'
    assert POST_FORM_RE.search(html)


def test_csrf_e_injetado_e_validado_em_producao():
    app = Flask(__name__)
    app.config.update(SECRET_KEY="teste-seguranca", TESTING=False)
    init_security(app)

    @app.route("/form", methods=["GET", "POST"])
    def form():
        return render_template_string('<form method="POST"><button>Salvar</button></form>')

    client = app.test_client()
    pagina = client.get("/form")
    assert b'name="csrf_token"' in pagina.data
    assert client.post("/form").status_code == 400


def test_limite_de_login_bloqueia_combinacao_usuario_ip(monkeypatch):
    class RepositoryFake:
        @staticmethod
        def contar_eventos_seguranca(_acao, _minutos, **filtros):
            return 5 if filtros.get("combinar") else 0

    monkeypatch.setattr(AuthConfigService, "repository", RepositoryFake)
    monkeypatch.setattr(AuthConfigService, "_auditar", classmethod(lambda cls, *args, **kwargs: None))

    with pytest.raises(ValueError, match="Muitas tentativas"):
        AuthConfigService._validar_limite_login("user@example.com", "192.0.2.10")


def test_diagnostico_nao_imprime_valores_dos_segredos():
    script = (ROOT / "deployment/security-diagnostic.sh").read_text()

    assert "valor oculto" in script
    assert "security.txt" in script
    assert "pip-audit" in script
