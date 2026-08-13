from datetime import datetime
from decimal import Decimal
from unicodedata import normalize


class RecebimentoMapper:
    STATUS_RECEBIDOS = {"RECEBIDO", "PAGO", "LIQUIDADO"}
    STATUS_SINCRONIZAVEIS = STATUS_RECEBIDOS | {"ATRASADO", "VENCIDO"}
    TERMOS_EXCLUIDOS = ("SETUP", "IMPLANTACAO")

    @classmethod
    def from_omie(cls, item, categorias_cache=None):
        categorias_cache = categorias_cache or {}
        recebimento = item.get("recebimento") or {}
        categoria_codigo = item.get("codigo_categoria") or cls._primeira_categoria(item)
        categoria_nome = categorias_cache.get(categoria_codigo)
        valor_documento = cls._decimal(item.get("valor_documento"))
        valor_recebido = cls._decimal(recebimento.get("valor")) or valor_documento
        categoria_excluida, motivo_exclusao = cls._categoria_excluida(categoria_nome or categoria_codigo)

        return {
            "codigo_externo": item.get("codigo_lancamento_omie"),
            "numero_documento": item.get("numero_documento"),
            "numero_documento_fiscal": item.get("numero_documento_fiscal"),
            "numero_parcela": item.get("numero_parcela"),
            "numero_contrato": item.get("cNumeroContrato"),
            "categoria_codigo": categoria_codigo,
            "categoria_nome": categoria_nome,
            "categoria_excluida": categoria_excluida,
            "motivo_exclusao": motivo_exclusao,
            "valor_original": valor_documento,
            "valor_recebido": valor_recebido,
            "valor_desconto": cls._decimal(recebimento.get("desconto")),
            "valor_juros": cls._decimal(recebimento.get("juros")),
            "data_vencimento": cls._data(item.get("data_vencimento")),
            "data_recebimento": cls._data(recebimento.get("data")) or cls._data(item.get("data_previsao")),
            "data_emissao": cls._data(item.get("data_emissao")),
            "situacao": item.get("status_titulo"),
            "codigo_cliente_omie": item.get("codigo_cliente_fornecedor"),
            "codigo_contrato_omie": None,
            "codigo_vendedor": item.get("codigo_vendedor") or None,
            "codigo_projeto": item.get("codigo_projeto") or None,
            "origem": "OMIE",
        }

    @staticmethod
    def recebido(item):
        return (item.get("status_titulo") or "").upper() in RecebimentoMapper.STATUS_RECEBIDOS

    @staticmethod
    def sincronizavel(item):
        return (item.get("status_titulo") or "").upper() in RecebimentoMapper.STATUS_SINCRONIZAVEIS

    @staticmethod
    def _primeira_categoria(item):
        categorias = item.get("categorias") or []
        if not categorias:
            return None
        return categorias[0].get("codigo_categoria")

    @staticmethod
    def _decimal(valor):
        if valor in (None, ""):
            return Decimal("0.00")
        return Decimal(str(valor))

    @staticmethod
    def _data(valor):
        if not valor:
            return None
        return datetime.strptime(valor, "%d/%m/%Y").date()

    @classmethod
    def _categoria_excluida(cls, valor):
        texto = cls._normalizar(valor or "")
        for termo in cls.TERMOS_EXCLUIDOS:
            if termo in texto:
                return True, "Categoria excluída da comissão."
        return False, None

    @staticmethod
    def _normalizar(valor):
        texto = normalize("NFKD", str(valor)).encode("ASCII", "ignore").decode("ASCII")
        return texto.upper()
