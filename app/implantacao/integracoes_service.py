import os
from urllib.parse import urlparse

import requests

from app.core.logging_config import get_logger

from app.implantacao.cofre_senhas_service import CofreSenhaService
from app.repositories.integracao_config_repository import IntegracaoConfigRepository


integration_logger = get_logger("integrations")


TIPOS_INTEGRACAO = {
    "omie": "OMIE",
    "clicksign": "ClickSign",
    "proxmox": "Proxmox VE",
    "pbs": "Proxmox Backup Server",
    "zabbix": "Zabbix",
    "freeipa": "FreeIPA",
    "ldap": "LDAP",
    "ad": "Active Directory",
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
        "descricao": "Configuração base para Proxmox, PBS, Zabbix, FreeIPA, LDAP, Active Directory e TrueNAS.",
        "tipos": ("proxmox", "pbs", "zabbix", "freeipa", "ldap", "ad", "truenas"),
    },
}


class IntegracaoConfigService:
    repository = IntegracaoConfigRepository

    @classmethod
    def listar(cls, tipo=None, ativo="1", grupo=None):
        integracoes = cls.repository.listar(
            tipo=tipo,
            ativo=cls._normalizar_ativo(ativo),
            tipos=cls.tipos_por_grupo(grupo),
        )
        return [cls._com_diagnostico(item) for item in integracoes]

    @classmethod
    def validacoes_recentes(cls, grupo=None, limite=10):
        return cls.repository.listar_validacoes_recentes(
            tipos=cls.tipos_por_grupo(grupo),
            limite=limite,
        )

    @classmethod
    def dashboard(cls, grupo=None):
        dashboard = cls.repository.dashboard(tipos=cls.tipos_por_grupo(grupo)) or {}
        diagnosticos = cls.repository.dashboard_diagnosticos(tipos=cls.tipos_por_grupo(grupo)) or {}
        dashboard.update(diagnosticos)
        return dashboard

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
        payload = cls._normalizar(dados, exigir_segredo=False)
        existente = cls.repository.buscar_por_tipo_nome(payload.get("tipo"), payload.get("nome"))
        if existente:
            raise ValueError("Já existe uma integração deste tipo com este nome.")
        segredo = payload.pop("segredo", None)
        payload["segredo_encrypted"] = CofreSenhaService._encrypt(segredo) if segredo else None
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
    def testar_configuracao(cls, integracao_id, usuario_email="sistema"):
        integracao = cls.repository.buscar_por_id(integracao_id)
        if not integracao:
            raise ValueError("Integração não encontrada.")
        status, mensagem = cls._validar_configuracao(integracao)
        if status != "ERRO":
            status, mensagem = cls._validar_conexao_real(integracao)
        cls.repository.registrar_teste(integracao_id, status, mensagem, usuario_email)
        return {"status": status, "mensagem": mensagem}

    @classmethod
    def historico_validacoes(cls, integracao_id, limite=10):
        return cls.repository.listar_historico(integracao_id, limite=limite)

    @classmethod
    def _com_diagnostico(cls, integracao):
        item = dict(integracao)
        diagnostico = cls._diagnostico_configuracao(item)
        item.update(diagnostico)
        return item

    @classmethod
    def _diagnostico_configuracao(cls, integracao):
        if not integracao.get("ativo"):
            return {
                "diagnostico_status": "inativa",
                "diagnostico_label": "Inativa",
                "diagnostico_classe": "secondary",
                "diagnostico_mensagem": "Configuração inativa, preservada apenas para consulta.",
            }
        status, mensagem = cls._validar_configuracao(integracao)
        if status == "ERRO":
            if not integracao.get("segredo_encrypted") and not integracao.get("possui_segredo"):
                return {
                    "diagnostico_status": "pendente_credencial",
                    "diagnostico_label": "Pendente de credencial",
                    "diagnostico_classe": "warning",
                    "diagnostico_mensagem": "Cadastre token ou senha antes da validação de conexão.",
                }
            return {
                "diagnostico_status": "erro_cadastro",
                "diagnostico_label": "Erro de cadastro",
                "diagnostico_classe": "danger",
                "diagnostico_mensagem": mensagem,
            }
        if not integracao.get("ultimo_teste_status"):
            return {
                "diagnostico_status": "pendente_teste",
                "diagnostico_label": "Pendente de teste",
                "diagnostico_classe": "info",
                "diagnostico_mensagem": "Configuração cadastrada, aguardando validação real read-only.",
            }
        if integracao.get("ultimo_teste_status") == "ERRO":
            return {
                "diagnostico_status": "erro_cadastro",
                "diagnostico_label": "Erro de cadastro",
                "diagnostico_classe": "danger",
                "diagnostico_mensagem": integracao.get("ultimo_teste_mensagem") or mensagem,
            }
        return {
            "diagnostico_status": "configurado",
            "diagnostico_label": "Configurado",
            "diagnostico_classe": "success",
            "diagnostico_mensagem": integracao.get("ultimo_teste_mensagem") or mensagem,
        }

    @classmethod
    def _validar_conexao_real(cls, integracao):
        tipo = integracao.get("tipo")
        if tipo in ("freeipa", "ldap", "ad"):
            return "OK", "Configuração estrutural de autenticação válida. Sincronismo e autenticação externa serão tratados pela etapa de Usuários e Acessos."
        if tipo not in ("proxmox", "pbs", "zabbix", "truenas", "clicksign"):
            return "OK", "Configuração estrutural válida. Validação real ainda não implementada para este tipo."
        try:
            segredo = cls.revelar_segredo_config(integracao.get("id"))
        except ValueError as erro:
            return "ERRO", str(erro)
        try:
            if tipo == "proxmox":
                return cls._testar_proxmox(integracao, segredo)
            if tipo == "pbs":
                return cls._testar_pbs(integracao, segredo)
            if tipo == "zabbix":
                return cls._testar_zabbix(integracao, segredo)
            if tipo == "truenas":
                return cls._testar_truenas(integracao, segredo)
            if tipo == "clicksign":
                return cls._testar_clicksign(integracao, segredo)
        except requests.exceptions.SSLError:
            integration_logger.exception("Integration SSL validation failed", extra={"service": tipo, "operation": "VALIDATE"})
            return "ERRO", "Falha na validação SSL do certificado. Ajuste a CA confiável ou desative Verificar SSL para este endpoint interno."
        except requests.exceptions.Timeout:
            integration_logger.exception("Integration request timed out", extra={"service": tipo, "operation": "VALIDATE"})
            return "ERRO", "Timeout ao conectar na API. Verifique host, porta, firewall e timeout configurado."
        except requests.exceptions.ConnectionError:
            integration_logger.exception("Integration connection failed", extra={"service": tipo, "operation": "VALIDATE"})
            return "ERRO", "Falha de conexão com a API. Verifique host, porta, rota de rede e firewall."
        except requests.exceptions.RequestException as erro:
            integration_logger.error("Integration HTTP validation failed: %s", cls._mensagem_segura(erro), extra={"service": tipo, "operation": "VALIDATE"})
            return "ERRO", f"Falha HTTP ao validar API: {cls._mensagem_segura(erro)}"
        except ValueError:
            integration_logger.error("Integration returned invalid response", extra={"service": tipo, "operation": "VALIDATE"})
            return "ERRO", "Resposta inválida da API. Endpoint respondeu, mas não retornou JSON esperado."
        return "ERRO", "Tipo de integração sem validador real."

    @classmethod
    def _testar_proxmox(cls, integracao, segredo):
        token_nome = cls._token_api_nome(integracao)
        headers = {"Authorization": f"PVEAPIToken={token_nome}={segredo}"}
        response = requests.get(
            f"{integracao.get('base_url').rstrip('/')}/api2/json/version",
            headers=headers,
            timeout=cls._timeout(integracao),
            verify=cls._verify_ssl(integracao),
        )
        if response.status_code in (401, 403):
            return "ERRO", "Proxmox respondeu, mas recusou autenticação/permissão do token."
        response.raise_for_status()
        version = ((response.json() or {}).get("data") or {}).get("version") or "ok"
        return "OK", f"Conexão Proxmox VE validada em modo leitura. Versão: {version}."

    @classmethod
    def _testar_pbs(cls, integracao, segredo):
        token_nome = cls._token_api_nome(integracao)
        headers = {"Authorization": f"PBSAPIToken={token_nome}:{segredo}"}
        response = requests.get(
            f"{integracao.get('base_url').rstrip('/')}/api2/json/version",
            headers=headers,
            timeout=cls._timeout(integracao),
            verify=cls._verify_ssl(integracao),
        )
        if response.status_code in (401, 403):
            return "ERRO", "PBS respondeu, mas recusou autenticação/permissão do token."
        response.raise_for_status()
        version = ((response.json() or {}).get("data") or {}).get("version") or "ok"
        return "OK", f"Conexão PBS validada em modo leitura. Versão: {version}."

    @classmethod
    def _testar_zabbix(cls, integracao, segredo):
        url = f"{integracao.get('base_url').rstrip('/')}/api_jsonrpc.php"
        payload = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {"output": ["hostid"], "limit": 1},
            "auth": segredo,
            "id": 1,
        }
        response = requests.post(
            url,
            json=payload,
            timeout=cls._timeout(integracao),
            verify=cls._verify_ssl(integracao),
        )
        body = response.json() if response.text else {}
        if response.ok and isinstance(body, dict) and "result" in body:
            return "OK", "Conexão Zabbix validada em modo leitura."
        payload.pop("auth", None)
        response = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {segredo}"},
            timeout=cls._timeout(integracao),
            verify=cls._verify_ssl(integracao),
        )
        body = response.json() if response.text else {}
        if response.ok and isinstance(body, dict) and "result" in body:
            return "OK", "Conexão Zabbix validada em modo leitura."
        if isinstance(body, dict) and body.get("error"):
            return "ERRO", f"Zabbix recusou a validação: {cls._mensagem_zabbix(body.get('error'))}"
        response.raise_for_status()
        return "ERRO", "Zabbix respondeu, mas sem resultado válido para consulta read-only."

    @classmethod
    def _testar_truenas(cls, integracao, segredo):
        response = requests.get(
            f"{integracao.get('base_url').rstrip('/')}/api/v2.0/system/info",
            headers={"Authorization": f"Bearer {segredo}"},
            timeout=cls._timeout(integracao),
            verify=cls._verify_ssl(integracao),
        )
        if response.status_code in (401, 403):
            return "ERRO", "TrueNAS respondeu, mas recusou autenticação/permissão do token."
        response.raise_for_status()
        hostname = (response.json() or {}).get("hostname") or "ok"
        return "OK", f"Conexão TrueNAS validada em modo leitura. Hostname: {hostname}."

    @classmethod
    def _testar_clicksign(cls, integracao, segredo):
        base_url = (integracao.get("base_url") or "").rstrip("/")
        response = requests.get(
            f"{base_url}/envelopes",
            headers={
                "Authorization": segredo,
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json",
            },
            params={"access_token": segredo},
            timeout=cls._timeout(integracao),
            verify=cls._verify_ssl(integracao),
        )
        if response.status_code in (401, 403):
            return "ERRO", f"Clicksign recusou autenticação/permissão: {cls._mensagem_http_json(response)}"
        response.raise_for_status()
        return "OK", "Conexão Clicksign validada em modo leitura."

    @staticmethod
    def _mensagem_http_json(response):
        try:
            payload = response.json()
        except ValueError:
            return (response.text or f"HTTP {response.status_code}")[:180]
        erros = payload.get("errors") if isinstance(payload, dict) else None
        if not erros:
            return str(payload)[:180]
        partes = []
        for erro in erros:
            titulo = erro.get("title") or "Erro"
            detalhe = erro.get("detail") or erro.get("code") or ""
            partes.append(f"{titulo}: {detalhe}".strip())
        return "; ".join(partes)[:180]

    @staticmethod
    def _token_api_nome(integracao):
        token_nome = (integracao.get("token_nome") or "").strip()
        usuario = (integracao.get("usuario") or "").strip()
        if "@" in token_nome and "!" in token_nome:
            return token_nome
        if usuario and token_nome:
            return f"{usuario}!{token_nome}"
        return token_nome or usuario

    @staticmethod
    def _timeout(integracao):
        return int(integracao.get("timeout_seconds") or 30)

    @staticmethod
    def _verify_ssl(integracao):
        return bool(integracao.get("verify_ssl"))

    @staticmethod
    def _mensagem_segura(erro):
        mensagem = str(erro)
        if len(mensagem) > 180:
            return mensagem[:177] + "..."
        return mensagem

    @staticmethod
    def _mensagem_zabbix(erro):
        if not isinstance(erro, dict):
            return "erro API"
        return erro.get("message") or erro.get("data") or "erro API"

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
        esquemas_validos = ("http", "https", "ldap", "ldaps") if integracao.get("tipo") == "freeipa" else (("ldap", "ldaps") if integracao.get("tipo") in ("ldap", "ad") else ("http", "https"))
        if parsed.scheme not in esquemas_validos or not parsed.netloc:
            return "ERRO", "URL base inválida."
        if not integracao.get("segredo_encrypted") and not integracao.get("possui_segredo"):
            return "ERRO", "Token ou senha não cadastrado."
        if integracao.get("tipo") in ("proxmox", "pbs", "freeipa", "ldap", "ad", "truenas") and not integracao.get("usuario") and not integracao.get("token_nome"):
            return "ERRO", "Informe usuário ou nome do token."
        if integracao.get("tipo") in ("zabbix", "omie", "clicksign") and not integracao.get("token_nome"):
            return "AVISO", "Configuração estrutural válida. Recomenda-se informar nome do token para auditoria."
        return "OK", "Configuração estrutural válida."

    @staticmethod
    def _normalizar_url(valor):
        texto = (valor or "").strip().rstrip("/")
        if not texto:
            return None
        parsed = urlparse(texto)
        if parsed.scheme not in ("http", "https", "ldap", "ldaps") or not parsed.netloc:
            raise ValueError("Informe uma URL base válida com http://, https://, ldap:// ou ldaps://.")
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
