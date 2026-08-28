import os
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
                if tentativa == 2:
                    raise
                time.sleep(2 ** tentativa)
        raise ultimo_erro

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

            {"nCodOS": codigo_os}

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
