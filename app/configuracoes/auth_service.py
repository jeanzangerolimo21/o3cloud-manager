import hashlib
import secrets
import socket
from datetime import datetime, timedelta

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
        cls.repository.registrar_login_usuario(usuario.get("id"))
        cls._auditar(usuario.get("email") or usuario.get("login"), "LOGIN_SUCESSO", "auth_usuarios", usuario.get("id"), "Login realizado", ip_origem, user_agent)
        return usuario

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
        return {"origem": "LOCAL", "status": "CONVIDADO"}

    @classmethod
    def buscar_usuario(cls, usuario_id):
        return cls.repository.buscar_usuario(usuario_id)

    @classmethod
    def criar_usuario(cls, dados, usuario_email="sistema"):
        payload = cls._normalizar_usuario(dados)
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
    def atualizar_usuario(cls, usuario_id, dados, usuario_email="sistema"):
        existente = cls.repository.buscar_usuario(usuario_id)
        if not existente:
            raise ValueError("Usuário não encontrado.")
        payload = cls._normalizar_usuario(dados)
        outro = cls.repository.buscar_usuario_por_email(payload["email"]) if payload["email"] else None
        if outro and int(outro["id"]) != int(usuario_id):
            raise ValueError("Já existe outro usuário cadastrado com este e-mail.")
        payload["updated_by"] = usuario_email or "sistema"
        cls.repository.atualizar_usuario(usuario_id, payload)
        cls._sincronizar_agenda(usuario_id, payload.get("possui_agenda"), usuario_email)
        cls._auditar(usuario_email, "USUARIO_ATUALIZADO", "auth_usuarios", usuario_id, payload["email"])

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
        }

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
    def _auditar(cls, usuario_email, acao, entidade, entidade_id=None, detalhes=None, ip_origem=None, user_agent=None):
        try:
            cls.repository.registrar_auditoria(usuario_email or "sistema", acao, entidade, entidade_id, detalhes, ip_origem, user_agent)
        except Exception:
            pass
