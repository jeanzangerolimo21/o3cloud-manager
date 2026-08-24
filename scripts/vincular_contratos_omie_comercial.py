import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.contratos.service import ContratoService


def main():
    resultado = ContratoService.preencher_vinculos_comerciais_omie_existentes()
    print(f"Contratos Omie processados: {resultado['processados']}")
    print(f"Contratos atualizados: {resultado['atualizados']}")
    print(f"Parceiros vinculados: {resultado['parceiro_match']}")
    print(f"Executivos vinculados: {resultado['executivo_match']}")

    if resultado["sem_parceiro"]:
        print("Vendedores Omie sem parceiro correspondente:")
        for nome in resultado["sem_parceiro"]:
            print(f"- {nome}")

    if resultado["sem_executivo"]:
        print("Projetos Omie sem executivo correspondente:")
        for nome in resultado["sem_executivo"]:
            print(f"- {nome}")


if __name__ == "__main__":
    main()
