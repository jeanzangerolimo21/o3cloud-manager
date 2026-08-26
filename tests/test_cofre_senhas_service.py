from io import BytesIO

from flask import Flask

from app.implantacao.cofre_senhas_service import CofreSenhaService


CLIENTE = {"id": 10, "nome_fantasia": "Cliente Teste", "razao_social": "", "cnpj": "123"}


def _dados(**extra):
    dados = {
        "cliente_id": "10",
        "categoria": "linux",
        "titulo": "Servidor app01",
        "usuario": "root",
        "senha": "senha-root",
        "ativo": "1",
    }
    dados.update(extra)
    return dados


def _patch_dependencias(monkeypatch):
    monkeypatch.setattr("app.implantacao.cofre_senhas_service.ClienteService.buscar_por_id", lambda cliente_id: CLIENTE)


def _app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    return app


def test_normalizar_permite_credencial_secundaria_ausente(monkeypatch):
    _patch_dependencias(monkeypatch)

    payload = CofreSenhaService._normalizar(_dados(), exigir_senha=True, usuario_email="ops@example.com")

    assert payload["usuario"] == "root"
    assert payload["senha"] == "senha-root"
    assert payload["usuario_2"] is None
    assert payload["senha_2"] == ""


def test_normalizar_exige_senha_quando_usuario_secundario_informado(monkeypatch):
    _patch_dependencias(monkeypatch)

    try:
        CofreSenhaService._normalizar(_dados(usuario_2="local", senha_2=""), exigir_senha=True)
    except ValueError as erro:
        assert "Senha da credencial secundaria" in str(erro)
    else:
        raise AssertionError("normalizacao deveria exigir senha secundaria")


def test_consumir_compartilhamento_secundario_retorna_somente_senha(monkeypatch):
    app = _app()
    with app.app_context():
        senha_2 = CofreSenhaService._encrypt("senha-local")

        class RepoFake:
            @classmethod
            def consumir_compartilhamento(cls, token_hash, ip_origem=None):
                return {
                    "cofre_senha_id": 5,
                    "credencial": "secundaria",
                    "titulo": "Servidor app01",
                    "senha_encrypted": CofreSenhaService._encrypt("senha-root"),
                    "senha_2_encrypted": senha_2,
                    "expires_at": None,
                }

        eventos = []
        monkeypatch.setattr(CofreSenhaService, "repository", RepoFake)
        monkeypatch.setattr("app.implantacao.cofre_senhas_service.registrar_evento", lambda *args, **kwargs: eventos.append(args))

        compartilhamento = CofreSenhaService.consumir_compartilhamento("token", "127.0.0.1")

    assert compartilhamento == {"titulo": "Servidor app01", "senha": "senha-local", "expires_at": None}
    assert "usuario" not in compartilhamento

class ArquivoFake:
    def __init__(self, nome, conteudo=b"secret"):
        self.filename = nome
        self.mimetype = "text/plain"
        self._buffer = BytesIO(conteudo)

    def seek(self, *args):
        return self._buffer.seek(*args)

    def tell(self):
        return self._buffer.tell()

    def save(self, destino):
        with open(destino, "wb") as handle:
            handle.write(self._buffer.getvalue())


def test_salvar_anexos_registra_arquivo_txt(monkeypatch, tmp_path):
    from app.core.storage import StorageService

    anexos = []

    class RepoFake:
        @classmethod
        def inserir_anexo(cls, senha_id, salvo):
            anexos.append((senha_id, salvo))

    monkeypatch.setattr(StorageService, "BASE_STORAGE", tmp_path)
    monkeypatch.setattr(CofreSenhaService, "repository", RepoFake)

    total = CofreSenhaService._salvar_anexos(7, [ArquivoFake("senhas.txt")], "ops@example.com")

    assert total == 1
    assert anexos[0][0] == 7
    assert anexos[0][1]["arquivo_original"] == "senhas.txt"
    assert anexos[0][1]["created_by"] == "ops@example.com"
    assert (tmp_path / "cofre_senhas" / "7" / anexos[0][1]["nome"]).exists()

