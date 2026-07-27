from urllib.parse import urlparse

from app.implantacao.cofre_senhas_service import CofreSenhaService
from app.repositories.integracao_config_repository import IntegracaoConfigRepository


TIPOS_INTEGRACAO = {
    "proxmox": "Proxmox VE",
    "pbs": "Proxmox Backup Server",
    "zabbix": "Zabbix",
}


class IntegracaoConfigService:
    repository = IntegracaoConfigRepository

    @classmethod
    def listar(cls, tipo=None, ativo="1"):
        return cls.repository.listar(tipo=tipo, ativo=cls._normalizar_ativo(ativo))

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard()

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
        if integracao.get("tipo") in ("proxmox", "pbs") and not integracao.get("usuario") and not integracao.get("token_nome"):
            return "ERRO", "Informe usuário ou nome do token."
        if integracao.get("tipo") == "zabbix" and not integracao.get("token_nome"):
            return "AVISO", "Configuração estrutural válida. Recomenda-se informar nome do token Zabbix para auditoria."
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
