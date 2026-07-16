from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.catalogo.import_service import ImportCatalogService
from app.importadores.base44 import Base44Importer


def main():
    arquivo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('catalogo_base44.csv')

    resultado = Base44Importer().executar(arquivo)

    if not resultado:
        print('Falha na leitura/interpretação do arquivo.')
        return 1

    resumo = ImportCatalogService().importar(resultado)
    ImportCatalogService.imprimir_resumo(resumo)

    if resumo['erros']:
        print('Importação concluída com erros.')
        return 1

    print('Importação concluída com sucesso.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
