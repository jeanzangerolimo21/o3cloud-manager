from app.implantacao.service import KANBAN_LABELS
from app.implantacao.service import STATUS_IMPLANTACAO
from app.implantacao.service import STATUS_PROVISIONAMENTO
from app.repositories.implantacao_workflow_repository import ImplantacaoWorkflowRepository


class ImplantacaoService:

    @staticmethod
    def buscar(cliente_id):

        implantacao = ImplantacaoWorkflowRepository.buscar_por_cliente_id(cliente_id)
        if not implantacao:
            return None

        implantacao = dict(implantacao)
        implantacao["status_label"] = STATUS_IMPLANTACAO.get(
            implantacao.get("status"),
            implantacao.get("status") or "-",
        )
        implantacao["etapa_label"] = KANBAN_LABELS.get(
            implantacao.get("etapa_kanban"),
            implantacao.get("etapa_kanban") or "-",
        )
        implantacao["provisionamento_label"] = STATUS_PROVISIONAMENTO.get(
            implantacao.get("provisionamento_status"),
            implantacao.get("provisionamento_status") or "-",
        )
        implantacao["responsavel_exibicao"] = (
            implantacao.get("implantador_nome")
            or implantacao.get("responsavel")
            or "-"
        )
        return implantacao
