import os
import requests
from dotenv import load_dotenv

load_dotenv()


class OmieClient:

    BASE_CONTRATOS = "https://app.omie.com.br/api/v1/servicos/contrato/"
    BASE_CLIENTES = "https://app.omie.com.br/api/v1/geral/clientes/"

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

        response = requests.post(
            url,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

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
                "apenas_importado_api": "N"
            }

        )
