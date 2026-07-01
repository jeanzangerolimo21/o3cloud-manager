from app.integracoes.omie.client import OmieClient
from app.integracoes.omie.contrato_mapper import ContratoMapper

from app.repositories.cliente_repository import ClienteRepository
from app.repositories.contrato_repository import ContratoRepository


class ContratoService:
    """
    Regras de negócio dos contratos.
    """

    @classmethod
    def sincronizar_contrato(cls, contrato_omie):


        dados = ContratoMapper.from_omie(contrato_omie)
        cliente = ClienteRepository.buscar_por_codigo_externo(
            dados["cliente_codigo_externo"]
        )

        if not cliente:
            return {
                "status": "IGNORADO",
                "numero": dados["numero"],
                "motivo": "Cliente não encontrado"
        }

        dados["cliente_id"] = cliente["id"]

        contrato = ContratoRepository.buscar_por_codigo_externo(
            dados["codigo_externo"]
        )

        if contrato:

            ContratoRepository.atualizar_sync(
                contrato["id"],
                dados
            )

            return {
                "status": "UPDATE",
                "numero": dados["numero"]
            }

        ContratoRepository.inserir(dados)

        return {
            "status": "INSERT",
            "numero": dados["numero"]
        }


    @classmethod
    def sincronizar(cls):

        omie = OmieClient()

        resposta = omie.listar_contratos()

        resultado = []

        for contrato in resposta.get("contratoCadastro", []):

            resultado.append(

                cls.sincronizar_contrato(
                    contrato
                )
            )

        return resultado

    @classmethod
    def criar(cls, dados):

        ContratoRepository.inserir_manual(dados)

    @classmethod
    def atualizar(cls, contrato_id, dados):

        ContratoRepository.atualizar(

            contrato_id,

            dados

        )
