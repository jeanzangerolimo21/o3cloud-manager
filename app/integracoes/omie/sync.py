from app.integracoes.omie.client import OmieClient
from app.integracoes.omie.mapper import OmieMapper

from app.clientes.service import ClienteService
from app.repositories.sync_repository import SyncRepository


class OmieSync:

    def __init__(self):
        self.client = OmieClient()


    def sincronizar_clientes(self):

        print("=" * 60)
        print("Iniciando sincronização de clientes OMIE...")
        print("=" * 60)

        sync_id = SyncRepository.iniciar("OMIE")

        pagina = 1

        processados = 0
        novos = 0
        atualizados = 0

        try:

            while True:

                print(f"\nLendo página {pagina}...")

                resposta = self.client.listar_clientes(pagina)

                clientes = resposta.get("clientes_cadastro", [])

                if not clientes:
                    break

                for cliente in clientes:

                    dados = OmieMapper.cliente(cliente)

                    print(f"Cliente: {dados['nome_fantasia']}")

                    resultado = ClienteService.sincronizar_omie(dados)

                    print(f"Resultado: {resultado}")

                    if resultado == "INSERT":
                        novos += 1
                    else:
                        atualizados += 1

                    processados += 1

                total_paginas = resposta.get("total_de_paginas", pagina)


                print(
                    f"[Página {pagina}/{total_paginas}] "
                    f"Processados: {processados} "
                    f"Novos: {novos} "
                    f"Atualizados: {atualizados}"

                )
                
                if pagina >= total_paginas:
                   break

                pagina += 1


            SyncRepository.finalizar(

                sync_id,
                "SUCESSO",
                processados,
                novos,
                atualizados,
                0

            )

            print("\n=====================================")
            print("Sincronização concluída com sucesso!")
            print(f"Processados : {processados}")
            print(f"Inseridos   : {novos}")
            print(f"Atualizados : {atualizados}")
            print("=====================================\n")

        except Exception as erro:

            print("\nERRO DURANTE A SINCRONIZAÇÃO")
            print(str(erro))  

            SyncRepository.finalizar(

                sync_id,
                "ERRO",
                processados,
                novos,
                atualizados,
                1,
                str(erro)

            )

            raise
