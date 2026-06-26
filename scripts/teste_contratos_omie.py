from app.integracoes.omie.sync import OmieSync


def main():

    sync = OmieSync()

    resultado = sync.sincronizar_contratos()

    print(resultado)


if __name__ == "__main__":
    main()
