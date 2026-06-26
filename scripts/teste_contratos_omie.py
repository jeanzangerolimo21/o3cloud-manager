from pprint import pprint

from app.integracoes.omie.client import OmieClient


def main():

    client = OmieClient()

    resposta = client.listar_contratos()

    pprint(resposta)


if __name__ == "__main__":
    main()
