from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation

from app.repositories.regra_campanha_repository import RegraCampanhaRepository


class RegraCampanhaService:
    repository = RegraCampanhaRepository

    @classmethod
    def listar(cls, pesquisa=None, ativo="1", pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        regras = cls.repository.listar(pesquisa=pesquisa, ativo=ativo, limit=limit, offset=offset)
        total = cls.repository.total(pesquisa=pesquisa, ativo=ativo)
        return regras, total

    @classmethod
    def buscar_por_id(cls, regra_id):
        return cls.repository.buscar_por_id(regra_id)

    @classmethod
    def criar(cls, dados, usuario_email="sistema"):
        payload = cls._normalizar(dados)
        payload["created_by"] = usuario_email or "sistema"
        payload["updated_by"] = usuario_email or "sistema"
        cls._validar(payload)
        cls._validar_sobreposicao(payload)
        return cls.repository.inserir(payload)

    @classmethod
    def atualizar(cls, regra_id, dados, usuario_email="sistema"):
        if not cls.repository.buscar_por_id(regra_id):
            raise ValueError("Regra de campanha não encontrada.")
        payload = cls._normalizar(dados)
        payload["updated_by"] = usuario_email or "sistema"
        cls._validar(payload)
        cls._validar_sobreposicao(payload, ignorar_id=regra_id)
        cls.repository.atualizar(regra_id, payload)

    @classmethod
    def excluir(cls, regra_id, usuario_email="sistema"):
        if not cls.repository.buscar_por_id(regra_id):
            raise ValueError("Regra de campanha não encontrada.")
        cls.repository.excluir(regra_id, usuario_email)

    @classmethod
    def _validar_sobreposicao(cls, dados, ignorar_id=None):
        if not dados.get("ativo"):
            return
        conflito = cls.repository.buscar_sobreposicao(
            dados.get("vigencia_inicio"),
            dados.get("vigencia_fim"),
            ignorar_id=ignorar_id,
        )
        if conflito:
            inicio = conflito.get("vigencia_inicio")
            fim = conflito.get("vigencia_fim")
            raise ValueError(
                "Já existe uma regra ativa com vigência sobreposta: "
                f"{conflito.get('nome')} ({inicio:%d/%m/%Y} a {fim:%d/%m/%Y})."
            )

    @classmethod
    def _validar(cls, dados):
        if not dados.get("nome"):
            raise ValueError("Nome da campanha é obrigatório.")
        if len(dados["nome"]) > 150:
            raise ValueError("Nome da campanha deve possuir no máximo 150 caracteres.")
        cls._validar_percentual(dados, "percentual_parceiro", "Percentual do parceiro")
        cls._validar_percentual(dados, "percentual_executivo", "Percentual dos executivos")
        if not dados.get("vigencia_inicio") or not dados.get("vigencia_fim"):
            raise ValueError("Vigência inicial e final são obrigatórias.")
        if dados["vigencia_fim"] < dados["vigencia_inicio"]:
            raise ValueError("Vigência final não pode ser anterior à vigência inicial.")
        return True

    @classmethod
    def _normalizar(cls, dados):
        return {
            "nome": cls._texto(dados.get("nome")),
            "percentual_parceiro": cls._decimal(dados.get("percentual_parceiro")),
            "percentual_executivo": cls._decimal(dados.get("percentual_executivo")),
            "vigencia_inicio": cls._data(dados.get("vigencia_inicio")),
            "vigencia_fim": cls._data(dados.get("vigencia_fim")),
            "descricao": cls._texto(dados.get("descricao")),
            "ativo": str(dados.get("ativo", "1")) in ("1", "true", "True", "on"),
        }

    @classmethod
    def _validar_percentual(cls, dados, campo, rotulo):
        if dados.get(campo) is None:
            raise ValueError(f"{rotulo} é obrigatório.")
        if dados[campo] < Decimal("0") or dados[campo] > Decimal("100"):
            raise ValueError(f"{rotulo} deve ficar entre 0 e 100.")

    @staticmethod
    def _texto(valor):
        texto = (valor or "").strip()
        return texto or None

    @staticmethod
    def _data(valor):
        if not valor:
            return None
        if hasattr(valor, "year"):
            return valor
        try:
            return datetime.strptime(str(valor), "%Y-%m-%d").date()
        except ValueError as erro:
            raise ValueError("Informe datas de vigência válidas.") from erro

    @staticmethod
    def _decimal(valor):
        if valor in (None, ""):
            return None
        texto = str(valor).strip()
        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")
        try:
            return Decimal(texto)
        except (InvalidOperation, ValueError) as erro:
            raise ValueError("Informe percentuais de comissão válidos.") from erro
