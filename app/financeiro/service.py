import csv
import io
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation

from app.financeiro.repository import FinanceiroRepository


class FinanceiroService:

    @staticmethod
    def listar_faturamentos():

        return FinanceiroRepository.listar_faturamentos()

    @staticmethod
    def resumo_faturamentos():

        return FinanceiroRepository.resumo_faturamentos()

    @staticmethod
    def contratos_para_faturamento():

        return FinanceiroRepository.contratos_para_faturamento()

    @classmethod
    def linhas_modelo_faturamentos(cls):

        linhas = []
        for contrato in cls.contratos_para_faturamento():
            linhas.append([
                contrato.get("id"),
                contrato.get("numero"),
                contrato.get("codigo_externo") or "",
                contrato.get("cliente_nome"),
                "",
                contrato.get("valor_mensal") or "",
                "0",
                "",
                "",
                "MANUAL",
                "",
            ])
        return linhas

    @classmethod
    def importar_faturamentos_csv(cls, arquivo):

        if not arquivo or not arquivo.filename:
            raise ValueError("Selecione um arquivo CSV para importar.")

        conteudo = arquivo.read().decode("utf-8-sig", errors="replace")
        if not conteudo.strip():
            raise ValueError("Arquivo CSV vazio.")

        linhas = cls._ler_csv(conteudo)
        if not linhas:
            raise ValueError("Nenhuma linha encontrada no CSV.")

        resumo = {"processadas": 0, "atualizadas": 0, "ignoradas": 0, "erros": []}

        for numero, linha in enumerate(linhas, start=2):
            try:
                normalizada = {cls._normalizar_header(chave): valor for chave, valor in linha.items()}
                contrato_ref = cls._valor(
                    normalizada,
                    "contrato_id",
                    "contrato_numero",
                    "numero",
                    "codigo_externo",
                    "contrato_codigo_externo",
                ).strip()
                competencia_raw = cls._valor(normalizada, "competencia", "mes")
                valor_bruto_raw = cls._valor(normalizada, "valor_bruto", "bruto", "valor")

                if not contrato_ref and not str(competencia_raw or "").strip() and not str(valor_bruto_raw or "").strip():
                    resumo["ignoradas"] += 1
                    continue
                if not contrato_ref:
                    raise ValueError("Contrato e obrigatorio.")

                contrato = FinanceiroRepository.buscar_contrato_faturamento(contrato_ref)
                if not contrato:
                    raise ValueError("Contrato ativo nao encontrado.")

                competencia = cls._normalizar_competencia(competencia_raw)
                valor_bruto = cls._normalizar_decimal(valor_bruto_raw)
                percentual_comissao = cls._normalizar_decimal(
                    cls._valor(normalizada, "percentual_comissao", "comissao_percentual"),
                    permitir_vazio=True,
                )
                valor_comissao_raw = cls._valor(normalizada, "valor_comissao", "comissao")
                valor_liquido_raw = cls._valor(normalizada, "valor_liquido", "liquido")

                if valor_bruto <= 0:
                    raise ValueError("Valor bruto deve ser maior que zero.")

                valor_comissao = cls._normalizar_decimal(valor_comissao_raw, permitir_vazio=True)
                if valor_comissao == 0 and percentual_comissao > 0:
                    valor_comissao = (valor_bruto * percentual_comissao / Decimal("100")).quantize(Decimal("0.01"))

                valor_liquido = cls._normalizar_decimal(valor_liquido_raw, permitir_vazio=True)
                if valor_liquido == 0:
                    valor_liquido = valor_bruto - valor_comissao
                if valor_liquido <= 0:
                    raise ValueError("Valor liquido deve ser maior que zero.")

                origem = cls._valor(normalizada, "origem").strip().upper() or "MANUAL"
                if origem not in ("OMIE", "MANUAL"):
                    raise ValueError("Origem deve ser OMIE ou MANUAL.")

                FinanceiroRepository.salvar_faturamento({
                    "contrato_id": contrato["id"],
                    "competencia": competencia,
                    "origem": origem,
                    "valor_bruto": valor_bruto,
                    "percentual_comissao": percentual_comissao,
                    "valor_comissao": valor_comissao,
                    "valor_liquido": valor_liquido,
                    "observacoes": cls._valor(normalizada, "observacoes", "observacao") or None,
                })
                resumo["atualizadas"] += 1
                resumo["processadas"] += 1
            except Exception as erro:
                resumo["erros"].append(f"Linha {numero}: {erro}")

        return resumo

    @staticmethod
    def dashboard(filtros=None):

        return FinanceiroRepository.dashboard_executivo(filtros)

    @staticmethod
    def filtros_dashboard(dados):

        return {
            "data_de": FinanceiroService._texto(dados.get("data_de")),
            "data_ate": FinanceiroService._texto(dados.get("data_ate")),
            "parceiro_id": FinanceiroService._inteiro(dados.get("parceiro_id")),
            "executivo_id": FinanceiroService._inteiro(dados.get("executivo_id")),
            "status_comercial": FinanceiroService._texto(dados.get("status_comercial")),
            "status_contrato": FinanceiroService._texto(dados.get("status_contrato")),
            "status_implantacao": FinanceiroService._texto(dados.get("status_implantacao")),
        }


    @staticmethod
    def filtros_produtos_clientes(dados):

        return {
            "q": FinanceiroService._texto(dados.get("q")),
            "status": FinanceiroService._texto(dados.get("status")),
            "origem": FinanceiroService._texto(dados.get("origem")),
            "situacao": FinanceiroService._texto(dados.get("situacao")),
        }

    @staticmethod
    def produtos_clientes(filtros=None):

        return FinanceiroRepository.produtos_clientes(filtros)

    @staticmethod
    def contexto_dashboard():

        return {
            "parceiros": FinanceiroRepository.listar_parceiros_dashboard(),
            "executivos": FinanceiroRepository.listar_executivos_dashboard(),
        }

    @staticmethod
    def links_dashboard(filtros):
        filtros = filtros or {}

        contratos_base = FinanceiroService._limpar_params({
            "status": filtros.get("status_contrato"),
            "data_de": filtros.get("data_de"),
            "data_ate": filtros.get("data_ate"),
        })
        implantacoes_base = FinanceiroService._limpar_params({
            "status": filtros.get("status_implantacao"),
        })
        propostas_base = FinanceiroService._limpar_params({
            "status": filtros.get("status_comercial"),
        })

        return {
            "propostas_index": propostas_base,
            "propostas_assinatura": FinanceiroService._limpar_params({
                **propostas_base,
                "clicksign_status": "AGUARDANDO_ASSINATURAS",
            }),
            "contratos_dashboard": contratos_base,
            "contratos_index": contratos_base,
            "contratos_ativos": FinanceiroService._limpar_params({
                **contratos_base,
                "status": "ATIVO",
            }),
            "contratos_a_iniciar": FinanceiroService._limpar_params({
                **contratos_base,
                "status": filtros.get("status_contrato") or "ENCAMINHADO_PROJETO",
            }),
            "implantacoes_index": implantacoes_base,
            "implantacoes_atrasadas": FinanceiroService._limpar_params({
                **implantacoes_base,
                "prazo": "atrasadas",
            }),
            "implantacoes_vence_7": FinanceiroService._limpar_params({
                **implantacoes_base,
                "prazo": "vence_7",
            }),
        }


    @staticmethod
    def listar_clientes():

        return FinanceiroRepository.listar_clientes()

    @staticmethod
    def buscar_cliente(cliente_id):

        return FinanceiroRepository.buscar_cliente(cliente_id)
    @staticmethod
    def _ler_csv(conteudo):

        amostra = conteudo[:2048]
        try:
            dialect = csv.Sniffer().sniff(amostra, delimiters=";,\t,")
        except csv.Error:
            dialect = csv.excel
            dialect.delimiter = ";"

        return list(csv.DictReader(io.StringIO(conteudo), dialect=dialect))

    @staticmethod
    def _normalizar_header(valor):

        return (valor or "").strip().lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def _valor(dados, *chaves):

        for chave in chaves:
            valor = dados.get(chave)
            if valor not in (None, ""):
                return str(valor).strip()
        return ""

    @staticmethod
    def _normalizar_decimal(valor, permitir_vazio=False):

        texto = str(valor or "").strip()
        if not texto and permitir_vazio:
            return Decimal("0")
        texto = texto.replace("R$", "").replace(" ", "")
        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")
        try:
            return Decimal(texto).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            raise ValueError(f"Valor decimal invalido: {valor}")

    @staticmethod
    def _normalizar_competencia(valor):

        texto = str(valor or "").strip()
        for formato in ("%Y-%m-%d", "%Y-%m", "%m/%Y", "%d/%m/%Y"):
            try:
                data = datetime.strptime(texto, formato)
                return data.replace(day=1).date()
            except ValueError:
                pass
        raise ValueError("Competencia invalida. Use AAAA-MM, AAAA-MM-DD, MM/AAAA ou DD/MM/AAAA.")

    @staticmethod
    def _texto(valor):

        return (valor or "").strip() or None

    @staticmethod
    def _inteiro(valor):

        try:
            return int(valor or 0) or None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _limpar_params(params):

        return {chave: valor for chave, valor in params.items() if valor not in (None, "")}

