import re

import requests


class CnpjService:
    API_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    API_FALLBACK_URL = "https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    HEADERS = {
        "Accept": "application/json",
        "User-Agent": "O3Cloud-Manager/1.0",
    }

    @classmethod
    def consultar(cls, valor):
        cnpj = re.sub(r"\D", "", str(valor or ""))
        if len(cnpj) != 14:
            raise ValueError("Informe um CNPJ com 14 dígitos.")

        dados = cls._consultar_brasil_api(cnpj)
        if dados is None:
            dados = cls._consultar_receita_ws(cnpj)

        return {
            "cnpj": cnpj,
            "razao_social": dados.get("razao_social") or "",
            "nome_fantasia": dados.get("nome_fantasia") or dados.get("razao_social") or "",
            "email": cls._normalizar_email(dados.get("email")),
            "telefone": dados.get("ddd_telefone_1") or dados.get("ddd_telefone_2") or "",
            "cidade": dados.get("municipio") or "",
            "estado": dados.get("uf") or "",
        }

    @classmethod
    def _consultar_brasil_api(cls, cnpj):
        try:
            resposta = requests.get(
                cls.API_URL.format(cnpj=cnpj),
                headers=cls.HEADERS,
                timeout=10,
            )
        except requests.RequestException:
            return None

        if resposta.status_code == 404:
            raise LookupError("CNPJ não encontrado.")
        if resposta.status_code == 429 or resposta.status_code >= 500:
            return None
        try:
            resposta.raise_for_status()
            return resposta.json()
        except (requests.RequestException, ValueError):
            return None

    @classmethod
    def _consultar_receita_ws(cls, cnpj):
        try:
            resposta = requests.get(
                cls.API_FALLBACK_URL.format(cnpj=cnpj),
                headers=cls.HEADERS,
                timeout=15,
            )
        except requests.RequestException as erro:
            raise RuntimeError("Os serviços de consulta de CNPJ estão indisponíveis.") from erro

        if resposta.status_code == 429:
            raise RuntimeError("Os serviços de consulta de CNPJ atingiram o limite de consultas. Tente novamente em alguns minutos.")
        try:
            resposta.raise_for_status()
            dados = resposta.json()
        except (requests.RequestException, ValueError) as erro:
            raise RuntimeError("Os serviços de consulta de CNPJ retornaram uma resposta inválida.") from erro

        if str(dados.get("status", "")).upper() == "ERROR":
            mensagem = dados.get("message") or "CNPJ não encontrado."
            raise LookupError(mensagem)

        return {
            "razao_social": dados.get("nome") or "",
            "nome_fantasia": dados.get("fantasia") or dados.get("nome") or "",
            "email": dados.get("email") or "",
            "ddd_telefone_1": dados.get("telefone") or "",
            "municipio": dados.get("municipio") or "",
            "uf": dados.get("uf") or "",
        }

    @staticmethod
    def _normalizar_email(valor):
        return str(valor or "").strip().rstrip(".,;")
