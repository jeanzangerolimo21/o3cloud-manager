import base64
import hashlib
import hmac
import secrets
import socket
import struct
import time
from datetime import datetime, timedelta
from html import escape
from urllib.parse import quote

from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app.core.access_control import MENU_PERMISSOES
from app.core.email import EmailService
from app.core.storage import StorageService
from app.implantacao.cofre_senhas_service import CofreSenhaService
from app.repositories.auth_repository import AuthRepository

class AuthConfigService:
    repository = AuthRepository
    ORIGENS = ("LOCAL", "FREEIPA", "LDAP", "AD")
    STATUS_USUARIO = ("CONVIDADO", "ATIVO", "BLOQUEADO", "INATIVO")
    TIPOS_PROVEDOR = ("FREEIPA", "LDAP", "AD")
    MENU_PERMISSOES = MENU_PERMISSOES
    MFA_COOKIE_NAME = "o3cloud_dispositivo_confiavel"
    MFA_CODE_MINUTES = 10
    MFA_TRUSTED_DEVICE_DAYS = 30
    MFA_MAX_ATTEMPTS = 5
    TOTP_ISSUER = "O3Cloud Manager"
    TOTP_INTERVAL_SECONDS = 30
    TOTP_DIGITS = 6
    TOTP_WINDOW = 1
    DASHBOARDS_PRINCIPAIS = (
        {"valor": "financeiro.dashboard", "label": "Visao Geral", "menu_key": "visao_geral"},
        {"valor": "financeiro.dashboard_executivo", "label": "Dashboard Executivo", "menu_key": "dashboard_executivo"},
        {"valor": "propostas.dashboard", "label": "Dashboard Comercial", "menu_key": "dashboard_comercial"},
        {"valor": "administrativo.index", "label": "Administrativo", "menu_key": "administrativo"},
        {"valor": "administrativo.agenda", "label": "Minha Agenda", "menu_key": "administrativo"},
        {"valor": "implantacao.index", "label": "Implantacao", "menu_key": "implantacao"},
        {"valor": "configuracoes.usuarios_index", "label": "Usuarios e Acessos", "menu_key": "usuarios_acessos"},
        {"valor": "infraestrutura.monitoramento_zabbix", "label": "Monitoramento Zabbix", "menu_key": "monitoramento_zabbix"},
    )

    @classmethod
    def dashboard(cls):
        usuarios = cls.repository.listar_usuarios()
        provedores = cls.repository.listar_provedores()
        return {
            "usuarios": usuarios,
            "provedores": provedores,
            "perfis": cls.repository.listar_perfis(),
            "total_usuarios": len(usuarios),
            "usuarios_ativos": len([u for u in usuarios if u.get("status") == "ATIVO"]),
            "convites_pendentes": len([u for u in usuarios if u.get("convite_status") == "PENDENTE"]),
            "provedores_ativos": len([p for p in provedores if p.get("ativo")]),
            "grupo_perfil_mapas": cls.repository.listar_grupo_perfil_mapas(),
            "integracoes_identidade": cls.repository.listar_integracoes_identidade(),
        }

    @classmethod
    def autenticar(cls, identificador, senha, ip_origem=None, user_agent=None):
        identificador = (cls._texto(identificador) or "").lower()
        usuario = cls.repository.buscar_usuario_por_login(identificador) if identificador else None
        if not usuario:
            cls._auditar(identificador or "desconhecido", "LOGIN_FALHA", "auth_usuarios", detalhes="Usuário não encontrado", ip_origem=ip_origem, user_agent=user_agent)
            raise ValueError("Usuário ou senha inválidos.")
        if usuario.get("origem") != "LOCAL":
            cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_FALHA", "auth_usuarios", usuario.get("id"), "Origem externa sem autenticação local", ip_origem, user_agent)
            raise ValueError("Usuário externo deve autenticar pelo provedor configurado.")
        if usuario.get("status") != "ATIVO":
            cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_FALHA", "auth_usuarios", usuario.get("id"), f"Status {usuario.get('status')}", ip_origem, user_agent)
            raise ValueError("Usuário não está ativo.")
        senha_hash = usuario.get("senha_hash") or ""
        if not senha_hash or not check_password_hash(senha_hash, senha or ""):
            cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_FALHA", "auth_usuarios", usuario.get("id"), "Senha inválida", ip_origem, user_agent)
            raise ValueError("Usuário ou senha inválidos.")
        cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_SENHA_VALIDADA", "auth_usuarios", usuario.get("id"), "Senha validada", ip_origem, user_agent)
        return usuario

    @classmethod
    def concluir_login(cls, usuario, ip_origem=None, user_agent=None, detalhes="Login realizado"):
        cls.repository.registrar_login_usuario(usuario.get("id"))
        cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_SUCESSO", "auth_usuarios", usuario.get("id"), detalhes, ip_origem, user_agent)

    @classmethod
    def exige_2fa(cls, usuario, token_dispositivo=None):
        if not usuario or not usuario.get("exigir_2fa"):
            return False
        return not cls.dispositivo_confiavel(usuario.get("id"), token_dispositivo)

    @classmethod
    def metodo_2fa(cls, usuario):
        metodo = (usuario.get("two_factor_metodo") or "EMAIL").upper()
        return metodo if metodo in ("EMAIL", "TOTP") else "EMAIL"

    @classmethod
    def dispositivo_confiavel(cls, usuario_id, token_dispositivo=None):
        if not usuario_id or not token_dispositivo:
            return False
        dispositivo = cls.repository.buscar_dispositivo_confiavel(usuario_id, cls._hash_token(token_dispositivo))
        if not dispositivo:
            return False
        cls.repository.registrar_uso_dispositivo_confiavel(dispositivo.get("id"))
        return True

    @classmethod
    def iniciar_2fa_email(cls, usuario_id, ip_origem=None, user_agent=None):
        usuario = cls.repository.buscar_usuario(usuario_id)
        if not usuario or usuario.get("status") != "ATIVO":
            raise ValueError("Sessão de autenticação inválida. Faça login novamente.")
        if not usuario.get("email"):
            raise ValueError("Usuário sem e-mail cadastrado para receber o código de segurança.")
        codigo = f"{secrets.randbelow(1000000):06d}"
        expira_em = datetime.now() + timedelta(minutes=cls.MFA_CODE_MINUTES)
        cls.repository.expirar_codigos_2fa_usuario(usuario_id)
        cls.repository.inserir_codigo_2fa({
            "usuario_id": usuario_id,
            "codigo_hash": cls._hash_codigo_2fa(usuario_id, codigo),
            "expira_em": expira_em,
            "ip_origem": ip_origem,
            "user_agent": user_agent,
        })
        assunto = "Código de segurança - O3Cloud Manager"
        corpo = (
            f"Olá, {usuario.get('nome')}.\n\n"
            "Seu código de segurança é:\n\n"
            f"    {codigo}\n\n"
            f"Ele expira em {cls.MFA_CODE_MINUTES} minutos.\n\n"
            "Caso você não tenha tentado acessar o sistema, ignore esta mensagem e avise o administrador."
        )
        corpo_html = cls._corpo_html_2fa(usuario, codigo)
        try:
            resultado = EmailService.enviar(assunto, corpo, [usuario.get("email")], corpo_html=corpo_html)
        except Exception as erro:
            resultado = {"enviado": False, "motivo": cls._mensagem_segura(erro), "destinatarios": [usuario.get("email")]}
        cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_2FA_CODIGO_ENVIADO", "auth_usuarios", usuario_id, resultado.get("motivo") or "Código enviado", ip_origem, user_agent)
        if not resultado.get("enviado"):
            raise ValueError(f"Não foi possível enviar o código de segurança ({resultado.get('motivo') or 'SMTP indisponível'}).")
        return {"email": usuario.get("email"), "expira_em": expira_em}

    @classmethod
    def validar_2fa_email(cls, usuario_id, codigo, ip_origem=None, user_agent=None):
        usuario = cls.repository.buscar_usuario(usuario_id)
        if not usuario or usuario.get("status") != "ATIVO":
            raise ValueError("Sessão de autenticação inválida. Faça login novamente.")
        desafio = cls.repository.buscar_codigo_2fa_pendente(usuario_id)
        if not desafio:
            cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_2FA_FALHA", "auth_usuarios", usuario_id, "Código expirado ou inexistente", ip_origem, user_agent)
            raise ValueError("Código expirado. Faça login novamente para receber um novo código.")
        if int(desafio.get("tentativas") or 0) >= cls.MFA_MAX_ATTEMPTS:
            cls.repository.expirar_codigos_2fa_usuario(usuario_id)
            cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_2FA_BLOQUEADO", "auth_usuarios", usuario_id, "Limite de tentativas excedido", ip_origem, user_agent)
            raise ValueError("Limite de tentativas excedido. Faça login novamente.")
        codigo_hash = cls._hash_codigo_2fa(usuario_id, codigo)
        if not hmac.compare_digest(codigo_hash, desafio.get("codigo_hash") or ""):
            cls.repository.registrar_tentativa_codigo_2fa(desafio.get("id"))
            cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_2FA_FALHA", "auth_usuarios", usuario_id, "Código inválido", ip_origem, user_agent)
            raise ValueError("Código inválido.")
        cls.repository.marcar_codigo_2fa_usado(desafio.get("id"))
        cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_2FA_SUCESSO", "auth_usuarios", usuario_id, "Código validado", ip_origem, user_agent)
        return usuario

    @classmethod
    def iniciar_configuracao_totp(cls, usuario_id):
        usuario = cls.repository.buscar_usuario(usuario_id)
        if not usuario or usuario.get("status") != "ATIVO":
            raise ValueError("Usuário não encontrado ou inativo.")
        if not usuario.get("email") and not usuario.get("login"):
            raise ValueError("Usuário sem identificador para configurar TOTP.")
        segredo = cls._gerar_totp_secret()
        return {
            "secret": segredo,
            "secret_formatado": cls._formatar_totp_secret(segredo),
            "otpauth_uri": cls._totp_uri(usuario, segredo),
        }

    @classmethod
    def confirmar_configuracao_totp(cls, usuario_id, segredo, codigo, usuario_email="sistema", ip_origem=None, user_agent=None):
        usuario = cls.repository.buscar_usuario(usuario_id)
        if not usuario or usuario.get("status") != "ATIVO":
            raise ValueError("Usuário não encontrado ou inativo.")
        segredo = cls._normalizar_totp_secret(segredo)
        if not cls._validar_totp(segredo, codigo):
            cls._auditar(usuario_email, "TOTP_CONFIGURACAO_FALHA", "auth_usuarios", usuario_id, "Código TOTP inválido", ip_origem, user_agent)
            raise ValueError("Código TOTP inválido.")
        cls.repository.atualizar_totp_usuario(usuario_id, cls._encrypt_totp_secret(segredo), usuario_email)
        cls._auditar(usuario_email, "TOTP_CONFIGURADO", "auth_usuarios", usuario_id, "TOTP habilitado", ip_origem, user_agent)
        return cls.repository.buscar_usuario(usuario_id)

    @classmethod
    def desativar_totp(cls, usuario_id, codigo, usuario_email="sistema", ip_origem=None, user_agent=None):
        usuario = cls.repository.buscar_usuario(usuario_id)
        if not usuario or usuario.get("status") != "ATIVO":
            raise ValueError("Usuário não encontrado ou inativo.")
        if cls.metodo_2fa(usuario) == "TOTP" and usuario.get("two_factor_secret"):
            if not cls.validar_codigo_totp_usuario(usuario, codigo):
                cls._auditar(usuario_email, "TOTP_DESATIVACAO_FALHA", "auth_usuarios", usuario_id, "Código TOTP inválido", ip_origem, user_agent)
                raise ValueError("Código TOTP inválido.")
        cls.repository.desativar_totp_usuario(usuario_id, usuario_email)
        cls._auditar(usuario_email, "TOTP_DESATIVADO", "auth_usuarios", usuario_id, "TOTP desabilitado", ip_origem, user_agent)
        return cls.repository.buscar_usuario(usuario_id)

    @classmethod
    def validar_2fa_totp(cls, usuario_id, codigo, ip_origem=None, user_agent=None):
        usuario = cls.repository.buscar_usuario(usuario_id)
        if not usuario or usuario.get("status") != "ATIVO":
            raise ValueError("Sessão de autenticação inválida. Faça login novamente.")
        if cls.metodo_2fa(usuario) != "TOTP" or not usuario.get("two_factor_secret") or not usuario.get("two_factor_configurado_em"):
            cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_2FA_FALHA", "auth_usuarios", usuario_id, "TOTP não configurado", ip_origem, user_agent)
            raise ValueError("TOTP não está configurado para este usuário.")
        if not cls.validar_codigo_totp_usuario(usuario, codigo):
            cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_2FA_FALHA", "auth_usuarios", usuario_id, "Código TOTP inválido", ip_origem, user_agent)
            raise ValueError("Código inválido.")
        cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_2FA_SUCESSO", "auth_usuarios", usuario_id, "Código TOTP validado", ip_origem, user_agent)
        return usuario

    @classmethod
    def validar_codigo_totp_usuario(cls, usuario, codigo):
        try:
            segredo = cls._decrypt_totp_secret(usuario.get("two_factor_secret"))
        except ValueError:
            return False
        return cls._validar_totp(segredo, codigo)

    @classmethod
    def criar_dispositivo_confiavel(cls, usuario_id, ip_origem=None, user_agent=None):
        token = secrets.token_urlsafe(32)
        expira_em = datetime.now() + timedelta(days=cls.MFA_TRUSTED_DEVICE_DAYS)
        descricao = (user_agent or "").split(" ", 1)[0][:180] or "Navegador"
        cls.repository.inserir_dispositivo_confiavel({
            "usuario_id": usuario_id,
            "token_hash": cls._hash_token(token),
            "descricao": descricao,
            "ip_origem": ip_origem,
            "user_agent": user_agent,
            "expira_em": expira_em,
        })
        return {"token": token, "expira_em": expira_em}

    @classmethod
    def atualizar_minha_conta(cls, usuario_id, dados, arquivo_foto=None):
        usuario = cls.repository.buscar_usuario(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        nome = cls._texto(dados.get("nome"))
        email = (cls._texto(dados.get("email")) or "").lower()
        if not nome:
            raise ValueError("Nome é obrigatório.")
        if usuario.get("origem") == "LOCAL" and (not email or "@" not in email):
            raise ValueError("E-mail válido é obrigatório para usuário local.")
        if email and "@" not in email:
            raise ValueError("E-mail inválido.")
        outro = cls.repository.buscar_usuario_por_email(email) if email else None
        if outro and int(outro.get("id")) != int(usuario_id):
            raise ValueError("Já existe outro usuário cadastrado com este e-mail.")
        foto = cls._salvar_foto_usuario(arquivo_foto) if arquivo_foto and arquivo_foto.filename else None
        login = email or usuario.get("login")
        cls.repository.atualizar_minha_conta(usuario_id, {
            "nome": nome,
            "email": email or None,
            "login": login,
            "foto": foto,
            "updated_by": usuario.get("email") or usuario.get("login"),
        })
        if foto and usuario.get("foto"):
            StorageService.excluir(StorageService.USUARIOS, usuario.get("foto"))
        cls._auditar(email or usuario.get("email") or usuario.get("login"), "MINHA_CONTA_ATUALIZADA", "auth_usuarios", usuario_id, "Dados pessoais atualizados")
        return cls.repository.buscar_usuario(usuario_id)

    @classmethod
    def alterar_minha_senha(cls, usuario_id, senha_atual, nova_senha, confirmacao):
        usuario = cls.repository.buscar_usuario(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        if usuario.get("origem") != "LOCAL":
            raise ValueError("Alteração de senha pelo sistema é permitida apenas para usuário Local.")
        if not check_password_hash(usuario.get("senha_hash") or "", senha_atual or ""):
            raise ValueError("Senha atual inválida.")
        nova_senha = nova_senha or ""
        if len(nova_senha) < 8:
            raise ValueError("A nova senha deve ter pelo menos 8 caracteres.")
        if nova_senha != (confirmacao or ""):
            raise ValueError("A confirmação de senha não confere.")
        cls.repository.atualizar_senha_usuario(usuario_id, generate_password_hash(nova_senha), usuario.get("email") or usuario.get("login"))
        cls._auditar(usuario.get("email") or usuario.get("login"), "SENHA_ALTERADA", "auth_usuarios", usuario_id, "Senha alterada pelo usuário")


    @classmethod
    def solicitar_reset_senha(cls, identificador, ip_origem=None, user_agent=None):
        identificador = (cls._texto(identificador) or "").lower()
        mensagem = "Se o cadastro existir e puder redefinir senha, enviaremos um link para o e-mail cadastrado."
        usuario = cls.repository.buscar_usuario_por_email_ou_login(identificador) if identificador else None
        if not usuario:
            cls._auditar(identificador or "desconhecido", "RESET_SENHA_SOLICITADO", "auth_usuarios", detalhes="Usuário não encontrado", ip_origem=ip_origem, user_agent=user_agent)
            return {"mensagem": mensagem, "email_enviado": False}
        if usuario.get("origem") != "LOCAL" or usuario.get("status") != "ATIVO" or not usuario.get("email"):
            cls._auditar(usuario.get("email") or usuario.get("login"), "RESET_SENHA_IGNORADO", "auth_usuarios", usuario.get("id"), "Usuário sem reset local disponível", ip_origem, user_agent)
            return {"mensagem": mensagem, "email_enviado": False}

        token = secrets.token_urlsafe(40)
        expira_em = datetime.now() + timedelta(minutes=60)
        cls.repository.expirar_resets_senha_usuario(usuario.get("id"))
        cls.repository.inserir_reset_senha({
            "usuario_id": usuario.get("id"),
            "token_hash": cls._hash_token(token),
            "expira_em": expira_em,
            "ip_origem": ip_origem,
            "user_agent": user_agent,
        })
        link = url_for("autenticacao.resetar_senha", token=token, _external=True)
        assunto = "Redefinição de senha - O3Cloud Manager"
        corpo = "\n".join([
            f"Olá, {usuario.get('nome')}.",
            "",
            "Recebemos uma solicitação para redefinir sua senha.",
            f"Acesse o link abaixo para cadastrar uma nova senha. O link expira em {expira_em:%d/%m/%Y %H:%M}.",
            "",
            link,
            "",
            "Caso você não tenha solicitado esta alteração, ignore esta mensagem.",
        ])
        corpo_html = cls._corpo_html_reset_senha(usuario, link, expira_em)
        try:
            resultado = EmailService.enviar(assunto, corpo, [usuario.get("email")], corpo_html=corpo_html)
        except Exception as erro:
            resultado = {"enviado": False, "motivo": cls._mensagem_segura(erro), "destinatarios": [usuario.get("email")]}
        cls._auditar(usuario.get("email") or usuario.get("login"), "RESET_SENHA_SOLICITADO", "auth_usuarios", usuario.get("id"), resultado.get("motivo") or "Link enviado", ip_origem, user_agent)
        return {"mensagem": mensagem, "email_enviado": bool(resultado.get("enviado")), "email_resultado": resultado}

    @classmethod
    def buscar_reset_senha(cls, token):
        reset = cls.repository.buscar_reset_senha_por_hash(cls._hash_token(token or ""))
        if not reset:
            return None
        reset["valido"] = (
            reset.get("status") == "PENDENTE"
            and reset.get("expira_em")
            and reset.get("expira_em") >= datetime.now()
            and reset.get("usuario_status") == "ATIVO"
            and reset.get("usuario_origem") == "LOCAL"
        )
        return reset

    @classmethod
    def redefinir_senha(cls, token, nova_senha, confirmacao, ip_origem=None, user_agent=None):
        reset = cls.buscar_reset_senha(token)
        if not reset or not reset.get("valido"):
            raise ValueError("Link de redefinição inválido ou expirado.")
        nova_senha = nova_senha or ""
        if len(nova_senha) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if nova_senha != (confirmacao or ""):
            raise ValueError("A confirmação de senha não confere.")
        usuario_email = reset.get("usuario_email") or reset.get("usuario_login")
        cls.repository.atualizar_senha_usuario(reset.get("usuario_id"), generate_password_hash(nova_senha), usuario_email)
        cls.repository.marcar_reset_senha_usado(reset.get("id"))
        cls.repository.expirar_codigos_2fa_usuario(reset.get("usuario_id"))
        cls._auditar(usuario_email, "RESET_SENHA_CONCLUIDO", "auth_usuarios", reset.get("usuario_id"), "Senha redefinida por link", ip_origem, user_agent)
        return reset

    @classmethod
    def _corpo_html_reset_senha(cls, usuario, link, expira_em):
        nome = escape(usuario.get("nome") or "")
        link_html = escape(link)
        expira = escape(f"{expira_em:%d/%m/%Y %H:%M}")
        return f"""
        <div style=\"font-family:Arial,sans-serif;color:#1f2937;line-height:1.5\">
            <h2 style=\"margin:0 0 12px\">Redefinição de senha</h2>
            <p>Olá, {nome}.</p>
            <p>Recebemos uma solicitação para redefinir sua senha.</p>
            <p><a href=\"{link_html}\" style=\"display:inline-block;background:#0d6efd;color:#fff;padding:10px 16px;border-radius:6px;text-decoration:none\">Cadastrar nova senha</a></p>
            <p style=\"color:#6b7280\">Este link expira em {expira}. Se você não solicitou esta alteração, ignore esta mensagem.</p>
        </div>
        """

    @classmethod
    def _salvar_foto_usuario(cls, arquivo):
        validacao = StorageService.validar(arquivo)
        if not validacao:
            return None
        if validacao.get("extensao") not in StorageService.IMAGE_EXTENSIONS:
            raise ValueError("A foto deve ser uma imagem PNG, JPG, JPEG ou SVG.")
        if validacao.get("tamanho", 0) > 2 * 1024 * 1024:
            raise ValueError("A foto deve ter no máximo 2 MB.")
        return StorageService.salvar(arquivo, StorageService.USUARIOS).get("nome")

    @classmethod
    def registrar_logout(cls, usuario_email, usuario_id=None, ip_origem=None, user_agent=None):
        cls._auditar(usuario_email or "sistema", "LOGOUT", "auth_usuarios", usuario_id, "Logout realizado", ip_origem, user_agent)

    @classmethod
    def filtros_auditoria(cls, args):
        return {
            "usuario_email": cls._texto(args.get("usuario_email")),
            "acao": cls._texto(args.get("acao")),
            "entidade": cls._texto(args.get("entidade")),
            "data_inicio": cls._texto(args.get("data_inicio")),
            "data_fim": cls._texto(args.get("data_fim")),
            "limite": cls._inteiro(args.get("limite")) or 100,
        }

    @classmethod
    def contexto_auditoria(cls, args):
        filtros = cls.filtros_auditoria(args)
        return {
            "filtros": filtros,
            "auditoria": cls.repository.listar_auditoria(filtros, filtros.get("limite")),
            "acoes": [item.get("acao") for item in cls.repository.listar_acoes_auditoria()],
            "entidades": [item.get("entidade") for item in cls.repository.listar_entidades_auditoria()],
        }

    @classmethod
    def bootstrap_admin(cls, nome, email, senha, login=None, permitir_atualizar=False):
        nome = cls._texto(nome) or "Administrador"
        email = (cls._texto(email) or "").lower()
        login = cls._texto(login) or email
        senha = senha or ""
        if not email or "@" not in email:
            raise ValueError("Informe um e-mail válido para o administrador inicial.")
        if len(senha) < 12:
            raise ValueError("A senha do administrador inicial deve ter pelo menos 12 caracteres.")
        perfil = cls.repository.buscar_perfil_por_codigo("ADMIN")
        if not perfil:
            raise ValueError("Perfil ADMIN não encontrado. Aplique as migrations de autenticação antes do bootstrap.")
        admins_ativos = cls.repository.contar_admins_ativos()
        existente = cls.repository.buscar_usuario_por_email_ou_login(email) or cls.repository.buscar_usuario_por_email_ou_login(login)
        if admins_ativos and not permitir_atualizar:
            raise ValueError("Já existe administrador ativo. Use --force para promover/atualizar o usuário informado.")
        senha_hash = generate_password_hash(senha)
        if existente:
            cls.repository.promover_admin_local(existente["id"], perfil["id"], senha_hash, "bootstrap")
            usuario_id = existente["id"]
            acao = "ADMIN_BOOTSTRAP_ATUALIZADO"
        else:
            usuario_id = cls.repository.inserir_usuario({
                "nome": nome,
                "email": email,
                "login": login,
                "origem": "LOCAL",
                "perfil_id": perfil["id"],
                "status": "ATIVO",
                "externo_id": None,
                "senha_hash": senha_hash,
                "created_by": "bootstrap",
                "updated_by": "bootstrap",
            })
            acao = "ADMIN_BOOTSTRAP_CRIADO"
        cls._auditar("bootstrap", acao, "auth_usuarios", usuario_id, email)
        return {"usuario_id": usuario_id, "email": email, "acao": acao, "admins_ativos_antes": admins_ativos}

    @classmethod
    def novo_perfil_payload(cls):
        return {"ativo": 1, "mostrar_valores": 0, "dashboard_principal": "financeiro.dashboard", "permissoes": [], "permissoes_niveis": {}}

    @classmethod
    def buscar_perfil(cls, perfil_id):
        perfil = cls.repository.buscar_perfil(perfil_id)
        if not perfil:
            return None
        perfil["permissoes_niveis"] = cls._permissoes_niveis_perfil(perfil)
        perfil["permissoes"] = sorted(perfil["permissoes_niveis"].keys())
        return perfil

    @classmethod
    def criar_perfil(cls, dados, usuario_email="sistema"):
        payload = cls._normalizar_perfil(dados)
        if cls.repository.buscar_perfil_por_codigo(payload["codigo"]):
            raise ValueError("Já existe perfil com este código.")
        perfil_id = cls.repository.inserir_perfil(payload)
        cls.repository.substituir_permissoes_perfil(perfil_id, cls._permissoes_form(dados))
        cls._auditar(usuario_email, "PERFIL_CRIADO", "auth_perfis", perfil_id, payload["codigo"])
        return perfil_id

    @classmethod
    def atualizar_perfil(cls, perfil_id, dados, usuario_email="sistema"):
        perfil = cls.repository.buscar_perfil(perfil_id)
        if not perfil:
            raise ValueError("Perfil não encontrado.")
        if perfil.get("codigo") == "ADMIN":
            raise ValueError("O perfil Administrador não pode ser editado.")
        payload = cls._normalizar_perfil(dados)
        outro = cls.repository.buscar_perfil_por_codigo(payload["codigo"])
        if outro and int(outro["id"]) != int(perfil_id):
            raise ValueError("Já existe outro perfil com este código.")
        cls.repository.atualizar_perfil(perfil_id, payload)
        cls.repository.substituir_permissoes_perfil(perfil_id, cls._permissoes_form(dados))
        cls._auditar(usuario_email, "PERFIL_ATUALIZADO", "auth_perfis", perfil_id, payload["codigo"])

    @classmethod
    def menus_por_grupo(cls):
        grupos = []
        indice = {}
        for item in cls.MENU_PERMISSOES:
            grupo = item["grupo"]
            if grupo not in indice:
                indice[grupo] = {"nome": grupo, "menus": []}
                grupos.append(indice[grupo])
            indice[grupo]["menus"].append(item)
        return grupos

    @classmethod
    def novo_usuario_payload(cls):
        return {
            "origem": "LOCAL",
            "status": "CONVIDADO",
            "alertas_operacao_periodicidade": "DIARIA",
            "alertas_operacao_horario": "08:00",
        }

    @classmethod
    def buscar_usuario(cls, usuario_id):
        return cls.repository.buscar_usuario(usuario_id)

    @classmethod
    def criar_usuario(cls, dados, usuario_email="sistema", administrador=False):
        payload = cls._normalizar_usuario(dados)
        if payload.get("two_factor_metodo") == "TOTP":
            raise ValueError("TOTP deve ser configurado pelo usuário após o primeiro acesso. Cadastre inicialmente com 2FA por e-mail.")
        if not administrador:
            payload["exigir_2fa"] = False
            payload["two_factor_metodo"] = "EMAIL"
        if payload["email"] and cls.repository.buscar_usuario_por_email(payload["email"]):
            raise ValueError("Já existe usuário cadastrado com este e-mail.")
        payload["created_by"] = usuario_email or "sistema"
        payload["updated_by"] = usuario_email or "sistema"
        usuario_id = cls.repository.inserir_usuario(payload)
        cls._sincronizar_agenda(usuario_id, payload.get("possui_agenda"), usuario_email)
        cls._auditar(usuario_email, "USUARIO_CRIADO", "auth_usuarios", usuario_id, payload["email"])
        if payload["origem"] == "LOCAL" and payload["status"] == "CONVIDADO":
            cls.enviar_convite(usuario_id, usuario_email)
        return usuario_id

    @classmethod
    def atualizar_usuario(cls, usuario_id, dados, usuario_email="sistema", administrador=False):
        existente = cls.repository.buscar_usuario(usuario_id)
        if not existente:
            raise ValueError("Usuário não encontrado.")
        payload = cls._normalizar_usuario(dados)
        if not administrador:
            payload["exigir_2fa"] = bool(existente.get("exigir_2fa"))
            payload["two_factor_metodo"] = existente.get("two_factor_metodo") or "EMAIL"
        if payload.get("two_factor_metodo") == "TOTP" and not existente.get("two_factor_secret"):
            raise ValueError("TOTP ainda não foi configurado por este usuário em Minha Conta.")
        outro = cls.repository.buscar_usuario_por_email(payload["email"]) if payload["email"] else None
        if outro and int(outro["id"]) != int(usuario_id):
            raise ValueError("Já existe outro usuário cadastrado com este e-mail.")
        payload["updated_by"] = usuario_email or "sistema"
        cls.repository.atualizar_usuario(usuario_id, payload)
        cls._sincronizar_agenda(usuario_id, payload.get("possui_agenda"), usuario_email)
        cls._auditar(usuario_email, "USUARIO_ATUALIZADO", "auth_usuarios", usuario_id, payload["email"])

    @classmethod
    def remover_usuario(cls, usuario_id, usuario_logado_id=None, perfil_logado=None, usuario_email="sistema"):
        if (perfil_logado or "").upper() != "ADMIN":
            raise ValueError("Apenas Administradores podem remover usuários de acesso.")
        existente = cls.repository.buscar_usuario(usuario_id)
        if not existente:
            raise ValueError("Usuário não encontrado.")
        if usuario_logado_id and int(usuario_id) == int(usuario_logado_id):
            raise ValueError("Você não pode remover o próprio usuário logado.")
        if existente.get("perfil_codigo") == "ADMIN" and existente.get("status") == "ATIVO" and cls.repository.contar_admins_ativos() <= 1:
            raise ValueError("Não é possível remover o último Administrador ativo do sistema.")

        detalhes = {
            "nome": existente.get("nome"),
            "email": existente.get("email"),
            "login": existente.get("login"),
            "perfil": existente.get("perfil_codigo"),
            "status": existente.get("status"),
        }
        cls.repository.excluir_usuario(usuario_id)
        if existente.get("foto"):
            StorageService.excluir(StorageService.USUARIOS, existente.get("foto"))
        cls._auditar(usuario_email, "USUARIO_REMOVIDO", "auth_usuarios", usuario_id, detalhes)

    @classmethod
    def enviar_convite(cls, usuario_id, usuario_email="sistema"):
        usuario = cls.repository.buscar_usuario(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        if usuario.get("origem") != "LOCAL":
            raise ValueError("Convite por e-mail é permitido apenas para usuários locais.")
        if not usuario.get("email"):
            raise ValueError("Usuário local precisa ter e-mail cadastrado para receber convite.")
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
        return convite

    @classmethod
    def novo_grupo_perfil_mapa_payload(cls):
        return {"provedor_tipo": "LDAP", "ativo": 1}

    @classmethod
    def buscar_grupo_perfil_mapa(cls, mapa_id):
        return cls.repository.buscar_grupo_perfil_mapa(mapa_id)

    @classmethod
    def criar_grupo_perfil_mapa(cls, dados, usuario_email="sistema"):
        payload = cls._normalizar_grupo_perfil_mapa(dados)
        payload["created_by"] = usuario_email or "sistema"
        payload["updated_by"] = usuario_email or "sistema"
        existente = cls.repository.buscar_grupo_perfil_mapa_existente(
            payload["provedor_tipo"], payload["grupo_externo"], payload.get("integracao_id")
        )
        if existente:
            raise ValueError("Já existe mapeamento ativo para este grupo externo.")
        mapa_id = cls.repository.inserir_grupo_perfil_mapa(payload)
        cls._auditar(usuario_email, "GRUPO_PERFIL_MAPA_CRIADO", "auth_grupo_perfil_mapas", mapa_id, payload["grupo_externo"])
        return mapa_id

    @classmethod
    def atualizar_grupo_perfil_mapa(cls, mapa_id, dados, usuario_email="sistema"):
        if not cls.repository.buscar_grupo_perfil_mapa(mapa_id):
            raise ValueError("Mapeamento de grupo externo não encontrado.")
        payload = cls._normalizar_grupo_perfil_mapa(dados)
        payload["updated_by"] = usuario_email or "sistema"
        existente = cls.repository.buscar_grupo_perfil_mapa_existente(
            payload["provedor_tipo"], payload["grupo_externo"], payload.get("integracao_id"), ignorar_id=mapa_id
        )
        if existente:
            raise ValueError("Já existe mapeamento ativo para este grupo externo.")
        cls.repository.atualizar_grupo_perfil_mapa(mapa_id, payload)
        cls._auditar(usuario_email, "GRUPO_PERFIL_MAPA_ATUALIZADO", "auth_grupo_perfil_mapas", mapa_id, payload["grupo_externo"])

    @classmethod
    def inativar_grupo_perfil_mapa(cls, mapa_id, usuario_email="sistema"):
        if not cls.repository.buscar_grupo_perfil_mapa(mapa_id):
            raise ValueError("Mapeamento de grupo externo não encontrado.")
        cls.repository.inativar_grupo_perfil_mapa(mapa_id, usuario_email)
        cls._auditar(usuario_email, "GRUPO_PERFIL_MAPA_INATIVADO", "auth_grupo_perfil_mapas", mapa_id)

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
    def _normalizar_perfil(cls, dados):
        nome = cls._texto(dados.get("nome"))
        codigo = (cls._texto(dados.get("codigo")) or "").upper().replace(" ", "_")
        if not nome:
            raise ValueError("Nome do perfil é obrigatório.")
        if not codigo:
            raise ValueError("Código do perfil é obrigatório.")
        if codigo == "ADMIN":
            raise ValueError("O perfil Administrador é reservado e não pode ser criado ou alterado.")
        dashboard_principal = cls._texto(dados.get("dashboard_principal")) or "financeiro.dashboard"
        if dashboard_principal not in {item["valor"] for item in cls.DASHBOARDS_PRINCIPAIS}:
            raise ValueError("Dashboard principal inválido.")
        return {
            "nome": nome,
            "codigo": codigo,
            "descricao": cls._texto(dados.get("descricao")),
            "ativo": cls._flag(dados, "ativo"),
            "mostrar_valores": cls._flag(dados, "mostrar_valores"),
            "dashboard_principal": dashboard_principal,
        }

    @classmethod
    def _permissoes_form(cls, dados):
        permitidos = {item["key"] for item in cls.MENU_PERMISSOES}
        niveis_validos = {"LEITURA", "EDICAO"}
        if hasattr(dados, "getlist"):
            valores = dados.getlist("menu_keys")
        else:
            valor = dados.get("menu_keys") or []
            valores = valor if isinstance(valor, (list, tuple, set)) else [valor]

        permissoes = {}
        for valor in valores:
            if valor not in permitidos:
                continue
            nivel = (cls._texto(dados.get(f"nivel_{valor}")) or "LEITURA").upper()
            permissoes[valor] = nivel if nivel in niveis_validos else "LEITURA"
        return dict(sorted(permissoes.items()))

    @classmethod
    def _permissoes_niveis_perfil(cls, perfil):
        if perfil.get("codigo") == "ADMIN":
            return {item["key"]: "EDICAO" for item in cls.MENU_PERMISSOES}
        return {
            item["menu_key"]: (item.get("nivel_acesso") or "LEITURA")
            for item in cls.repository.listar_permissoes_perfil(perfil.get("id"))
            if item.get("permitido")
        }
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
        if origem == "LOCAL" and "@" not in email:
            raise ValueError("E-mail é obrigatório para usuários locais e deve ser válido.")
        if email and "@" not in email:
            raise ValueError("E-mail do usuário deve ser válido.")
        if origem != "LOCAL" and not login:
            raise ValueError("Login é obrigatório quando o usuário externo não tiver e-mail cadastrado.")
        if origem != "LOCAL" and status == "CONVIDADO":
            status = "ATIVO"
        metodo_2fa = (cls._texto(dados.get("two_factor_metodo")) or "EMAIL").upper()
        if metodo_2fa not in ("EMAIL", "TOTP"):
            metodo_2fa = "EMAIL"
        return {
            "nome": nome,
            "email": email or None,
            "login": login,
            "origem": origem,
            "perfil_id": cls._inteiro(dados.get("perfil_id")),
            "status": status,
            "externo_id": cls._texto(dados.get("externo_id")),
            "senha_hash": None,
            "possui_agenda": cls._flag(dados, "possui_agenda"),
            "exigir_2fa": cls._flag(dados, "exigir_2fa"),
            "two_factor_metodo": metodo_2fa,
            "receber_alertas_operacao": cls._flag(dados, "receber_alertas_operacao"),
            "alertas_operacao_periodicidade": cls._periodicidade_alertas_operacao(dados.get("alertas_operacao_periodicidade")),
            "alertas_operacao_horario": cls._horario_alertas_operacao(dados.get("alertas_operacao_horario")),
        }

    @classmethod
    def _periodicidade_alertas_operacao(cls, valor):
        periodicidade = (cls._texto(valor) or "DIARIA").upper()
        return periodicidade if periodicidade in ("DIARIA", "SEMANAL") else "DIARIA"

    @classmethod
    def _horario_alertas_operacao(cls, valor):
        texto = cls._texto(valor) or "08:00"
        partes = texto.split(":")
        try:
            hora = max(0, min(int(partes[0]), 23))
            minuto = max(0, min(int(partes[1]) if len(partes) > 1 else 0, 59))
        except (TypeError, ValueError, IndexError):
            hora, minuto = 8, 0
        return f"{hora:02d}:{minuto:02d}"

    @classmethod
    def _sincronizar_agenda(cls, usuario_id, possui_agenda, usuario_email):
        try:
            from app.repositories.administrativo_repository import AdministrativoRepository
            AdministrativoRepository.garantir_agenda(usuario_id, possui_agenda, usuario_email)
        except Exception:
            return False
        return True

    @classmethod
    def _normalizar_grupo_perfil_mapa(cls, dados):
        provedor_tipo = (cls._texto(dados.get("provedor_tipo")) or "LDAP").upper()
        if provedor_tipo not in cls.TIPOS_PROVEDOR:
            raise ValueError("Tipo de provedor inválido para o mapeamento.")
        grupo_externo = cls._texto(dados.get("grupo_externo"))
        if not grupo_externo:
            raise ValueError("Grupo externo é obrigatório.")
        if len(grupo_externo) > 180:
            raise ValueError("Grupo externo deve possuir no máximo 180 caracteres.")
        perfil_id = cls._inteiro(dados.get("perfil_id"))
        if not perfil_id or not cls.repository.buscar_perfil(perfil_id):
            raise ValueError("Perfil interno é obrigatório.")
        integracao_id = cls._inteiro(dados.get("integracao_id"))
        integracoes = cls.repository.listar_integracoes_identidade()
        integracao = next((item for item in integracoes if int(item.get("id")) == int(integracao_id)), None) if integracao_id else None
        if integracao:
            provedor_tipo = {"freeipa": "FREEIPA", "ldap": "LDAP", "ad": "AD"}.get(integracao.get("tipo"), provedor_tipo)
        return {
            "integracao_id": integracao_id,
            "provedor_tipo": provedor_tipo,
            "grupo_externo": grupo_externo,
            "perfil_id": perfil_id,
            "ativo": cls._flag(dados, "ativo"),
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



    @classmethod
    def _corpo_html_2fa(cls, usuario, codigo):
        nome = escape(usuario.get("nome") or "")
        return f"""
        <div style="font-family:Arial,Helvetica,sans-serif;color:#1f2937;line-height:1.5;max-width:560px;margin:0 auto;padding:24px;">
            <h2 style="margin:0 0 12px;font-size:20px;color:#111827;">Código de segurança</h2>
            <p style="margin:0 0 16px;">Olá, {nome}.</p>
            <p style="margin:0 0 12px;">Use o código abaixo para concluir seu acesso ao O3Cloud Manager:</p>
            <div style="background:#f3f4f6;border:1px solid #d1d5db;border-radius:8px;padding:18px 20px;text-align:center;margin:18px 0;">
                <div style="font-size:32px;letter-spacing:8px;font-weight:700;color:#0f172a;font-family:Arial,Helvetica,sans-serif;">{codigo}</div>
            </div>
            <p style="margin:0 0 16px;color:#4b5563;">Este código expira em <strong>{cls.MFA_CODE_MINUTES} minutos</strong>.</p>
            <p style="margin:0;color:#6b7280;font-size:13px;">Caso você não tenha tentado acessar o sistema, ignore esta mensagem e avise o administrador.</p>
        </div>
        """

    @classmethod
    def _gerar_totp_secret(cls):
        return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")

    @classmethod
    def _normalizar_totp_secret(cls, segredo):
        segredo = "".join(str(segredo or "").upper().split())
        if not segredo:
            raise ValueError("Segredo TOTP inválido.")
        try:
            cls._totp_key(segredo)
        except Exception as erro:
            raise ValueError("Segredo TOTP inválido.") from erro
        return segredo

    @staticmethod
    def _formatar_totp_secret(segredo):
        segredo = "".join(str(segredo or "").split())
        return " ".join(segredo[i:i + 4] for i in range(0, len(segredo), 4))

    @classmethod
    def _totp_uri(cls, usuario, segredo):
        identificador = usuario.get("email") or usuario.get("login") or str(usuario.get("id"))
        label = f"{cls.TOTP_ISSUER}:{identificador}"
        return (
            "otpauth://totp/"
            f"{quote(label)}?secret={segredo}&issuer={quote(cls.TOTP_ISSUER)}"
            f"&algorithm=SHA1&digits={cls.TOTP_DIGITS}&period={cls.TOTP_INTERVAL_SECONDS}"
        )

    @classmethod
    def _encrypt_totp_secret(cls, segredo):
        return CofreSenhaService._encrypt(segredo)

    @classmethod
    def _decrypt_totp_secret(cls, valor):
        return CofreSenhaService._decrypt(valor)

    @classmethod
    def _validar_totp(cls, segredo, codigo, momento=None):
        codigo = str(codigo or "").strip().replace(" ", "")
        if not codigo.isdigit() or len(codigo) != cls.TOTP_DIGITS:
            return False
        contador = int((momento if momento is not None else time.time()) // cls.TOTP_INTERVAL_SECONDS)
        for deslocamento in range(-cls.TOTP_WINDOW, cls.TOTP_WINDOW + 1):
            esperado = cls._totp_codigo(segredo, contador + deslocamento)
            if hmac.compare_digest(esperado, codigo):
                return True
        return False

    @classmethod
    def _totp_codigo(cls, segredo, contador):
        chave = cls._totp_key(segredo)
        mensagem = struct.pack(">Q", int(contador))
        digest = hmac.new(chave, mensagem, hashlib.sha1).digest()
        offset = digest[-1] & 0x0F
        inteiro = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
        return str(inteiro % (10 ** cls.TOTP_DIGITS)).zfill(cls.TOTP_DIGITS)

    @staticmethod
    def _totp_key(segredo):
        padding = "=" * ((8 - len(segredo) % 8) % 8)
        return base64.b32decode((segredo + padding).encode("ascii"), casefold=True)

    @staticmethod
    def _hash_token(token):
        return hashlib.sha256((token or "").encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_codigo_2fa(usuario_id, codigo):
        return hashlib.sha256(f"{usuario_id}:{str(codigo or '').strip()}".encode("utf-8")).hexdigest()

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
    def _auditar(cls, usuario_email, acao, entidade, entidade_id=None, detalhes=None, ip_origem=None, user_agent=None):
        try:
            cls.repository.registrar_auditoria(usuario_email or "sistema", acao, entidade, entidade_id, detalhes, ip_origem, user_agent)
        except Exception:
            pass
