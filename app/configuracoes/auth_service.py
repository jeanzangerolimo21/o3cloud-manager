import hashlib
import secrets
import socket
from datetime import datetime, timedelta

from flask import url_for
from werkzeug.security import generate_password_hash

from app.core.email import EmailService
from app.implantacao.cofre_senhas_service import CofreSenhaService
from app.repositories.auth_repository import AuthRepository


class AuthConfigService:
    repository = AuthRepository
    ORIGENS = ("LOCAL", "FREEIPA", "LDAP", "AD")
    STATUS_USUARIO = ("CONVIDADO", "ATIVO", "BLOQUEADO", "INATIVO")
    TIPOS_PROVEDOR = ("FREEIPA", "LDAP", "AD")

    @classmethod
    def dashboard(cls):
        usuarios = cls.repository.listar_usuarios()
        provedores = cls.repository.listar_provedores()
        return {
            "usuarios": usuarios,
            "provedores": provedores,
            "perfis": cls.repository.listar_perfis(),
            "auditoria": cls.repository.listar_auditoria(),
            "total_usuarios": len(usuarios),
            "usuarios_ativos": len([u for u in usuarios if u.get("status") == "ATIVO"]),
            "convites_pendentes": len([u for u in usuarios if u.get("convite_status") == "PENDENTE"]),
            "provedores_ativos": len([p for p in provedores if p.get("ativo")]),
        }

    @classmethod
    def novo_usuario_payload(cls):
        return {"origem": "LOCAL", "status": "CONVIDADO"}

    @classmethod
    def buscar_usuario(cls, usuario_id):
        return cls.repository.buscar_usuario(usuario_id)

    @classmethod
    def criar_usuario(cls, dados, usuario_email="sistema"):
        payload = cls._normalizar_usuario(dados)
        if cls.repository.buscar_usuario_por_email(payload["email"]):
            raise ValueError("Já existe usuário cadastrado com este e-mail.")
        payload["created_by"] = usuario_email or "sistema"
        payload["updated_by"] = usuario_email or "sistema"
        usuario_id = cls.repository.inserir_usuario(payload)
        cls._auditar(usuario_email, "USUARIO_CRIADO", "auth_usuarios", usuario_id, payload["email"])
        if payload["origem"] == "LOCAL" and payload["status"] == "CONVIDADO":
            cls.enviar_convite(usuario_id, usuario_email)
        return usuario_id

    @classmethod
    def atualizar_usuario(cls, usuario_id, dados, usuario_email="sistema"):
        existente = cls.repository.buscar_usuario(usuario_id)
        if not existente:
            raise ValueError("Usuário não encontrado.")
        payload = cls._normalizar_usuario(dados)
        outro = cls.repository.buscar_usuario_por_email(payload["email"])
        if outro and int(outro["id"]) != int(usuario_id):
            raise ValueError("Já existe outro usuário cadastrado com este e-mail.")
        payload["updated_by"] = usuario_email or "sistema"
        cls.repository.atualizar_usuario(usuario_id, payload)
        cls._auditar(usuario_email, "USUARIO_ATUALIZADO", "auth_usuarios", usuario_id, payload["email"])

    @classmethod
    def enviar_convite(cls, usuario_id, usuario_email="sistema"):
        usuario = cls.repository.buscar_usuario(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        if usuario.get("origem") != "LOCAL":
            raise ValueError("Convite por e-mail é permitido apenas para usuários locais.")
        if usuario.get("status") == "BLOQUEADO":
            raise ValueError("Usuário bloqueado não pode receber convite.")

        token = secrets.token_urlsafe(32)
        token_hash = cls._hash_token(token)
        expira_em = datetime.now() + timedelta(days=3)
        cls.repository.expirar_convites_usuario(usuario_id)
        cls.repository.inserir_convite(
            {
                "usuario_id": usuario_id,
                "token_hash": token_hash,
                "email": usuario.get("email"),
                "expira_em": expira_em,
                "enviado_em": datetime.now(),
                "created_by": usuario_email or "sistema",
            }
        )
        link = url_for("configuracoes.usuarios_aceitar_convite", token=token, _external=True)
        assunto = "Convite de acesso - O3Cloud Manager"
        corpo = (
            f"Olá, {usuario.get('nome')}.\n\n"
            "Você foi convidado para acessar o O3Cloud Manager.\n"
            f"Acesse o link abaixo para cadastrar sua senha. O convite expira em {expira_em:%d/%m/%Y %H:%M}.\n\n"
            f"{link}\n\n"
            "Caso você não reconheça este convite, ignore esta mensagem."
        )
        try:
            resultado = EmailService.enviar(assunto, corpo, [usuario.get("email")])
        except Exception as erro:
            resultado = {
                "enviado": False,
                "motivo": cls._mensagem_segura(erro),
                "destinatarios": [usuario.get("email")],
            }
        cls._auditar(usuario_email, "CONVITE_ENVIADO", "auth_usuarios", usuario_id, usuario.get("email"))
        return {"link": link, "email": usuario.get("email"), "email_resultado": resultado}

    @classmethod
    def buscar_convite(cls, token):
        convite = cls.repository.buscar_convite_por_hash(cls._hash_token(token or ""))
        if not convite:
            return None
        convite["valido"] = (
            convite.get("status") == "PENDENTE"
            and convite.get("expira_em")
            and convite.get("expira_em") >= datetime.now()
        )
        return convite

    @classmethod
    def aceitar_convite(cls, token, senha, confirmacao):
        convite = cls.buscar_convite(token)
        if not convite or not convite.get("valido"):
            raise ValueError("Convite inválido ou expirado.")
        senha = senha or ""
        if len(senha) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if senha != (confirmacao or ""):
            raise ValueError("A confirmação de senha não confere.")
        cls.repository.definir_senha(convite["usuario_id"], generate_password_hash(senha))
        cls.repository.marcar_convite_usado(convite["id"])
        cls._auditar(
            convite.get("usuario_email"),
            "CONVITE_ACEITO",
            "auth_usuarios",
            convite["usuario_id"],
            convite.get("usuario_email"),
        )

    @classmethod
    def novo_provedor_payload(cls):
        return {
            "tipo": "LDAP",
            "porta": 389,
            "ativo": 1,
            "atributo_login": "uid",
            "atributo_email": "mail",
            "atributo_nome": "cn",
        }

    @classmethod
    def buscar_provedor(cls, provedor_id):
        return cls.repository.buscar_provedor(provedor_id)

    @classmethod
    def criar_provedor(cls, dados, usuario_email="sistema"):
        payload = cls._normalizar_provedor(dados)
        payload["created_by"] = usuario_email or "sistema"
        payload["updated_by"] = usuario_email or "sistema"
        provedor_id = cls.repository.inserir_provedor(payload)
        cls._auditar(usuario_email, "PROVEDOR_CRIADO", "auth_provedores", provedor_id, payload["tipo"])
        return provedor_id

    @classmethod
    def atualizar_provedor(cls, provedor_id, dados, usuario_email="sistema"):
        if not cls.repository.buscar_provedor(provedor_id):
            raise ValueError("Provedor não encontrado.")
        payload = cls._normalizar_provedor(dados)
        payload["updated_by"] = usuario_email or "sistema"
        cls.repository.atualizar_provedor(provedor_id, payload)
        cls._auditar(usuario_email, "PROVEDOR_ATUALIZADO", "auth_provedores", provedor_id, payload["tipo"])

    @classmethod
    def testar_provedor(cls, provedor_id, dados_teste=None):
        provedor = cls.repository.buscar_provedor(provedor_id)
        if not provedor:
            raise ValueError("Provedor não encontrado.")
        try:
            mensagem = cls._testar_socket(provedor)
            usuario_teste = cls._texto((dados_teste or {}).get("usuario_teste"))
            senha_teste = (dados_teste or {}).get("senha_teste") or ""
            if usuario_teste and senha_teste:
                mensagem = cls._testar_autenticacao_ldap(provedor, usuario_teste, senha_teste)
        except Exception as erro:
            texto = cls._mensagem_segura(erro)
            cls.repository.registrar_teste_provedor(provedor_id, "ERRO", texto)
            raise ValueError(f"Falha no teste do provedor: {texto}") from erro
        cls.repository.registrar_teste_provedor(provedor_id, "OK", mensagem)
        return {"status": "OK", "mensagem": mensagem}

    @classmethod
    def _normalizar_usuario(cls, dados):
        nome = cls._texto(dados.get("nome"))
        email = (cls._texto(dados.get("email")) or "").lower()
        login = cls._texto(dados.get("login")) or email
        origem = (cls._texto(dados.get("origem")) or "LOCAL").upper()
        status = (cls._texto(dados.get("status")) or "CONVIDADO").upper()
        if origem not in cls.ORIGENS:
            raise ValueError("Origem de autenticação inválida.")
        if status not in cls.STATUS_USUARIO:
            raise ValueError("Status de usuário inválido.")
        if not nome:
            raise ValueError("Nome do usuário é obrigatório.")
        if "@" not in email:
            raise ValueError("E-mail do usuário é obrigatório e deve ser válido.")
        if origem != "LOCAL" and status == "CONVIDADO":
            status = "ATIVO"
        return {
            "nome": nome,
            "email": email,
            "login": login,
            "origem": origem,
            "perfil_id": cls._inteiro(dados.get("perfil_id")),
            "status": status,
            "externo_id": cls._texto(dados.get("externo_id")),
            "senha_hash": None,
        }

    @classmethod
    def _normalizar_provedor(cls, dados):
        tipo = (cls._texto(dados.get("tipo")) or "LDAP").upper()
        if tipo not in cls.TIPOS_PROVEDOR:
            raise ValueError("Tipo de provedor inválido.")
        nome = cls._texto(dados.get("nome")) or tipo
        host = cls._texto(dados.get("host"))
        porta = cls._inteiro(dados.get("porta")) or (636 if cls._flag(dados, "usar_tls") else 389)
        if not host:
            raise ValueError("Host do provedor é obrigatório.")
        if porta < 1 or porta > 65535:
            raise ValueError("Porta do provedor inválida.")
        senha = dados.get("bind_password") or ""
        return {
            "nome": nome,
            "tipo": tipo,
            "host": host,
            "porta": porta,
            "dominio": cls._texto(dados.get("dominio")),
            "base_dn": cls._texto(dados.get("base_dn")),
            "bind_dn": cls._texto(dados.get("bind_dn")),
            "bind_password_encrypted": CofreSenhaService._encrypt(senha) if senha else None,
            "usar_tls": cls._flag(dados, "usar_tls"),
            "usar_starttls": cls._flag(dados, "usar_starttls"),
            "filtro_usuarios": cls._texto(dados.get("filtro_usuarios")),
            "filtro_grupos": cls._texto(dados.get("filtro_grupos")),
            "atributo_login": cls._texto(dados.get("atributo_login")) or ("sAMAccountName" if tipo == "AD" else "uid"),
            "atributo_email": cls._texto(dados.get("atributo_email")) or "mail",
            "atributo_nome": cls._texto(dados.get("atributo_nome")) or "cn",
            "upn_suffix": cls._texto(dados.get("upn_suffix")),
            "ativo": cls._flag(dados, "ativo"),
        }

    @staticmethod
    def _testar_socket(provedor):
        with socket.create_connection((provedor.get("host"), int(provedor.get("porta") or 389)), timeout=8):
            return f"Comunicação OK com {provedor.get('host')}:{provedor.get('porta')}"

    @classmethod
    def _testar_autenticacao_ldap(cls, provedor, usuario, senha):
        try:
            from ldap3 import ALL, Connection, Server, Tls
        except ImportError:
            return "Comunicação OK. Biblioteca ldap3 não instalada; validação de credencial ficará pendente."
        use_ssl = bool(provedor.get("usar_tls"))
        server = Server(
            provedor.get("host"),
            port=int(provedor.get("porta") or 389),
            use_ssl=use_ssl,
            get_info=ALL,
            tls=Tls() if use_ssl else None,
        )
        user = cls._usuario_bind(provedor, usuario)
        conn = Connection(server, user=user, password=senha, auto_bind=False)
        if provedor.get("usar_starttls"):
            conn.open()
            conn.start_tls()
        if not conn.bind():
            raise ValueError("Autenticação recusada pelo provedor.")
        conn.unbind()
        return f"Comunicação e autenticação OK para {usuario}."

    @staticmethod
    def _usuario_bind(provedor, usuario):
        if provedor.get("tipo") == "AD" and "@" not in usuario and provedor.get("upn_suffix"):
            return f"{usuario}@{provedor.get('upn_suffix')}"
        return usuario

    @staticmethod
    def _hash_token(token):
        return hashlib.sha256((token or "").encode("utf-8")).hexdigest()

    @staticmethod
    def _mensagem_segura(erro):
        return str(erro)[:500].replace("password", "senha").replace("token", "segredo")

    @staticmethod
    def _flag(dados, chave):
        if hasattr(dados, "getlist"):
            valores = dados.getlist(chave)
            return any(str(valor).lower() in ("1", "true", "on", "sim") for valor in valores)
        return str(dados.get(chave) or "").lower() in ("1", "true", "on", "sim")

    @staticmethod
    def _texto(valor):
        return (valor or "").strip() or None

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor) if valor not in (None, "") else None
        except (TypeError, ValueError):
            return None

    @classmethod
    def _auditar(cls, usuario_email, acao, entidade, entidade_id=None, detalhes=None):
        try:
            cls.repository.registrar_auditoria(usuario_email or "sistema", acao, entidade, entidade_id, detalhes)
        except Exception:
            pass
