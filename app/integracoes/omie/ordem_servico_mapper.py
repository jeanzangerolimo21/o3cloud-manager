from datetime import datetime
from decimal import Decimal, InvalidOperation


class OrdemServicoMapper:
    STATUS_LABELS = {
        "ABERTO": "Aberto",
        "CANCELADO": "Cancelado",
        "FATURADO": "Faturado",
        "NAO_ENCONTRADO": "Nao encontrado",
        "NAO_SINCRONIZADO": "Nao sincronizado",
    }

    STATUS_CLASSES = {
        "ABERTO": "warning",
        "CANCELADO": "danger",
        "FATURADO": "success",
        "NAO_ENCONTRADO": "secondary",
        "NAO_SINCRONIZADO": "light text-dark border",
    }

    @classmethod
    def from_omie(cls, item, status_resposta=None, total_encontradas=1):
        status_resposta = status_resposta or {}
        cabecalho = cls._grupo(item, "Cabecalho", "cabecalho")
        info = cls._grupo(item, "InfoCadastro", "infoCadastro", "info_cadastro")
        adicionais = cls._grupo(item, "InformacoesAdicionais", "informacoesAdicionais", "infAdic")
        observacoes = cls._grupo(item, "Observacoes", "observacoes")

        cancelada = cls._sim(status_resposta.get("cCancelada") or info.get("cCancelada"))
        faturada = cls._sim(status_resposta.get("cFaturada") or info.get("cFaturada"))
        if cancelada:
            status = "CANCELADO"
        elif faturada:
            status = "FATURADO"
        else:
            status = "ABERTO"

        valor = (
            cls._decimal(status_resposta.get("nValorTot"))
            or cls._decimal(cabecalho.get("nValorTotal"))
            or cls._total_servicos(item.get("ServicosPrestados") or item.get("servicosPrestados") or [])
        )
        descricao = cls._descricao(item)
        observacao = observacoes.get("cObsOS") or adicionais.get("cDadosAdicNF")
        if total_encontradas and total_encontradas > 1:
            observacao = (observacao + " | " if observacao else "") + f"Selecionada automaticamente entre {total_encontradas} OS do cliente."

        return {
            "setup_omie_status": status,
            "setup_omie_codigo_os": cabecalho.get("nCodOS") or status_resposta.get("nCodOS"),
            "setup_omie_numero_os": cabecalho.get("cNumOS") or status_resposta.get("cNumOS"),
            "setup_omie_valor_total": valor,
            "setup_omie_parcelas": cls._inteiro(cabecalho.get("nQtdeParc")),
            "setup_omie_etapa": cabecalho.get("cEtapa") or status_resposta.get("cEtapa"),
            "setup_omie_faturamento_status": cls._faturamento_status(status),
            "setup_omie_data_previsao": cls._data(cabecalho.get("dDtPrevisao")),
            "setup_omie_data_faturamento": cls._data(status_resposta.get("dDtFat") or info.get("dDtFat")),
            "setup_omie_data_cancelamento": cls._data(status_resposta.get("dDtCanc") or info.get("dDtCanc")),
            "setup_omie_descricao": descricao,
            "setup_omie_observacao": observacao,
            "valor_setup": valor if valor and valor > 0 else None,
        }

    @classmethod
    def nao_encontrado(cls, observacao):
        return {
            "setup_omie_status": "NAO_ENCONTRADO",
            "setup_omie_codigo_os": None,
            "setup_omie_numero_os": None,
            "setup_omie_valor_total": None,
            "setup_omie_parcelas": None,
            "setup_omie_etapa": None,
            "setup_omie_faturamento_status": "NAO_ENCONTRADO",
            "setup_omie_data_previsao": None,
            "setup_omie_data_faturamento": None,
            "setup_omie_data_cancelamento": None,
            "setup_omie_descricao": None,
            "setup_omie_observacao": observacao,
            "valor_setup": None,
        }

    @staticmethod
    def _grupo(item, *nomes):
        for nome in nomes:
            valor = item.get(nome)
            if isinstance(valor, dict):
                return valor
        return {}

    @staticmethod
    def _sim(valor):
        return str(valor or "").strip().upper() == "S"

    @staticmethod
    def _inteiro(valor):
        if valor in (None, ""):
            return None
        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _decimal(valor):
        if valor in (None, ""):
            return None
        try:
            return Decimal(str(valor)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError, TypeError):
            return None

    @classmethod
    def _total_servicos(cls, servicos):
        total = Decimal("0.00")
        for servico in servicos or []:
            quantidade = cls._decimal(servico.get("nQtde")) or Decimal("0.00")
            valor_unitario = cls._decimal(servico.get("nValUnit")) or Decimal("0.00")
            total += quantidade * valor_unitario
        return total.quantize(Decimal("0.01")) if total else None

    @staticmethod
    def _data(valor):
        if not valor:
            return None
        return datetime.strptime(valor, "%d/%m/%Y").date()

    @staticmethod
    def _faturamento_status(status):
        if status == "FATURADO":
            return "FATURADO"
        if status == "CANCELADO":
            return "CANCELADO"
        return "EM_ABERTO"

    @staticmethod
    def _descricao(item):
        partes = []
        for servico in item.get("ServicosPrestados") or item.get("servicosPrestados") or []:
            texto = servico.get("cDescServ") or servico.get("cDadosAdicItem")
            if texto:
                partes.append(str(texto).strip())
        return " | ".join(partes)[:500] if partes else None
