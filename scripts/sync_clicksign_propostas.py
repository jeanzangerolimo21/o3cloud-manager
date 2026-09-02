import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.propostas.service import PropostaService


def main():
    app = create_app()
    print("Sincronizando propostas pendentes na ClickSign...")
    with app.app_context():
        resultados = PropostaService.sincronizar_clicksign_pendentes("sync-clicksign")
    if not resultados:
        print("Nenhuma proposta pendente para sincronizar.")
        return
    for item in resultados:
        if item["status"] == "OK":
            print(f"OK proposta #{item['id']} {item.get('codigo_proposta') or ''}: {item['clicksign_status']}")
        else:
            print(f"ERRO proposta #{item['id']} {item.get('codigo_proposta') or ''}: {item['erro']}")


if __name__ == "__main__":
    main()
