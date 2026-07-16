from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict
from typing import Optional


@dataclass(slots=True)
class RegistroImportado:

    tipo: str

    categoria: str

    descricao: str

    ativo: bool = field(default=True, kw_only=True)


@dataclass(slots=True)
class ProdutoImportado(RegistroImportado):

    produto: str

    nome_comercial: str = ""

    modelo: str = "STANDARD"

    faixa_inicio: Optional[int] = None

    faixa_fim: Optional[int] = None

    valor_mensal: Decimal = Decimal("0")

    valor_setup: Decimal = Decimal("0")

    quantidade_minima: int = 1

    tem_projeto: bool = False


@dataclass(slots=True)
class RecursoImportado(RegistroImportado):

    produto: str

    grupo: str = ""

    modelo: str = "PADRAO"

    unidade: Optional[str] = None

    valor_mensal: Decimal = Decimal("0")

    valor_setup: Decimal = Decimal("0")


@dataclass(slots=True)
class ResultadoImportacao:

    categorias: list = field(default_factory=list)

    produtos: list = field(default_factory=list)

    modelos: list = field(default_factory=list)

    faixas: list = field(default_factory=list)

    recursos: list = field(default_factory=list)

    precos: list = field(default_factory=list)

    erros: list = field(default_factory=list)

    avisos: list = field(default_factory=list)

    resumo: Dict = field(default_factory=dict)


class ImportacaoErro(Exception):
    """Erro durante o processo de importacao."""
    pass
