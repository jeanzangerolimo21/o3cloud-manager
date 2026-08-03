from app.repositories.ambiente_repository import AmbienteRepository
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.parceiro_repository import ParceiroRepository
from app.repositories.contrato_repository import ContratoRepository
from app.repositories.proxmox_inventory_repository import ProxmoxInventoryRepository
from app.ambientes.implantador_service import ImplantadorService

FORM_LIMIT = 1000

class AmbienteService:

    @staticmethod
    def listar(pesquisa=None, pagina=1):

        limite = 50

        offset = (pagina - 1) * limite

        ambientes = AmbienteRepository.listar(

            pesquisa=pesquisa,

            limit=limite,

            offset=offset

        )

        total = AmbienteRepository.total(

            pesquisa=pesquisa

        )

        return ambientes, total

    @staticmethod
    def buscar_por_id(ambiente_id):

        ambiente = AmbienteRepository.buscar_por_id(

            ambiente_id

        )
        if ambiente:
            ambiente = dict(ambiente)
            ambiente["vinculos"] = AmbienteRepository.buscar_vinculos(ambiente_id)
            ambiente["cliente_ids"] = [item["id"] for item in ambiente["vinculos"]["clientes"]]
            ambiente["contrato_ids"] = [item["id"] for item in ambiente["vinculos"]["contratos"]]
            ambiente["recurso_ids"] = [item["id"] for item in ambiente["vinculos"]["recursos"]]
        return ambiente

    @staticmethod
    def buscar_por_cliente(cliente_id):

        return AmbienteRepository.buscar_por_cliente(

            cliente_id

        )

    @staticmethod
    def criar(dados):

        payload = AmbienteService._normalizar_vinculos(dados)
        ambiente_id = AmbienteRepository.inserir(

            payload

        )
        AmbienteRepository.salvar_vinculos(
            ambiente_id,
            payload.get("cliente_ids"),
            payload.get("contrato_ids"),
            payload.get("recurso_ids"),
        )
        return ambiente_id

    @staticmethod
    def atualizar(ambiente_id, dados):

        payload = AmbienteService._normalizar_vinculos(dados)
        AmbienteRepository.atualizar(

            ambiente_id,

            payload

        )
        AmbienteRepository.salvar_vinculos(
            ambiente_id,
            payload.get("cliente_ids"),
            payload.get("contrato_ids"),
            payload.get("recurso_ids"),
        )

    @staticmethod
    def excluir(ambiente_id):

        AmbienteRepository.excluir(

            ambiente_id

        )

    @staticmethod
    def carregar_dependencias_formulario():

            clientes = ClienteRepository.listar(
                limit=FORM_LIMIT,
                offset=0
            )

            parceiros = ParceiroRepository.listar(
                limit=FORM_LIMIT,
                offset=0
            )

            contratos = ContratoRepository.listar_para_ambientes(
                limit=FORM_LIMIT,
                offset=0
            )

            return {

                "clientes": clientes,

                "parceiros": parceiros,

                "contratos": contratos,

                # Sprint 7
                "clusters": [],

                # Sprint 7
                "nodes": [],

                # Sprint 8
                "storage": [],

                # Sprint 8
                "equipes": [],

                "recursos_proxmox": ProxmoxInventoryRepository.listar(),

                "implantadores": ImplantadorService.listar_para_select(),

            }

    @staticmethod
    def _normalizar_vinculos(dados):
        payload = dict(dados)
        cliente_ids = AmbienteService._ids(payload.get("cliente_ids"))
        contrato_ids = AmbienteService._ids(payload.get("contrato_ids"))
        recurso_ids = AmbienteService._ids(payload.get("recurso_ids"))
        implantador_ids = AmbienteService._ids([payload.get("implantador_id")])
        parceiro_ids = AmbienteService._ids([payload.get("parceiro_id")])
        if not cliente_ids and payload.get("cliente_id"):
            cliente_ids = AmbienteService._ids([payload.get("cliente_id")])
        if not contrato_ids and payload.get("contrato_id"):
            contrato_ids = AmbienteService._ids([payload.get("contrato_id")])
        if not cliente_ids:
            raise ValueError("Selecione pelo menos um cliente para o ambiente.")
        payload["cliente_ids"] = cliente_ids
        payload["contrato_ids"] = contrato_ids
        payload["recurso_ids"] = recurso_ids
        payload["cliente_id"] = cliente_ids[0]
        payload["contrato_id"] = contrato_ids[0] if contrato_ids else None
        payload["implantador_id"] = implantador_ids[0] if implantador_ids else None
        payload["parceiro_id"] = parceiro_ids[0] if parceiro_ids else None
        return payload

    @staticmethod
    def _ids(valores):
        ids = []
        for valor in valores or []:
            try:
                item = int(valor)
            except (TypeError, ValueError):
                continue
            if item and item not in ids:
                ids.append(item)
        return ids
