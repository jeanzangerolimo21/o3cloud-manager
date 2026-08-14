from datetime import datetime, timedelta

import pytest
from werkzeug.security import check_password_hash

from app.configuracoes.auth_service import AuthConfigService


class Repo2FAFake:
    usuarios = {}
    codigos = []
    dispositivos = {}
    auditoria = []
    totp_updates = []
    totp_disable = []
    expirou_codigos = []
    tentativas = []
    usados = []
    logins = []
    usos_dispositivo = []
    convite = None
    senha_definida = None
    convite_usado = []

    @classmethod
    def reset(cls):
        cls.usuarios = {}
        cls.codigos = []
        cls.dispositivos = {}
        cls.auditoria = []
        cls.totp_updates = []
        cls.totp_disable = []
        cls.expirou_codigos = []
        cls.tentativas = []
        cls.usados = []
        cls.logins = []
        cls.usos_dispositivo = []
        cls.convite = None
        cls.senha_definida = None
        cls.convite_usado = []

    @classmethod
    def buscar_usuario(cls, usuario_id):
        return cls.usuarios.get(usuario_id)

    @classmethod
    def expirar_codigos_2fa_usuario(cls, usuario_id):
        cls.expirou_codigos.append(usuario_id)
        return True

    @classmethod
    def inserir_codigo_2fa(cls, dados):
        codigo = {**dados, "id": len(cls.codigos) + 1, "status": "PENDENTE", "tentativas": 0}
        cls.codigos.append(codigo)
        return codigo["id"]

    @classmethod
    def buscar_codigo_2fa_pendente(cls, usuario_id):
        for codigo in reversed(cls.codigos):
            if codigo["usuario_id"] == usuario_id and codigo["status"] == "PENDENTE" and codigo["expira_em"] >= datetime.now():
                return codigo
        return None

    @classmethod
    def marcar_codigo_2fa_usado(cls, codigo_id):
        cls.usados.append(codigo_id)
        for codigo in cls.codigos:
            if codigo["id"] == codigo_id:
                codigo["status"] = "USADO"
        return True

    @classmethod
    def registrar_tentativa_codigo_2fa(cls, codigo_id):
        cls.tentativas.append(codigo_id)
        for codigo in cls.codigos:
            if codigo["id"] == codigo_id:
                codigo["tentativas"] += 1
        return True

    @classmethod
    def buscar_dispositivo_confiavel(cls, usuario_id, token_hash):
        return cls.dispositivos.get((usuario_id, token_hash))

    @classmethod
    def registrar_uso_dispositivo_confiavel(cls, dispositivo_id):
        cls.usos_dispositivo.append(dispositivo_id)
        return True

    @classmethod
    def inserir_dispositivo_confiavel(cls, dados):
        cls.dispositivos[(dados["usuario_id"], dados["token_hash"])] = {**dados, "id": len(cls.dispositivos) + 1}
        return len(cls.dispositivos)

    @classmethod
    def atualizar_totp_usuario(cls, usuario_id, secret_encrypted, atualizado_por=None):
        cls.totp_updates.append((usuario_id, secret_encrypted, atualizado_por))
        cls.usuarios[usuario_id]["exigir_2fa"] = 1
        cls.usuarios[usuario_id]["two_factor_metodo"] = "TOTP"
        cls.usuarios[usuario_id]["two_factor_secret"] = secret_encrypted
        cls.usuarios[usuario_id]["two_factor_configurado_em"] = datetime.now()
        return True

    @classmethod
    def desativar_totp_usuario(cls, usuario_id, atualizado_por=None):
        cls.totp_disable.append((usuario_id, atualizado_por))
        cls.usuarios[usuario_id]["two_factor_metodo"] = "EMAIL"
        cls.usuarios[usuario_id]["two_factor_secret"] = None
        cls.usuarios[usuario_id]["two_factor_configurado_em"] = None
        return True

    @classmethod
    def registrar_login_usuario(cls, usuario_id):
        cls.logins.append(usuario_id)
        return True

    @classmethod
    def buscar_convite_por_hash(cls, token_hash):
        if cls.convite and cls.convite.get("token_hash") == token_hash:
            return cls.convite
        return None

    @classmethod
    def definir_senha(cls, usuario_id, senha_hash):
        cls.senha_definida = (usuario_id, senha_hash)
        return True

    @classmethod
    def marcar_convite_usado(cls, convite_id):
        cls.convite_usado.append(convite_id)
        if cls.convite:
            cls.convite["status"] = "USADO"
        return True

    @classmethod
    def registrar_auditoria(cls, usuario_email, acao, entidade, entidade_id=None, detalhes=None, ip_origem=None, user_agent=None):
        cls.auditoria.append({
            "usuario_email": usuario_email,
            "acao": acao,
            "entidade": entidade,
            "entidade_id": entidade_id,
            "detalhes": detalhes,
            "ip_origem": ip_origem,
            "user_agent": user_agent,
        })
        return True


@pytest.fixture(autouse=True)
def repo_fake(monkeypatch):
    Repo2FAFake.reset()
    Repo2FAFake.usuarios[7] = {"id": 7, "nome": "Ana", "email": "ana@example.com", "login": "ana@example.com", "status": "ATIVO", "two_factor_metodo": "EMAIL", "two_factor_secret": None, "two_factor_configurado_em": None}
    monkeypatch.setattr(AuthConfigService, "repository", Repo2FAFake)
    yield
    monkeypatch.setattr(AuthConfigService, "repository", Repo2FAFake)


def test_iniciar_2fa_email_expira_codigo_anterior_salva_hash_e_envia_email(monkeypatch):
    envios = []
    monkeypatch.setattr("app.configuracoes.auth_service.secrets.randbelow", lambda limite: 1234)
    monkeypatch.setattr("app.configuracoes.auth_service.EmailService.enviar", lambda assunto, corpo, destinatarios, corpo_html=None: envios.append((assunto, corpo, destinatarios, corpo_html)) or {"enviado": True})

    resultado = AuthConfigService.iniciar_2fa_email(7, "10.0.0.1", "pytest")

    assert resultado["email"] == "ana@example.com"
    assert Repo2FAFake.expirou_codigos == [7]
    assert Repo2FAFake.codigos[0]["codigo_hash"] == AuthConfigService._hash_codigo_2fa(7, "001234")
    assert Repo2FAFake.codigos[0]["codigo_hash"] != "001234"
    assert "001234" in envios[0][1]
    assert "001234" in envios[0][3]
    assert "font-size:32px" in envios[0][3]
    assert Repo2FAFake.auditoria[-1]["acao"] == "LOGIN_2FA_CODIGO_ENVIADO"


def test_iniciar_2fa_email_bloqueia_usuario_sem_email(monkeypatch):
    Repo2FAFake.usuarios[7]["email"] = None
    monkeypatch.setattr("app.configuracoes.auth_service.EmailService.enviar", lambda *args, **kwargs: {"enviado": True})

    with pytest.raises(ValueError, match="sem e-mail"):
        AuthConfigService.iniciar_2fa_email(7)

    assert Repo2FAFake.codigos == []


def test_validar_2fa_email_aceita_codigo_correto_e_marca_como_usado():
    Repo2FAFake.codigos.append({
        "id": 1,
        "usuario_id": 7,
        "codigo_hash": AuthConfigService._hash_codigo_2fa(7, "654321"),
        "status": "PENDENTE",
        "expira_em": datetime.now() + timedelta(minutes=5),
        "tentativas": 0,
    })

    usuario = AuthConfigService.validar_2fa_email(7, "654321", "10.0.0.1", "pytest")

    assert usuario["id"] == 7
    assert Repo2FAFake.usados == [1]
    assert Repo2FAFake.auditoria[-1]["acao"] == "LOGIN_2FA_SUCESSO"


def test_validar_2fa_email_rejeita_codigo_invalido_e_incrementa_tentativa():
    Repo2FAFake.codigos.append({
        "id": 1,
        "usuario_id": 7,
        "codigo_hash": AuthConfigService._hash_codigo_2fa(7, "654321"),
        "status": "PENDENTE",
        "expira_em": datetime.now() + timedelta(minutes=5),
        "tentativas": 0,
    })

    with pytest.raises(ValueError, match="Código inválido"):
        AuthConfigService.validar_2fa_email(7, "000000")

    assert Repo2FAFake.tentativas == [1]
    assert Repo2FAFake.codigos[0]["tentativas"] == 1
    assert Repo2FAFake.auditoria[-1]["acao"] == "LOGIN_2FA_FALHA"


def test_validar_2fa_email_expira_desafio_apos_limite_de_tentativas():
    Repo2FAFake.codigos.append({
        "id": 1,
        "usuario_id": 7,
        "codigo_hash": AuthConfigService._hash_codigo_2fa(7, "654321"),
        "status": "PENDENTE",
        "expira_em": datetime.now() + timedelta(minutes=5),
        "tentativas": AuthConfigService.MFA_MAX_ATTEMPTS,
    })

    with pytest.raises(ValueError, match="Limite de tentativas"):
        AuthConfigService.validar_2fa_email(7, "654321")

    assert Repo2FAFake.expirou_codigos == [7]
    assert Repo2FAFake.auditoria[-1]["acao"] == "LOGIN_2FA_BLOQUEADO"


def test_dispositivo_confiavel_confere_token_por_hash_e_registra_uso():
    token_hash = AuthConfigService._hash_token("token-real")
    Repo2FAFake.dispositivos[(7, token_hash)] = {"id": 33, "usuario_id": 7, "token_hash": token_hash}

    assert AuthConfigService.dispositivo_confiavel(7, "token-real") is True
    assert Repo2FAFake.usos_dispositivo == [33]


def test_exige_2fa_dispensa_quando_dispositivo_e_confiavel(monkeypatch):
    usuario = {"id": 7, "exigir_2fa": 1, "two_factor_metodo": "EMAIL"}
    monkeypatch.setattr(AuthConfigService, "dispositivo_confiavel", classmethod(lambda cls, usuario_id, token: True))

    assert AuthConfigService.exige_2fa(usuario, "token-real") is False


def test_totp_codigo_usa_vetor_rfc_6238_sha1_6_digitos(monkeypatch):
    segredo = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    monkeypatch.setattr(AuthConfigService, "TOTP_DIGITS", 8)

    assert AuthConfigService._totp_codigo(segredo, 59 // 30) == "94287082"


def test_confirmar_configuracao_totp_valida_codigo_e_salva_segredo(monkeypatch):
    segredo = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    codigo = AuthConfigService._totp_codigo(segredo, 1)
    monkeypatch.setattr("app.configuracoes.auth_service.time.time", lambda: 30)
    monkeypatch.setattr(AuthConfigService, "_encrypt_totp_secret", classmethod(lambda cls, valor: f"enc:{valor}"))

    usuario = AuthConfigService.confirmar_configuracao_totp(7, segredo, codigo, "admin@example.com")

    assert usuario["two_factor_metodo"] == "TOTP"
    assert Repo2FAFake.totp_updates == [(7, f"enc:{segredo}", "admin@example.com")]
    assert Repo2FAFake.auditoria[-1]["acao"] == "TOTP_CONFIGURADO"


def test_validar_2fa_totp_aceita_codigo_atual(monkeypatch):
    segredo = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    Repo2FAFake.usuarios[7].update({
        "exigir_2fa": 1,
        "two_factor_metodo": "TOTP",
        "two_factor_secret": "enc",
        "two_factor_configurado_em": datetime.now(),
    })
    monkeypatch.setattr("app.configuracoes.auth_service.time.time", lambda: 30)
    monkeypatch.setattr(AuthConfigService, "_decrypt_totp_secret", classmethod(lambda cls, valor: segredo))

    usuario = AuthConfigService.validar_2fa_totp(7, AuthConfigService._totp_codigo(segredo, 1))

    assert usuario["id"] == 7
    assert Repo2FAFake.auditoria[-1]["acao"] == "LOGIN_2FA_SUCESSO"


def test_desativar_totp_exige_codigo_valido(monkeypatch):
    segredo = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    Repo2FAFake.usuarios[7].update({
        "two_factor_metodo": "TOTP",
        "two_factor_secret": "enc",
        "two_factor_configurado_em": datetime.now(),
    })
    monkeypatch.setattr("app.configuracoes.auth_service.time.time", lambda: 30)
    monkeypatch.setattr(AuthConfigService, "_decrypt_totp_secret", classmethod(lambda cls, valor: segredo))

    with pytest.raises(ValueError, match="Código TOTP inválido"):
        AuthConfigService.desativar_totp(7, "000000", "ana@example.com")

    assert Repo2FAFake.totp_disable == []

    AuthConfigService.desativar_totp(7, AuthConfigService._totp_codigo(segredo, 1), "ana@example.com")

    assert Repo2FAFake.totp_disable == [(7, "ana@example.com")]


def test_aceitar_convite_retorna_convite_aceito_sem_rebuscar_token_usado():
    token = "convite-token"
    Repo2FAFake.convite = {
        "id": 55,
        "usuario_id": 7,
        "usuario_email": "ana@example.com",
        "usuario_nome": "Ana",
        "token_hash": AuthConfigService._hash_token(token),
        "status": "PENDENTE",
        "expira_em": datetime.now() + timedelta(hours=1),
    }

    convite = AuthConfigService.aceitar_convite(token, "senha-segura", "senha-segura")

    assert convite["id"] == 55
    assert Repo2FAFake.senha_definida[0] == 7
    assert check_password_hash(Repo2FAFake.senha_definida[1], "senha-segura")
    assert Repo2FAFake.convite_usado == [55]
    assert Repo2FAFake.auditoria[-1]["acao"] == "CONVITE_ACEITO"
