import os
import re
import requests
import time
from dotenv import load_dotenv

load_dotenv()


class OmieClient:

    BASE_CONTRATOS = "https://app.omie.com.br/api/v1/servicos/contrato/"
    BASE_CLIENTES = "https://app.omie.com.br/api/v1/geral/clientes/"
    BASE_PROJETOS = "https://app.omie.com.br/api/v1/geral/projetos/"
    BASE_VENDEDORES = "https://app.omie.com.br/api/v1/geral/vendedores/"
    BASE_CONTAS_RECEBER = "https://app.omie.com.br/api/v1/financas/contareceber/"
    BASE_CATEGORIAS = "https://app.omie.com.br/api/v1/geral/categorias/"
    BASE_OS = "https://app.omie.com.br/api/v1/servicos/os/"

    def __init__(self):

        self.app_key = os.getenv("OMIE_APP_KEY")
        self.app_secret = os.getenv("OMIE_APP_SECRET")

    def _post(self, url, call, params):

        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params]
        }

        ultimo_erro = None
        for tentativa in range(3):
            response = None
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as erro:
                ultimo_erro = erro
                espera_redundante = _espera_consumo_redundante(response)
                if espera_redundante and tentativa < 2:
                    time.sleep(espera_redundante)
                    continue
                if tentativa == 2:
                    raise RuntimeError(_erro_omie(call, response, erro)) from erro
                time.sleep(2 ** tentativa)
        raise RuntimeError(str(ultimo_erro))

    # -----------------------------------------
    # CLIENTES
    # -----------------------------------------

    def listar_clientes(self, pagina=1):

        return self._post(

            self.BASE_CLIENTES,

            "ListarClientes",

            {
                "pagina": pagina,
                "registros_por_pagina": 100,
                "apenas_importado_api": "N"
            }

        )

    # -----------------------------------------
    # CONTRATOS
    # -----------------------------------------

    def listar_contratos(self, pagina=1):

        return self._post(

            self.BASE_CONTRATOS,

            "ListarContratos",

            {
                "pagina": pagina,
                "registros_por_pagina": 100,
                "apenas_importado_api": "N",
                "cExibeObs": "S"
            }

        )


    # -----------------------------------------
    # ORDENS DE SERVIÇO
    # -----------------------------------------

    def listar_ordens_servico(self, pagina=1, filtros=None):

        params = {
            "pagina": pagina,
            "registros_por_pagina": 100,
            "apenas_importado_api": "N",
            "ordem_descrescente": "S",
        }
        if filtros:
            params.update(filtros)

        return self._post(

            self.BASE_OS,

            "ListarOS",

            params

        )

    def status_ordem_servico(self, codigo_os):

        return self._post(

            self.BASE_OS,

            "StatusOS",

            {"nCodOS": int(codigo_os)}

        )

    # -----------------------------------------
    # CADASTROS AUXILIARES
    # -----------------------------------------

    def listar_vendedores(self, pagina=1):

        return self._post(

            self.BASE_VENDEDORES,

            "ListarVendedores",

            {
                "pagina": pagina,
                "registros_por_pagina": 100
            }

        )

    def listar_projetos(self, pagina=1):

        return self._post(

            self.BASE_PROJETOS,

            "ListarProjetos",

            {
                "pagina": pagina,
                "registros_por_pagina": 100
            }

        )

    # -----------------------------------------
    # FINANCEIRO
    # -----------------------------------------

    def listar_categorias(self, pagina=1):

        return self._post(

            self.BASE_CATEGORIAS,

            "ListarCategorias",

            {
                "pagina": pagina,
                "registros_por_pagina": 100
            }

        )

    def listar_contas_receber(self, pagina=1, filtros=None):

        params = {
            "pagina": pagina,
            "registros_por_pagina": 100,
        }
        if filtros:
            params.update(filtros)

        return self._post(

            self.BASE_CONTAS_RECEBER,

            "ListarContasReceber",

            params

        )

def _erro_omie(call, response, erro):
    if response is None:
        return f"Omie {call} falhou: {erro}"
    detalhe = _detalhe_resposta_omie(response) or str(erro)
    return f"Omie {call} falhou HTTP {response.status_code}: {detalhe[:300]}"


def _espera_consumo_redundante(response):
    detalhe = _detalhe_resposta_omie(response)
    if "REDUNDANT" not in detalhe.upper():
        return None
    match = re.search(r"Aguarde\s+(\d+)\s+segundos", detalhe, re.IGNORECASE)
    segundos = int(match.group(1)) if match else 60
    return min(max(segundos + 2, 5), 70)


def _detalhe_resposta_omie(response):
    if response is None:
        return ""
    try:
        corpo = response.json()
        detalhe = corpo.get("faultstring") or corpo.get("description") or corpo.get("message") or str(corpo)
    except ValueError:
        detalhe = response.text or ""
    return " ".join(str(detalhe).split())

