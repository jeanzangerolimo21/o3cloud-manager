import base64
import os
from pathlib import Path
from urllib.parse import unquote
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()


class ClicksignError(Exception):
    pass


class ClicksignClient:
    DEFAULT_BASE_URL = "https://sandbox.clicksign.com/api/v3"

    def __init__(self):
        self.access_token = (os.getenv("CLICKSIGN_ACCESS_TOKEN") or "").strip()
        configured_url = (os.getenv("CLICKSIGN_API_URL") or "").strip()
        self.base_url = self._base_url(configured_url)
        if not self.access_token:
            raise ClicksignError("CLICKSIGN_ACCESS_TOKEN nao configurado no .env.")

    def enviar_contrato(self, *, nome_envelope, caminho_documento, nome_documento, signatario=None, signatarios=None):
        caminho = Path(caminho_documento)
        if not caminho.exists():
            raise ClicksignError("Documento do contrato nao encontrado para envio ao Clicksign.")

        signatarios_envio = list(signatarios or [])
        if signatario:
            signatarios_envio.insert(0, signatario)
        if not signatarios_envio:
            raise ClicksignError("Informe ao menos um signatario para envio ao Clicksign.")

        envelope = self.criar_envelope(nome_envelope)
        envelope_id = envelope["id"]
        documento = self.adicionar_documento(envelope_id, caminho, nome_documento)
        signatarios_criados = []
        for item in signatarios_envio:
            signatario_criado = self.adicionar_signatario(envelope_id, item)
            signatarios_criados.append(signatario_criado)
            self.criar_requisito_assinatura(envelope_id, documento["id"], signatario_criado["id"], item.get("role") or "sign")
            self.criar_requisito_autenticacao_email(envelope_id, documento["id"], signatario_criado["id"])
        self.ativar_envelope(envelope_id)
        self.enviar_notificacoes(envelope_id)
        return {
            "envelope_id": envelope_id,
            "document_id": documento["id"],
            "signer_id": signatarios_criados[0]["id"],
            "signer_ids": [item["id"] for item in signatarios_criados],
            "status": "running",
        }

    def criar_envelope(self, nome):
        payload = {
            "data": {
                "type": "envelopes",
                "attributes": {"name": nome},
            }
        }
        return self._data(self._request("POST", "/envelopes", json=payload))

    def adicionar_documento(self, envelope_id, caminho, nome_documento):
        conteudo = base64.b64encode(Path(caminho).read_bytes()).decode("ascii")
        payload = {
            "data": {
                "type": "documents",
                "attributes": {
                    "filename": nome_documento,
                    "content_base64": f"data:application/pdf;base64,{conteudo}",
                },
            }
        }
        return self._data(self._request("POST", f"/envelopes/{envelope_id}/documents", json=payload))

    def adicionar_signatario(self, envelope_id, signatario):
        atributos = {
            "name": (signatario.get("name") or "").strip(),
            "email": (signatario.get("email") or "").strip().lower(),
        }
        if not atributos["name"] or not atributos["email"]:
            raise ClicksignError("Informe nome e e-mail do contato antes de enviar para Clicksign.")

        payload = {
            "data": {
                "type": "signers",
                "attributes": atributos,
            }
        }
        return self._data(self._request("POST", f"/envelopes/{envelope_id}/signers", json=payload))

    def criar_requisito_assinatura(self, envelope_id, document_id, signer_id, role="sign"):
        payload = self._payload_requisito(
            document_id,
            signer_id,
            {"action": "agree", "role": role},
        )
        return self._data(self._request("POST", f"/envelopes/{envelope_id}/requirements", json=payload))

    def criar_requisito_autenticacao_email(self, envelope_id, document_id, signer_id):
        payload = self._payload_requisito(
            document_id,
            signer_id,
            {"action": "provide_evidence", "auth": "email"},
        )
        return self._data(self._request("POST", f"/envelopes/{envelope_id}/requirements", json=payload))

    def ativar_envelope(self, envelope_id):
        payload = {
            "data": {
                "id": envelope_id,
                "type": "envelopes",
                "attributes": {"status": "running"},
            }
        }
        return self._data(self._request("PATCH", f"/envelopes/{envelope_id}", json=payload))

    def enviar_notificacoes(self, envelope_id):
        payload = {"data": {"type": "notifications", "attributes": {}}}
        return self._request("POST", f"/envelopes/{envelope_id}/notifications", json=payload)

    def consultar_envelope(self, envelope_id):
        return self._data(self._request("GET", f"/envelopes/{envelope_id}"))

    def listar_documentos(self, envelope_id):
        payload = self._request("GET", f"/envelopes/{envelope_id}/documents")
        return payload.get("data") or []

    def baixar_documento_assinado(self, envelope_id):
        for documento in self.listar_documentos(envelope_id):
            signed_url = (((documento.get("links") or {}).get("files") or {}).get("signed"))
            if signed_url:
                response = requests.get(signed_url, timeout=60)
                if response.status_code >= 400:
                    raise ClicksignError(f"Erro ao baixar PDF assinado da Clicksign: HTTP {response.status_code}")
                return {
                    "document_id": documento.get("id"),
                    "filename": self._filename_download(signed_url),
                    "content": response.content,
                }
        raise ClicksignError("Documento assinado ainda nao esta disponivel para download na Clicksign.")

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": self.access_token,
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        }
        params = kwargs.pop("params", {}) or {}
        params.setdefault("access_token", self.access_token)
        response = requests.request(method, url, headers=headers, params=params, timeout=60, **kwargs)
        if response.status_code >= 400:
            raise ClicksignError(self._mensagem_erro(response))
        if not response.text:
            return {}
        return response.json()

    @staticmethod
    def _data(payload):
        data = payload.get("data") if isinstance(payload, dict) else None
        if not data or not data.get("id"):
            raise ClicksignError("Resposta inesperada da Clicksign.")
        return data

    @staticmethod
    def _payload_requisito(document_id, signer_id, attributes):
        return {
            "data": {
                "type": "requirements",
                "attributes": attributes,
                "relationships": {
                    "document": {"data": {"type": "documents", "id": document_id}},
                    "signer": {"data": {"type": "signers", "id": signer_id}},
                },
            }
        }

    @classmethod
    def _base_url(cls, configured_url):
        if not configured_url:
            return cls.DEFAULT_BASE_URL
        parsed = urlparse(configured_url)
        if parsed.scheme and parsed.netloc and "/api/v3" in parsed.path:
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path.split('/api/v3', 1)[0]}/api/v3"
        return configured_url.rstrip("/")

    @staticmethod
    def _mensagem_erro(response):
        try:
            payload = response.json()
        except ValueError:
            return f"Clicksign retornou HTTP {response.status_code}: {response.text[:300]}"
        erros = payload.get("errors") if isinstance(payload, dict) else None
        if erros:
            partes = []
            for erro in erros:
                titulo = erro.get("title") or "Erro"
                detalhe = erro.get("detail") or erro.get("code") or ""
                partes.append(f"{titulo}: {detalhe}".strip())
            return f"Clicksign retornou HTTP {response.status_code}: " + "; ".join(partes)
        return f"Clicksign retornou HTTP {response.status_code}: {str(payload)[:300]}"

    @staticmethod
    def _filename_download(url):
        path = urlparse(url).path
        nome = unquote(Path(path).name or "contrato-assinado.pdf")
        return nome if nome.lower().endswith(".pdf") else f"{nome}.pdf"

    @classmethod
    def _documentacao_valida(cls, valor):
        documento = cls._somente_digitos(valor)
        return documento if len(documento) in (11, 14) else ""

    @staticmethod
    def _somente_digitos(valor):
        return "".join(ch for ch in str(valor or "") if ch.isdigit())
