import re

from decimal import Decimal, InvalidOperation

from .models import (
    ProdutoImportado,
    RecursoImportado,
)


class Base44Parser:

    PRODUTOS = {
        "LOGUS STORE": "Logus Store",
        "LOGUS": "Logus",
        "TARGET": "Target",
        "USUARIO ADICIONAL": "Usuario Adicional",
        "USUÁRIO ADICIONAL": "Usuario Adicional",
        "PACOTE UPGRADE": "Upgrade",
        "VPN": "VPN",
        "WINDOWS SERVER": "Windows Server",
        "O3 WEB": "O3 WEB",
        "REMOTEAPP": "RemoteAPP",
        "NAS STORAGE": "NAS Storage",
        "NVME": "NVME",
        "VCPUS": "vCPU",
        "RAM": "RAM",
        "SNAPSHOT": "Snapshot",
        "IPV4": "IPV4/IPV6",
        "VR": "VR",
    }

    @staticmethod
    def _campo(registro, *nomes, default=""):
        for nome in nomes:
            if nome in registro and registro.get(nome) not in (None, ""):
                return registro.get(nome)
        return default

    def parse(self, registro):
        tipo = self._campo(registro, "Tipo").strip()

        if tipo in ("Licenca por Usuario", "Licença por Usuário"):
            return self._parse_licenca(registro)

        if tipo == "Recurso de Servidor":
            return self._parse_recurso(registro)

        return None

    def _decimal(self, valor):
        if not valor:
            return Decimal("0")

        try:
            valor = (
                str(valor)
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
            return Decimal(valor)
        except InvalidOperation:
            return Decimal("0")

    def _boolean(self, valor):
        return str(valor).strip().lower() == "sim"

    def _status(self, valor):
        return str(valor).strip().lower() == "ativo"

    def _produto(self, texto):
        texto = str(texto).upper()

        for chave, produto in self.PRODUTOS.items():
            if chave in texto:
                return produto

        return texto.title()

    def _faixa(self, texto):
        numeros = re.findall(r"\d+", str(texto))

        if len(numeros) >= 2:
            return (
                int(numeros[0]),
                int(numeros[1]),
            )

        if len(numeros) == 1:
            numero = int(numeros[0])
            return numero, numero

        return None, None

    def _parse_licenca(self, registro):
        software = self._campo(
            registro,
            "Software",
            "Software/Categoria",
            "Nome/Categoria",
        )

        descricao = self._campo(
            registro,
            "Descricao",
            "Descrição",
            "Descrição/Nome",
            "Descricao/Nome",
            default=software,
        )
        inicio, fim = self._faixa(software)

        quantidade = self._campo(
            registro,
            "Qtd Minima",
            "Qtd Mínima",
            default="",
        )

        try:
            quantidade = int(quantidade)
        except Exception:
            quantidade = 1

        return ProdutoImportado(
            tipo="LICENCA",
            categoria="Licenciamento",
            descricao=descricao,
            ativo=self._status(self._campo(registro, "Status")),
            produto=self._produto(software),
            nome_comercial=software,
            modelo="STANDARD",
            faixa_inicio=inicio,
            faixa_fim=fim,
            valor_mensal=self._decimal(
                self._campo(registro, "Preco Mensal (R$)", "Preço Mensal (R$)")
            ),
            valor_setup=self._decimal(
                self._campo(
                    registro,
                    "Preco Minimo/Setup (R$)",
                    "Preço Mínimo/Setup (R$)",
                    "Preco Min. / Setup (R$)",
                    "Preço Mín. / Setup (R$)",
                )
            ),
            quantidade_minima=quantidade,
            tem_projeto=self._boolean(self._campo(registro, "Tem Projeto")),
        )

    def _parse_recurso(self, registro):
        grupo = self._campo(
            registro,
            "Categoria",
            "Software/Categoria",
            "Nome/Categoria",
        )
        recurso = self._campo(
            registro,
            "Recurso",
            "Nome",
            "Descrição/Nome",
            "Descricao/Nome",
            default=grupo,
        )
        descricao = self._campo(
            registro,
            "Descricao",
            "Descrição",
            default=recurso,
        )

        return RecursoImportado(
            tipo="RECURSO",
            categoria="Recursos Cloud",
            descricao=descricao,
            ativo=self._status(self._campo(registro, "Status")),
            produto=(recurso or grupo).strip(),
            grupo=grupo.strip(),
            modelo="PADRAO",
            unidade=None,
            valor_mensal=self._decimal(
                self._campo(registro, "Preco Mensal (R$)", "Preço Mensal (R$)")
            ),
            valor_setup=self._decimal(
                self._campo(
                    registro,
                    "Preco Minimo/Setup (R$)",
                    "Preço Mínimo/Setup (R$)",
                    "Preco Min. / Setup (R$)",
                    "Preço Mín. / Setup (R$)",
                )
            ),
        )
