from app.oportunidades.service import STATUS_OPORTUNIDADE
from app.repositories.oportunidade_repository import OportunidadeRepository


class PipelineService:

    repository = OportunidadeRepository

    @classmethod
    def carregar(cls, pesquisa=None):
        oportunidades = cls.repository.listar_pipeline(pesquisa=pesquisa)
        colunas = []

        for status, titulo in STATUS_OPORTUNIDADE.items():
            itens = [item for item in oportunidades if item.get("status") == status]
            total_valor = sum((item.get("valor_estimado") or 0) for item in itens)
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
            "total": len(oportunidades),
            "valor_total": sum((item.get("valor_estimado") or 0) for item in oportunidades),
            "ganhas": len([item for item in oportunidades if item.get("status") == "GANHA"]),
            "perdidas": len([item for item in oportunidades if item.get("status") == "PERDIDA"]),
        }

        return colunas, resumo
