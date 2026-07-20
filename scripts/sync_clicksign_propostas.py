from app.propostas.service import PropostaService


def main():
    print("Sincronizando propostas pendentes na ClickSign...")
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
