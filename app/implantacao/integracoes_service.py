import os
from urllib.parse import urlparse

from app.implantacao.cofre_senhas_service import CofreSenhaService
from app.repositories.integracao_config_repository import IntegracaoConfigRepository


TIPOS_INTEGRACAO = {
    "omie": "OMIE",
    "clicksign": "ClickSign",
    "proxmox": "Proxmox VE",
    "pbs": "Proxmox Backup Server",
    "zabbix": "Zabbix",
    "freeipa": "FreeIPA",
    "truenas": "TrueNAS",
}

GRUPOS_INTEGRACAO = {
    "negocio": {
        "titulo": "Integrações de Negócio",
        "descricao": "Configuração base para OMIE e ClickSign.",
        "tipos": ("omie", "clicksign"),
    },
    "tecnicas": {
        "titulo": "Integrações Técnicas",
        "descricao": "Configuração base para Proxmox, PBS, Zabbix, FreeIPA e TrueNAS.",
        "tipos": ("proxmox", "pbs", "zabbix", "freeipa", "truenas"),
    },
}


class IntegracaoConfigService:
    repository = IntegracaoConfigRepository

    @classmethod
    def listar(cls, tipo=None, ativo="1", grupo=None):
        return cls.repository.listar(
            tipo=tipo,
            ativo=cls._normalizar_ativo(ativo),
            tipos=cls.tipos_por_grupo(grupo),
        )

    @classmethod
    def dashboard(cls, grupo=None):
        return cls.repository.dashboard(tipos=cls.tipos_por_grupo(grupo))

    @classmethod
    def tipos_por_grupo(cls, grupo):
        if grupo in GRUPOS_INTEGRACAO:
            return GRUPOS_INTEGRACAO[grupo]["tipos"]
        return None

    @classmethod
    def tipo_options(cls, grupo=None):
        tipos = cls.tipos_por_grupo(grupo)
        if not tipos:
            return TIPOS_INTEGRACAO
        return {tipo: TIPOS_INTEGRACAO[tipo] for tipo in tipos}

    @classmethod
    def grupo_por_tipo(cls, tipo):
        for grupo, config in GRUPOS_INTEGRACAO.items():
            if tipo in config["tipos"]:
                return grupo
        return "tecnicas"

    @classmethod
    def contexto_grupo(cls, grupo):
        grupo = grupo if grupo in GRUPOS_INTEGRACAO else "tecnicas"
        contexto = GRUPOS_INTEGRACAO[grupo]
        return {
            "grupo": grupo,
            "titulo": contexto["titulo"],
            "descricao": contexto["descricao"],
            "tipos": contexto["tipos"],
        }

    @classmethod
    def integracoes_ambiente(cls, grupo=None):
        if grupo != "negocio":
            return []

        clicksign_url = cls._url_sem_token(os.getenv("CLICKSIGN_API_URL") or "https://sandbox.clicksign.com/api/v3")
        return [
            {
                "tipo": "omie",
                "nome": "OMIE",
                "origem_config": ".env",
                "base_url": "https://app.omie.com.br/api/v1",
                "ambiente": "producao",
                "status": "Configurada" if os.getenv("OMIE_APP_KEY") and os.getenv("OMIE_APP_SECRET") else "Pendente",
                "classe": "success" if os.getenv("OMIE_APP_KEY") and os.getenv("OMIE_APP_SECRET") else "warning",
                "segredos": [
                    {"chave": "OMIE_APP_KEY", "label": "App Key", "mascara": cls._mascara(os.getenv("OMIE_APP_KEY"))},
                    {"chave": "OMIE_APP_SECRET", "label": "App Secret", "mascara": cls._mascara(os.getenv("OMIE_APP_SECRET"))},
                ],
            },
            {
                "tipo": "clicksign",
                "nome": "ClickSign",
                "origem_config": ".env",
                "base_url": clicksign_url,
                "ambiente": os.getenv("CLICKSIGN_ENVIRONMENT") or "sandbox",
                "status": "Configurada" if os.getenv("CLICKSIGN_ACCESS_TOKEN") else "Pendente",
                "classe": "success" if os.getenv("CLICKSIGN_ACCESS_TOKEN") else "warning",
                "segredos": [
                    {"chave": "CLICKSIGN_ACCESS_TOKEN", "label": "Access Token", "mascara": cls._mascara(os.getenv("CLICKSIGN_ACCESS_TOKEN"))},
                ],
            },
        ]

    @classmethod
    def revelar_segredo_ambiente(cls, chave):
        permitidas = {
            "OMIE_APP_KEY",
            "OMIE_APP_SECRET",
            "CLICKSIGN_ACCESS_TOKEN",
        }
        if chave not in permitidas:
            raise ValueError("Segredo de ambiente nao permitido.")
        valor = os.getenv(chave) or ""
        if not valor:
            raise ValueError("Segredo nao configurado.")
        return valor

    @classmethod
    def revelar_segredo_config(cls, integracao_id):
        integracao = cls.repository.buscar_por_id(integracao_id)
        if not integracao or not integracao.get("ativo"):
            raise ValueError("Integração não encontrada ou inativa.")
        try:
            return CofreSenhaService._decrypt(integracao.get("segredo_encrypted"))
        except ValueError as erro:
            raise ValueError("Não foi possível descriptografar o segredo. Verifique a chave do cofre.") from erro

    @staticmethod
    def _mascara(valor):
        if not valor:
            return "Nao configurado"
        return "****"

    @staticmethod
    def _url_sem_token(valor):
        texto = (valor or "").strip()
        if "?" in texto:
            return texto.split("?", 1)[0]
        return texto

    @classmethod
    def buscar_por_id(cls, integracao_id):
        return cls.repository.buscar_por_id(integracao_id)

    @classmethod
    def criar(cls, dados, usuario_email="sistema"):
        payload = cls._normalizar(dados, exigir_segredo=True)
        existente = cls.repository.buscar_por_tipo_nome(payload.get("tipo"), payload.get("nome"))
        if existente:
            raise ValueError("Já existe uma integração deste tipo com este nome.")
        payload["segredo_encrypted"] = CofreSenhaService._encrypt(payload.pop("segredo"))
        payload["created_by"] = usuario_email or "sistema"
        payload["updated_by"] = usuario_email or "sistema"
        return cls.repository.inserir(payload)

    @classmethod
    def atualizar(cls, integracao_id, dados, usuario_email="sistema"):
        existente = cls.repository.buscar_por_id(integracao_id)
        if not existente:
            raise ValueError("Integração não encontrada.")
        payload = cls._normalizar(dados, exigir_segredo=False, existente=existente)
        segredo = payload.pop("segredo", None)
        payload["segredo_encrypted"] = CofreSenhaService._encrypt(segredo) if segredo else None
        payload["updated_by"] = usuario_email or "sistema"
        duplicada = cls.repository.buscar_por_tipo_nome(payload.get("tipo"), payload.get("nome"))
        if duplicada and int(duplicada.get("id")) != int(integracao_id):
            raise ValueError("Já existe outra integração deste tipo com este nome.")
        cls.repository.atualizar(integracao_id, payload)

    @classmethod
    def inativar(cls, integracao_id, usuario_email="sistema"):
        if not cls.repository.buscar_por_id(integracao_id):
            raise ValueError("Integração não encontrada.")
        cls.repository.inativar(integracao_id, usuario_email)

    @classmethod
    def testar_configuracao(cls, integracao_id):
        integracao = cls.repository.buscar_por_id(integracao_id)
        if not integracao:
            raise ValueError("Integração não encontrada.")
        status, mensagem = cls._validar_configuracao(integracao)
        cls.repository.registrar_teste(integracao_id, status, mensagem)
        return {"status": status, "mensagem": mensagem}

    @classmethod
    def _normalizar(cls, dados, exigir_segredo=False, existente=None):
        tipo = cls._texto(dados.get("tipo") or (existente or {}).get("tipo"))
        if tipo not in TIPOS_INTEGRACAO:
            raise ValueError("Tipo de integração inválido.")
        nome = cls._texto(dados.get("nome"))
        base_url = cls._normalizar_url(dados.get("base_url"))
        usuario = cls._texto(dados.get("usuario"))
        token_nome = cls._texto(dados.get("token_nome"))
        segredo = (dados.get("segredo") or "").strip()
        if not nome:
            raise ValueError("Nome é obrigatório.")
        if not base_url:
            raise ValueError("URL base é obrigatória.")
        if exigir_segredo and not segredo:
            raise ValueError("Token ou senha é obrigatório.")
        timeout = cls._inteiro(dados.get("timeout_seconds")) or 30
        if timeout < 5 or timeout > 120:
            raise ValueError("Timeout deve ficar entre 5 e 120 segundos.")
        ativo_valores = dados.getlist("ativo") if hasattr(dados, "getlist") else [dados.get("ativo", "1")]
        verify_valores = dados.getlist("verify_ssl") if hasattr(dados, "getlist") else [dados.get("verify_ssl", "1")]
        return {
            "tipo": tipo,
            "nome": nome,
            "base_url": base_url,
            "usuario": usuario,
            "token_nome": token_nome,
            "segredo": segredo,
            "verify_ssl": str((verify_valores or ["0"])[-1]).lower() in ("1", "true", "on", "sim"),
            "timeout_seconds": timeout,
            "ativo": str((ativo_valores or ["0"])[-1]).lower() in ("1", "true", "on", "sim"),
            "observacoes": cls._texto_longo(dados.get("observacoes")),
        }

    @classmethod
    def _validar_configuracao(cls, integracao):
        if integracao.get("tipo") not in TIPOS_INTEGRACAO:
            return "ERRO", "Tipo de integração inválido."
        parsed = urlparse(integracao.get("base_url") or "")
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return "ERRO", "URL base inválida."
        if not integracao.get("segredo_encrypted"):
            return "ERRO", "Token ou senha não cadastrado."
        if integracao.get("tipo") in ("proxmox", "pbs", "freeipa", "truenas") and not integracao.get("usuario") and not integracao.get("token_nome"):
            return "ERRO", "Informe usuário ou nome do token."
        if integracao.get("tipo") in ("zabbix", "omie", "clicksign") and not integracao.get("token_nome"):
            return "AVISO", "Configuração estrutural válida. Recomenda-se informar nome do token para auditoria."
        return "OK", "Configuração estrutural válida. Conexão externa será habilitada em etapa futura."

    @staticmethod
    def _normalizar_url(valor):
        texto = (valor or "").strip().rstrip("/")
        if not texto:
            return None
        parsed = urlparse(texto)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Informe uma URL base válida com http:// ou https://.")
        return texto

    @staticmethod
    def _texto(valor):
        return (valor or "").strip() or None

    @staticmethod
    def _texto_longo(valor):
        return (valor or "").strip() or None

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalizar_ativo(valor):
        if valor == "todos":
            return None
        if str(valor) == "0":
            return 0
        return 1
