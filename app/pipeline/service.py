from app.oportunidades.service import STATUS_OPORTUNIDADE
from app.repositories.oportunidade_repository import OportunidadeRepository
from app.repositories.proposta_repository import PropostaRepository


class PipelineService:

    repository = OportunidadeRepository

    @classmethod
    def carregar(cls, pesquisa=None):
        oportunidades = [cls._decorar_oportunidade(item) for item in cls.repository.listar_pipeline(pesquisa=pesquisa)]
        propostas = [cls._decorar_proposta(item) for item in PropostaRepository.listar_pipeline_sem_oportunidade(pesquisa=pesquisa)]
        itens_pipeline = oportunidades + propostas
        colunas = []

        for status, titulo in STATUS_OPORTUNIDADE.items():
            itens = [item for item in itens_pipeline if item.get("status_pipeline") == status]
            total_valor = sum((item.get("valor_pipeline") or 0) for item in itens)
            colunas.append(
                {
                    "status": status,
                    "titulo": titulo,
                    "itens": itens,
                    "quantidade": len(itens),
                    "valor_total": total_valor,
                }
            )

        resumo = {
            "total": len(itens_pipeline),
            "valor_total": sum((item.get("valor_pipeline") or 0) for item in itens_pipeline),
            "ganhas": len([item for item in itens_pipeline if item.get("status_pipeline") == "GANHA"]),
            "perdidas": len([item for item in itens_pipeline if item.get("status_pipeline") == "PERDIDA"]),
        }

        return colunas, resumo

    @staticmethod
    def _decorar_oportunidade(item):
        item = dict(item)
        item["tipo_pipeline"] = "OPORTUNIDADE"
        item["status_pipeline"] = item.get("status")
        item["valor_pipeline"] = item.get("valor_estimado") or 0
        probabilidade = item.get("probabilidade")
        if probabilidade is None:
            item["semaforo_fechamento"] = "FRIO"
        elif probabilidade >= 70:
            item["semaforo_fechamento"] = "QUENTE"
        elif probabilidade >= 35:
            item["semaforo_fechamento"] = "MORNO"
        else:
            item["semaforo_fechamento"] = "FRIO"
        return item

    @staticmethod
    def _decorar_proposta(item):
        item = dict(item)
        item["tipo_pipeline"] = "PROPOSTA"
        item["status_pipeline"] = {
            "RASCUNHO": "PROPOSTA",
            "EM_ANALISE": "NEGOCIACAO",
            "ENVIADA": "NEGOCIACAO",
            "APROVADA": "GANHA",
            "REJEITADA": "PERDIDA",
            "EXPIRADA": "PERDIDA",
        }.get(item.get("status"), "PROPOSTA")
        item["valor_pipeline"] = item.get("valor_total") or item.get("total_mensal") or 0
        item["empresa"] = item.get("cliente_nome")
        item["cliente_exibicao"] = item.get("cliente_nome")
        item["contato_nome"] = item.get("contato_nome")
        item["executivo_responsavel_nome"] = item.get("executivo_nome")
        item["probabilidade"] = None
        item["semaforo_fechamento"] = (item.get("semaforo_fechamento") or "FRIO").upper()
        return item
