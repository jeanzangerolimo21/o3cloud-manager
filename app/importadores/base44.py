"""
Importador Base44

Fluxo:

CSV
    ↓
CSVReader
    ↓
Parser
    ↓
Normalizador
    ↓
ResultadoImportacao

Nesta primeira versão NÃO grava no banco.
"""

from pathlib import Path

from .base import BaseImporter
from .csv_reader import CSVReader
from .parser import Base44Parser
from .normalizador import Base44Normalizador


class Base44Importer(BaseImporter):

    def __init__(self):

        super().__init__()

        self.reader = None
        self.parser = Base44Parser()
        self.normalizador = Base44Normalizador()

    ######################################################################
    # Importação
    ######################################################################

    def executar(self, arquivo):

        arquivo = Path(arquivo)

        if not arquivo.exists():

            self.adicionar_erro(
                f"Arquivo não encontrado: {arquivo}"
            )

            return None

        self.info(f"Lendo arquivo: {arquivo.name}")

        self.reader = CSVReader(arquivo)

        registros_csv = self.reader.ler()

        self.info(
            f"{len(registros_csv)} registros encontrados."
        )

        registros = []

        for linha in registros_csv:

            objeto = self.parser.parse(linha)

            if objeto:

                registros.append(objeto)

        self.info(

            f"{len(registros)} registros interpretados."

        )

        resultado = self.normalizador.normalizar(

            registros

        )

        self.info("Normalização concluída.")

        self._mostrar_resumo(resultado)

        return resultado

    ######################################################################
    # Resumo
    ######################################################################

    def _mostrar_resumo(self, resultado):

        print()

        print("=" * 60)

        print("RESUMO DA IMPORTAÇÃO BASE44")

        print("=" * 60)

        print(f"Categorias : {len(resultado.categorias)}")

        print(f"Produtos   : {len(resultado.produtos)}")

        print(f"Modelos    : {len(resultado.modelos)}")

        print(f"Faixas     : {len(resultado.faixas)}")

        print(f"Recursos   : {len(resultado.recursos)}")

        print(f"Preços     : {len(resultado.precos)}")

        print(f"Avisos     : {len(resultado.avisos)}")

        print(f"Erros      : {len(resultado.erros)}")

        print("=" * 60)

        print()

        if resultado.erros:

            print("ERROS")

            print("-" * 60)

            for erro in resultado.erros:

                print(f" • {erro}")

            print()

        if resultado.avisos:

            print("AVISOS")

            print("-" * 60)

            for aviso in resultado.avisos:

                print(f" • {aviso}")

            print()
