from app.integracoes.omie.client import OmieClient

client = OmieClient()

pagina = 1

while True:

    resposta = client.listar_contratos(pagina)

    contratos = resposta.get("contratoCadastro", [])

    if not contratos:
        break

    for contrato in contratos:

        cab = contrato["cabecalho"]

        if cab["cNumCtr"] == "2026/00201":

            print(cab)

    if pagina >= resposta.get("total_de_paginas", pagina):
        break

    pagina += 1
