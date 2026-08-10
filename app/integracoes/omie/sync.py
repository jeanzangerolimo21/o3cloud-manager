from app.integracoes.omie.client import OmieClient
from app.core.logging_config import get_logger
from app.integracoes.omie.cliente_mapper import ClienteMapper
from app.contratos.service import ContratoService
from app.clientes.service import ClienteService
from app.repositories.sync_repository import SyncRepository
from app.contratos.item_service import ContratoItemService


logger = get_logger("integrations")


def _log(mensagem=""):
    try:
        logger.info(mensagem)
    except OSError:
        pass


class OmieSync:

    def __init__(self):
        self.client = OmieClient()


    def sincronizar_clientes(self):

        _log("=" * 60)
        _log("Iniciando sincronização de clientes OMIE...")
        _log("=" * 60)

        sync_id = SyncRepository.iniciar("OMIE")

        pagina = 1

        processados = 0
        novos = 0
        atualizados = 0

        try:

            while True:

                _log(f"\nLendo página {pagina}...")

                resposta = self.client.listar_clientes(pagina)

                clientes = resposta.get("clientes_cadastro", [])

                if not clientes:
                    break

                for cliente in clientes:

                    dados = ClienteMapper.from_omie(cliente)

                    _log(f"Cliente: {dados['nome_fantasia']}")

                    resultado = ClienteService.sincronizar_omie(dados)

                    _log(f"Resultado: {resultado}")

                    if resultado == "INSERT":
                        novos += 1
                    else:
                        atualizados += 1

                    processados += 1

                total_paginas = resposta.get("total_de_paginas", pagina)


                _log(
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

            _log("\n=====================================")
            _log("Sincronização concluída com sucesso!")
            _log(f"Processados : {processados}")
            _log(f"Inseridos   : {novos}")
            _log(f"Atualizados : {atualizados}")
            _log("=====================================\n")

        except Exception as erro:

            _log("\nERRO DURANTE A SINCRONIZAÇÃO")
            _log(str(erro))

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

    def sincronizar_contratos(self):

        _log("=" * 60)
        _log("Iniciando sincronização de contratos OMIE...")
        _log("=" * 60)

        sync_id = SyncRepository.iniciar("OMIE")

        pagina = 1

        processados = 0
        novos = 0
        atualizados = 0
        ignorados = 0

        try:

            while True:

                _log(f"\nLendo página {pagina}...")

                resposta = self.client.listar_contratos(pagina)

                contratos = resposta.get("contratoCadastro", [])

                if not contratos:
                    break

                for contrato in contratos:


                    resultado = ContratoService.sincronizar_contrato(contrato)

                    itens = ContratoItemService.sincronizar_itens(contrato)
                    if isinstance(itens, list):
                        _log(f"Itens sincronizados: {len(itens)}")

                    _log(resultado)

                    status = resultado["status"]

                    if status == "INSERT":
                        novos += 1

                    elif status == "UPDATE":
                        atualizados += 1

                    elif status == "IGNORADO":
                        ignorados += 1

                    processados += 1

                total_paginas = resposta.get(
                    "total_de_paginas",
                    pagina
                )

                _log(

                    f"[Página {pagina}/{total_paginas}] "

                    f"Processados: {processados} "

                    f"Novos: {novos} "

                    f"Atualizados: {atualizados} "

                    f"Ignorados: {ignorados}"

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
                ignorados
            )

            return {
                "processados": processados,
                "novos": novos,
                "atualizados": atualizados,
                "ignorados": ignorados
            }

        except Exception as erro:

            SyncRepository.finalizar(
                sync_id,
                "ERRO",
                processados,
                novos,
                atualizados,
                ignorados,
                str(erro)
            )

            raise erro

