from app.integracoes.omie.recebimento_mapper import RecebimentoMapper
from app.repositories.financeiro_recebimento_repository import FinanceiroRecebimentoRepository


class FinanceiroRecebimentoService:
    repository = FinanceiroRecebimentoRepository

    @classmethod
    def sincronizar_omie(cls, recebimento_omie, categorias_cache=None, data_de=None, data_ate=None):
        if not RecebimentoMapper.sincronizavel(recebimento_omie):
            return "IGNORADO"

        dados = RecebimentoMapper.from_omie(recebimento_omie, categorias_cache)
        data_recebimento = dados.get("data_recebimento")
        if data_de and data_recebimento and data_recebimento < data_de:
            return "IGNORADO"
        if data_ate and data_recebimento and data_recebimento > data_ate:
            return "IGNORADO"
        vinculos = cls.repository.buscar_vinculos(
            dados.get("codigo_cliente_omie"),
            dados.get("numero_contrato"),
        )
        if not cls._possui_nota_fiscal(dados):
            return "IGNORADO"

        if not dados.get("numero_contrato"):
            return "IGNORADO"

        if not vinculos:
            return "IGNORADO"

        dados.update(vinculos)
        if not dados.get("contrato_id") or not dados.get("cliente_id"):
            return "IGNORADO"

        return cls.repository.upsert(dados)

    @staticmethod
    def _possui_nota_fiscal(dados):
        return bool((dados.get("numero_documento_fiscal") or "").strip())
