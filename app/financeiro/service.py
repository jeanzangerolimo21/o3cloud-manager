import base64
import csv
import io
import mimetypes
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape
from datetime import date
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.email import EmailService
from app.core.filters import date_br, moeda
from app.financeiro.repository import FinanceiroRepository
from app.repositories.contrato_adendo_repository import ContratoAdendoRepository


class FinanceiroService:

    STATUS_PREMIACAO_MANUAL = {
        "ABERTO": "Aberto",
        "LANCADO": "Lançado",
        "PAGO": "Pago",
    }


    STATUS_PAGAMENTO_CAMPANHAS = {
        "A_RECEBER": "A pagar (Lançado)",
        "ABERTO": "Aberto",
        "LANCADO": "Lançado",
        "PAGO": "Pago",
        "TODOS": "Todos",
    }

    @staticmethod
    def filtros_pagamento_campanhas(dados):
        incluir_adendos = dados.get("incluir_adendos", "1")
        if hasattr(dados, "getlist"):
            valores_adendos = dados.getlist("incluir_adendos")
            incluir_adendos = "1" if "1" in valores_adendos else (valores_adendos[0] if valores_adendos else "1")
        return {
            "q": FinanceiroService._texto(dados.get("q")),
            "campanha_id": FinanceiroService._inteiro(dados.get("campanha_id")),
            "parceiro_id": FinanceiroService._inteiro(dados.get("parceiro_id")),
            "executivo_id": FinanceiroService._inteiro(dados.get("executivo_id")),
            "data_de": FinanceiroService._texto(dados.get("data_de")),
            "data_ate": FinanceiroService._texto(dados.get("data_ate")),
            "status_manual": (FinanceiroService._texto(dados.get("status_manual")) or "A_RECEBER").upper(),
            "incluir_adendos": "0" if str(incluir_adendos) == "0" else "1",
        }

    @classmethod
    def contexto_pagamento_campanhas(cls, filtros=None):
        filtros = filtros or cls.filtros_pagamento_campanhas({})
        itens = FinanceiroRepository.listar_pagamento_campanhas_itens(filtros)
        grupos = cls._agrupar_pagamentos_campanhas(itens)
        return {
            "filtros": filtros,
            "campanhas": cls.listar_campanhas_comissao(),
            "parceiros": FinanceiroRepository.listar_parceiros_pagamento_campanhas(),
            "itens": itens,
            "grupos": grupos,
            "resumo": cls._resumo_pagamento_campanhas(grupos),
            "status_options": cls.STATUS_PAGAMENTO_CAMPANHAS,
            "corpo_email_padrao": cls.corpo_email_pagamento_campanha(),
        }

    @staticmethod
    def filtros_relatorio_geral_pagamento_campanhas(filtros=None):
        """Os relatórios do cabeçalho sempre consolidam todas as campanhas e parceiros."""
        filtros = dict(filtros or {})
        for chave in ("q", "campanha_id", "parceiro_id", "executivo_id"):
            filtros[chave] = None
        return filtros

    @classmethod
    def exportar_pagamento_campanhas_csv(cls, filtros=None):
        filtros = cls.filtros_relatorio_geral_pagamento_campanhas(filtros)
        itens = FinanceiroRepository.listar_pagamento_campanhas_itens(filtros)
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow([
            "campanha", "parceiro", "executivo", "origem", "contrato", "cliente",
            "data_recebimento_omie", "data_ativacao_contrato", "status_premiacao",
            "valor_base", "premiacao_parceiro", "premiacao_executivo", "premiacao_total",
        ])
        for item in itens:
            writer.writerow([
                item.get("campanha_nome") or "",
                item.get("parceiro_nome") or "",
                item.get("executivo_nome") or "",
                item.get("origem") or "",
                item.get("contrato_numero") or "",
                item.get("cliente_nome") or "",
                date_br(item.get("data_recebimento")) if item.get("data_recebimento") else "",
                date_br(item.get("data_ativacao")) if item.get("data_ativacao") else "",
                item.get("status_manual") or "",
                item.get("valor_base") or 0,
                item.get("valor_premiacao_parceiro") or 0,
                item.get("valor_premiacao_executivo") or 0,
                item.get("valor_total_premiacao") or 0,
            ])
        return buffer.getvalue()


    @classmethod
    def gerar_relatorio_pagamento_campanhas_pdf(cls, filtros=None):
        filtros = cls.filtros_relatorio_geral_pagamento_campanhas(filtros)
        itens = FinanceiroRepository.listar_pagamento_campanhas_itens(filtros)
        if not itens:
            raise ValueError("Nenhuma premiação encontrada para gerar o relatório.")
        return cls._pdf_pagamento_campanhas(itens, tipo="relatorio", filtros=filtros or {})

    @classmethod
    def gerar_recibo_pagamento_campanhas_pdf(cls, filtros=None, tipo="parceiro", parceiro_id=None, executivo_id=None):
        filtros = dict(filtros or {})
        if parceiro_id:
            filtros["parceiro_id"] = cls._inteiro(parceiro_id)
        if executivo_id:
            filtros["executivo_id"] = cls._inteiro(executivo_id)
        itens = FinanceiroRepository.listar_pagamento_campanhas_itens(filtros)
        if tipo == "executivo" and executivo_id:
            itens = [item for item in itens if cls._inteiro(item.get("executivo_id")) == cls._inteiro(executivo_id)]
        if not itens:
            raise ValueError("Nenhuma premiação encontrada para gerar o recibo.")
        return cls._pdf_pagamento_campanhas(itens, tipo=tipo, filtros=filtros)

    @classmethod
    def enviar_email_pagamento_campanha(cls, dados, usuario_email="sistema"):
        filtros = cls.filtros_pagamento_campanhas(dados)
        parceiro_id = cls._inteiro(dados.get("parceiro_id"))
        if not parceiro_id:
            raise ValueError("Selecione um parceiro para enviar o e-mail.")
        filtros["parceiro_id"] = parceiro_id
        itens = FinanceiroRepository.listar_pagamento_campanhas_itens(filtros)
        if not itens:
            raise ValueError("Nenhuma premiação encontrada para o parceiro e filtros informados.")
        grupo = cls._agrupar_pagamentos_campanhas(itens)[0]
        destinatarios = grupo.get("emails") or []
        if not destinatarios:
            raise ValueError("Parceiro sem e-mail cadastrado para envio.")
        assunto = cls._texto(dados.get("assunto")) or f"Pagamento de campanha - {grupo.get('campanha_nome') or 'O3 Cloud'}"
        corpo = cls._aplicar_variaveis_email_pagamento(cls._texto(dados.get("corpo")) or cls.corpo_email_pagamento_campanha(), grupo, filtros)
        anexos_temp = []
        try:
            anexos_temp.append(cls._arquivo_temporario_pdf(cls._pdf_pagamento_campanhas(itens, "parceiro", filtros), f"recibo-parceiro-{parceiro_id}.pdf"))
            for executivo in grupo.get("executivos") or []:
                if not executivo.get("executivo_id"):
                    continue
                exec_itens = [item for item in itens if item.get("executivo_id") == executivo.get("executivo_id")]
                if exec_itens:
                    anexos_temp.append(cls._arquivo_temporario_pdf(cls._pdf_pagamento_campanhas(exec_itens, "executivo", filtros), f"recibo-executivo-{executivo['executivo_id']}.pdf"))
            resultado = EmailService.enviar(
                assunto,
                corpo,
                destinatarios,
                corpo_html=cls._corpo_html_email_pagamento(corpo, grupo),
                finalidade="PAGAMENTO_CAMPANHAS",
                anexos=[{"caminho": str(caminho), "nome": nome, "mime_type": "application/pdf"} for caminho, nome in anexos_temp],
            )
        finally:
            for caminho, _nome in anexos_temp:
                try:
                    Path(caminho).unlink(missing_ok=True)
                except Exception:
                    pass
        if not resultado.get("enviado"):
            raise ValueError(f"E-mail não enviado: {resultado.get('motivo') or 'falha desconhecida'}")
        return {"destinatarios": resultado.get("destinatarios") or destinatarios, "anexos": len(anexos_temp)}

    @staticmethod
    def corpo_email_pagamento_campanha():
        return (
            "Olá, {parceiro}.\n\n"
            "Segue a relação de premiações lançadas para pagamento da campanha {campanha}, referente ao período {periodo}.\n"
            "Total previsto para pagamento: {total}.\n\n"
            "Os recibos do parceiro e dos executivos vinculados seguem em anexo para conferência.\n\n"
            "Atenciosamente,\nContas O3 Cloud"
        )

    @classmethod
    def _agrupar_pagamentos_campanhas(cls, itens):
        grupos = {}
        for item in itens or []:
            chave = (item.get("campanha_id") or 0, item.get("parceiro_id") or 0)
            grupo = grupos.setdefault(chave, {
                "campanha_id": item.get("campanha_id"),
                "campanha_nome": item.get("campanha_nome") or "Campanha não informada",
                "parceiro_id": item.get("parceiro_id"),
                "parceiro_nome": item.get("parceiro_nome") or "Sem parceiro",
                "emails": cls._emails_parceiro(item),
                "itens": [],
                "executivos_map": {},
                "total_base": Decimal("0.00"),
                "total_parceiro": Decimal("0.00"),
                "total_executivo": Decimal("0.00"),
                "total_premiacao": Decimal("0.00"),
            })
            grupo["itens"].append(item)
            grupo["total_base"] += cls._decimal_seguro(item.get("valor_base"))
            grupo["total_parceiro"] += cls._decimal_seguro(item.get("valor_premiacao_parceiro"))
            grupo["total_executivo"] += cls._decimal_seguro(item.get("valor_premiacao_executivo"))
            grupo["total_premiacao"] += cls._decimal_seguro(item.get("valor_total_premiacao"))
            exec_id = item.get("executivo_id") or 0
            exec_nome = item.get("executivo_nome") or "Sem executivo"
            executivo = grupo["executivos_map"].setdefault(exec_id, {
                "executivo_id": item.get("executivo_id"),
                "executivo_nome": exec_nome,
                "executivo_email": item.get("executivo_email"),
                "itens": 0,
                "total": Decimal("0.00"),
            })
            executivo["itens"] += 1
            executivo["total"] += cls._decimal_seguro(item.get("valor_premiacao_executivo"))
        resultado = []
        for grupo in grupos.values():
            grupo["executivos"] = sorted(grupo.pop("executivos_map").values(), key=lambda item: item["executivo_nome"])
            resultado.append(grupo)
        return sorted(resultado, key=lambda item: (-item["total_premiacao"], item["parceiro_nome"]))

    @classmethod
    def _resumo_pagamento_campanhas(cls, grupos):
        resumo = {
            "parceiros": len(grupos or []),
            "itens": 0,
            "executivos": 0,
            "total_base": Decimal("0.00"),
            "total_parceiro": Decimal("0.00"),
            "total_executivo": Decimal("0.00"),
            "total_premiacao": Decimal("0.00"),
        }
        executivos = set()
        for grupo in grupos or []:
            resumo["itens"] += len(grupo.get("itens") or [])
            resumo["total_base"] += grupo["total_base"]
            resumo["total_parceiro"] += grupo["total_parceiro"]
            resumo["total_executivo"] += grupo["total_executivo"]
            resumo["total_premiacao"] += grupo["total_premiacao"]
            for executivo in grupo.get("executivos") or []:
                if executivo.get("executivo_id"):
                    executivos.add(executivo["executivo_id"])
        resumo["executivos"] = len(executivos)
        return resumo

    @classmethod
    def _pdf_pagamento_campanhas(cls, itens, tipo="parceiro", filtros=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=28, leftMargin=28, topMargin=28, bottomMargin=28)
        styles = getSampleStyleSheet()
        titulo = {"parceiro": "Recibo de Pagamento de Campanha - Parceiro", "executivo": "Recibo de Pagamento de Campanha - Executivo"}.get(tipo, "Relatório de Pagamento de Campanhas")
        campanha = itens[0].get("campanha_nome") or "Campanha não informada"
        parceiro = itens[0].get("parceiro_nome") or "Sem parceiro"
        executivo = itens[0].get("executivo_nome") or "Sem executivo"
        total_parceiro = sum(cls._decimal_seguro(i.get("valor_premiacao_parceiro")) for i in itens)
        total_executivo = sum(cls._decimal_seguro(i.get("valor_premiacao_executivo")) for i in itens)
        total = total_executivo if tipo == "executivo" else total_parceiro + total_executivo
        elementos = [
            cls._logo_pdf("/opt/o3cloud-manager/app/static/img/logo.png", 125, 38) or Paragraph("O3 Cloud", styles["Title"]),
            Paragraph(titulo, styles["Heading2"]),
            Spacer(1, 8),
            Paragraph(f"Campanha: {cls._pdf_text(campanha)}" if tipo != "relatorio" else "Campanhas: todas", styles["Normal"]),
            Paragraph(f"Parceiro: {cls._pdf_text(parceiro)}" if tipo != "relatorio" else "Parceiros: todos", styles["Normal"]),
        ]
        logo_parceiro = cls._logo_parceiro_pdf(itens[0])
        if logo_parceiro:
            elementos.extend([Spacer(1, 5), logo_parceiro])
        if tipo == "executivo":
            elementos.append(Paragraph(f"Executivo: {cls._pdf_text(executivo)}", styles["Normal"]))
        elementos.extend([
            Paragraph(f"Período: {cls._periodo_label(filtros or {})}", styles["Normal"]),
            Paragraph(f"Total do recibo: {moeda(total)}", styles["Heading3"]),
            Spacer(1, 10),
        ])
        if tipo == "relatorio":
            parceiros = {}
            for item in itens:
                parceiros[item.get("parceiro_id") or item.get("parceiro_nome")] = item
            logos = []
            for item in sorted(parceiros.values(), key=lambda valor: valor.get("parceiro_nome") or ""):
                logo = cls._logo_parceiro_pdf(item)
                if logo:
                    logos.append([logo, Paragraph(cls._pdf_text(item.get("parceiro_nome") or "Parceiro"), styles["Normal"])])
            if logos:
                elementos.append(Paragraph("Parceiros", styles["Heading3"]))
                elementos.append(Table(logos, colWidths=[80, 390], hAlign="LEFT"))
                elementos.append(Spacer(1, 8))
        dados = [["Contrato", "Cliente", "Receb. Omie", "Ativação", "Base", "Parceiro", "Executivo"]]
        for item in itens:
            dados.append([
                item.get("contrato_numero") or "-",
                Paragraph(cls._pdf_text(item.get("cliente_nome") or "-"), styles["BodyText"]),
                date_br(item.get("data_recebimento")) if item.get("data_recebimento") else "-",
                date_br(item.get("data_ativacao")) if item.get("data_ativacao") else "-",
                moeda(item.get("valor_base") or 0),
                moeda(item.get("valor_premiacao_parceiro") or 0),
                moeda(item.get("valor_premiacao_executivo") or 0),
            ])
        dados.append(["", "", "", "Total", moeda(sum(cls._decimal_seguro(i.get("valor_base")) for i in itens)), moeda(total_parceiro), moeda(total_executivo)])
        tabela = Table(dados, colWidths=[58, 150, 68, 62, 65, 65, 65], repeatRows=1)
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
            ("ALIGN", (4, 1), (-1, -1), "RIGHT"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef2ff")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ]))
        elementos.append(tabela)
        elementos.append(Spacer(1, 18))
        elementos.append(Paragraph("Recibo gerado pelo O3Cloud Manager para conferência do Contas a Pagar.", styles["Italic"]))
        doc.build(elementos)
        return buffer.getvalue()

    @staticmethod
    def _logo_pdf(caminho, largura, altura):
        caminho = Path(caminho)
        if not caminho.is_file():
            return None
        return Image(str(caminho), width=largura, height=altura, kind="proportional")

    @classmethod
    def _logo_parceiro_pdf(cls, item):
        nome = item.get("parceiro_logo")
        if not nome:
            return None
        return cls._logo_pdf(Path("/opt/o3cloud-manager/storage/parceiros") / str(nome), 75, 32)

    @staticmethod
    def _logo_data_uri(caminho):
        caminho = Path(caminho)
        if not caminho.is_file():
            return ""
        mime = mimetypes.guess_type(caminho.name)[0] or "image/png"
        return f"data:{mime};base64,{base64.b64encode(caminho.read_bytes()).decode('ascii')}"

    @classmethod
    def _corpo_html_email_pagamento(cls, corpo, grupo):
        texto = escape(corpo or "").replace("\n", "<br>")
        logo_o3 = cls._logo_data_uri("/opt/o3cloud-manager/app/static/img/logo.png")
        logo_parceiro = ""
        if grupo.get("itens"):
            nome = grupo["itens"][0].get("parceiro_logo")
            if nome:
                logo_parceiro = cls._logo_data_uri(Path("/opt/o3cloud-manager/storage/parceiros") / str(nome))
        imagens = ""
        if logo_o3:
            imagens += f'<img src="{logo_o3}" alt="O3 Cloud" style="max-height:48px;max-width:150px;margin-right:24px;">'
        if logo_parceiro:
            imagens += f'<img src="{logo_parceiro}" alt="Parceiro" style="max-height:48px;max-width:150px;">'
        return f'<div style="font-family:Arial,sans-serif;color:#263238">{imagens}<hr style="border:0;border-top:1px solid #ddd;margin:16px 0"><p>{texto}</p></div>'

    @staticmethod
    def _pdf_text(valor):
        return escape(str(valor or "-"))

    @staticmethod
    def _arquivo_temporario_pdf(conteudo, nome):
        arquivo = tempfile.NamedTemporaryFile(prefix="o3-recibo-", suffix=".pdf", delete=False)
        try:
            arquivo.write(conteudo)
            arquivo.flush()
            return Path(arquivo.name), nome
        finally:
            arquivo.close()

    @staticmethod
    def _emails_parceiro(item):
        emails = []
        for campo in ("parceiro_email", "parceiro_contato_1_email", "parceiro_contato_2_email", "parceiro_contato_3_email"):
            email = (item.get(campo) or "").strip().lower()
            if email and "@" in email and email not in emails:
                emails.append(email)
        return emails

    @classmethod
    def _aplicar_variaveis_email_pagamento(cls, corpo, grupo, filtros):
        variaveis = {
            "parceiro": grupo.get("parceiro_nome") or "Parceiro",
            "campanha": grupo.get("campanha_nome") or "campanha selecionada",
            "periodo": cls._periodo_label(filtros),
            "total": moeda(grupo.get("total_premiacao") or 0),
            "total_parceiro": moeda(grupo.get("total_parceiro") or 0),
            "total_executivo": moeda(grupo.get("total_executivo") or 0),
        }

        class VariaveisEmail(dict):
            def __missing__(self, chave):
                return "{" + chave + "}"

        return (corpo or "").format_map(VariaveisEmail(variaveis))

    @staticmethod
    def _periodo_label(filtros):
        inicio = filtros.get("data_de")
        fim = filtros.get("data_ate")
        if inicio and fim:
            return f"{date_br(inicio)} a {date_br(fim)}"
        if inicio:
            return f"a partir de {date_br(inicio)}"
        if fim:
            return f"até {date_br(fim)}"
        return "sem filtro de data"

    @staticmethod
    def listar_faturamentos():

        return FinanceiroRepository.listar_faturamentos()

    @staticmethod
    def resumo_faturamentos():

        return FinanceiroRepository.resumo_faturamentos()

    @staticmethod
    def filtros_recebimentos(dados):

        return {
            "q": FinanceiroService._texto(dados.get("q_recebimento")),
            "data_de": FinanceiroService._texto(dados.get("recebimento_de")),
            "data_ate": FinanceiroService._texto(dados.get("recebimento_ate")),
            "categoria_excluida": FinanceiroService._texto(dados.get("categoria_excluida")),
            "situacao": FinanceiroService._texto(dados.get("situacao_recebimento")),
        }

    @staticmethod
    def listar_recebimentos_omie(filtros=None, pagina=1, limite=50):

        pagina = max(1, int(pagina or 1))
        offset = (pagina - 1) * limite
        return FinanceiroRepository.listar_recebimentos_omie(filtros, limite=limite, offset=offset)

    @staticmethod
    def resumo_recebimentos_omie(filtros=None):

        return FinanceiroRepository.resumo_recebimentos_omie(filtros)

    @staticmethod
    def situacoes_recebimentos_omie():

        return FinanceiroRepository.situacoes_recebimentos_omie()

    @staticmethod
    def filtros_comissoes(dados):

        return {
            "q": FinanceiroService._texto(dados.get("q")),
            "campanha_id": FinanceiroService._inteiro(dados.get("campanha_id")),
            "status_pagamento": FinanceiroService._texto(dados.get("status_pagamento")),
            "premiacao_liberada": FinanceiroService._texto(dados.get("premiacao_liberada")),
        }

    @staticmethod
    def listar_campanhas_comissao():

        return FinanceiroRepository.listar_campanhas_comissao()

    @staticmethod
    def buscar_campanha_comissao(campanha_id):

        return FinanceiroRepository.buscar_campanha_comissao(campanha_id)

    @staticmethod
    def listar_comissoes_contratos(filtros=None, pagina=1, limite=50):

        pagina = max(1, int(pagina or 1))
        offset = (pagina - 1) * limite
        return FinanceiroRepository.listar_comissoes_contratos(filtros, limite=limite, offset=offset)

    @staticmethod
    def resumo_comissoes_contratos(filtros=None):

        resumo = FinanceiroRepository.resumo_comissoes_contratos(filtros) or {}
        resumo_adendos = FinanceiroRepository.resumo_premiacoes_adendos(filtros) or {}
        valor_base_contratos = FinanceiroService._decimal_seguro(resumo.get("valor_base_comissao"))
        valor_premiacao_contratos = FinanceiroService._decimal_seguro(resumo.get("valor_comissao_prevista"))
        valor_base_adendos = FinanceiroService._decimal_seguro(resumo_adendos.get("valor_base"))
        valor_premiacao_adendos = FinanceiroService._decimal_seguro(resumo_adendos.get("valor_total"))
        resumo["contratos_total"] = resumo.get("total") or 0
        resumo["adendos_total"] = resumo_adendos.get("total") or 0
        resumo["total_itens_premiacao"] = resumo["contratos_total"] + resumo["adendos_total"]
        resumo["valor_base_comissao_contratos"] = valor_base_contratos
        resumo["valor_comissao_prevista_contratos"] = valor_premiacao_contratos
        resumo["valor_base_comissao_adendos"] = valor_base_adendos
        resumo["valor_comissao_prevista_adendos"] = valor_premiacao_adendos
        resumo["valor_base_comissao"] = valor_base_contratos + valor_base_adendos
        resumo["valor_comissao_prevista"] = valor_premiacao_contratos + valor_premiacao_adendos
        return resumo

    @staticmethod
    def buscar_comissao_contrato(contrato_id, campanha_id=None):

        return FinanceiroRepository.buscar_comissao_contrato(contrato_id, campanha_id)

    @staticmethod
    def campanhas_contrato(contrato_id):

        return FinanceiroRepository.listar_campanhas_contrato(contrato_id)

    @classmethod
    def calcular_comissao_manual(cls, contrato, dados):

        if not contrato:
            raise ValueError("Contrato ativo não encontrado para cálculo de premiação.")
        if not contrato.get("campanha_id"):
            raise ValueError("O contrato não possui campanha vinculada pela vigência. Selecione ou ajuste uma Regra de Campanha antes do cálculo.")

        valor_manual = cls._normalizar_decimal(dados.get("valor_manual_base"), permitir_vazio=True)
        base_contrato = cls._decimal_seguro(contrato.get("valor_base_comissao"))
        base_calculo = valor_manual if valor_manual > 0 else base_contrato
        percentual_parceiro = cls._decimal_seguro(contrato.get("percentual_parceiro_aplicado"))
        percentual_executivo = cls._decimal_seguro(contrato.get("percentual_executivo_aplicado"))
        valor_premiacao_parceiro = (base_calculo * percentual_parceiro / Decimal("100")).quantize(Decimal("0.01"))
        valor_premiacao_executivo = (base_calculo * percentual_executivo / Decimal("100")).quantize(Decimal("0.01"))
        valor_comissao = valor_premiacao_parceiro + valor_premiacao_executivo

        return {
            "valor_manual_base": valor_manual,
            "valor_base_contrato": base_contrato,
            "valor_base_calculo": base_calculo,
            "percentual_parceiro": percentual_parceiro,
            "percentual_executivo": percentual_executivo,
            "valor_premiacao_parceiro": valor_premiacao_parceiro,
            "valor_premiacao_executivo": valor_premiacao_executivo,
            "valor_comissao": valor_comissao,
            "usou_valor_manual": valor_manual > 0,
        }

    @staticmethod
    def status_comissoes():

        return {
            "RECEBIDO": "Recebido",
            "ATRASADO": "Atrasado",
            "NAO_LOCALIZADO": "Nao localizado",
        }

    @classmethod
    def status_premiacao_manual_options(cls):

        return cls.STATUS_PREMIACAO_MANUAL

    @classmethod
    def atualizar_status_premiacao_manual(cls, contrato_id, campanha_id, status_manual, usuario_email="sistema"):

        contrato_id = cls._inteiro(contrato_id)
        campanha_id = cls._inteiro(campanha_id)
        status_manual = cls._texto(status_manual).upper()
        if not contrato_id or not campanha_id:
            raise ValueError("Contrato e campanha são obrigatórios para atualizar a premiação.")
        if status_manual not in cls.STATUS_PREMIACAO_MANUAL:
            raise ValueError("Status de premiação inválido.")
        contrato = cls.buscar_comissao_contrato(contrato_id, campanha_id)
        if not contrato or not contrato.get("premiacao_liberada"):
            raise ValueError("Premiação não encontrada para o contrato informado.")
        if contrato.get("status_pagamento") != "RECEBIDO":
            raise ValueError("A checagem manual só fica disponível após o recebimento pelo sistema.")
        FinanceiroRepository.salvar_status_premiacao_manual(contrato_id, campanha_id, status_manual, usuario_email)
        return {
            "status": status_manual,
            "label": cls.STATUS_PREMIACAO_MANUAL[status_manual],
        }

    @staticmethod
    def listar_premiacoes_adendos(filtros=None):

        return FinanceiroRepository.listar_premiacoes_adendos(filtros)

    @staticmethod
    def resumo_premiacoes_adendos(filtros=None):

        return FinanceiroRepository.resumo_premiacoes_adendos(filtros)

    @staticmethod
    def regularizar_premiacoes_adendos_vinculo_manual(usuario_email="sistema", adendo_id=None):

        return FinanceiroRepository.atualizar_premiacoes_adendos_sem_executivo_por_vinculo_manual(usuario_email, adendo_id)

    @classmethod
    def lancar_premiacao_adendo(cls, dados, usuario_email="sistema"):

        adendo_id = cls._inteiro(dados.get("adendo_id"))
        adendo = ContratoAdendoRepository.buscar_por_id(adendo_id)
        if not adendo:
            raise ValueError("Adendo contratual nao encontrado.")
        cls.regularizar_premiacoes_adendos_vinculo_manual(usuario_email, adendo_id)
        if FinanceiroRepository.buscar_premiacao_adendo(adendo_id):
            raise ValueError("Este adendo ja possui premiacao manual lancada.")

        campanha_id = cls._inteiro(dados.get("campanha_id"))
        campanha = cls.buscar_campanha_comissao(campanha_id)
        if not campanha:
            raise ValueError("Selecione uma campanha valida para calcular a premiacao do adendo.")
        contrato = FinanceiroRepository.buscar_base_premiacao_contrato(adendo["contrato_id"])
        if not contrato or not contrato.get("premiacao_liberada"):
            raise ValueError("Contrato sem parceiro ou executivo habilitado para premiacao.")

        valor_base = cls._normalizar_decimal(dados.get("valor_base"))
        if valor_base <= 0:
            raise ValueError("Valor base da premiacao deve ser maior que zero.")

        parceiro_id = contrato.get("parceiro_premiacao_id")
        executivo_id = contrato.get("executivo_premiacao_id")
        percentual_parceiro = cls._decimal_seguro(campanha.get("percentual_parceiro")) if parceiro_id else Decimal("0.00")
        percentual_executivo = cls._decimal_seguro(campanha.get("percentual_executivo")) if executivo_id else Decimal("0.00")
        valor_premiacao_parceiro = (valor_base * percentual_parceiro / Decimal("100")).quantize(Decimal("0.01"))
        valor_premiacao_executivo = (valor_base * percentual_executivo / Decimal("100")).quantize(Decimal("0.01"))

        status_manual = cls._texto(dados.get("status_manual") or "LANCADO").upper()
        if status_manual not in cls.STATUS_PREMIACAO_MANUAL:
            raise ValueError("Status de premiacao invalido.")

        descricao = cls._texto(dados.get("descricao")) or f"Premiacao manual do adendo {adendo.get('titulo')}"
        payload = {
            "adendo_id": adendo_id,
            "contrato_id": adendo["contrato_id"],
            "cliente_id": adendo["cliente_id"],
            "campanha_id": campanha["id"],
            "parceiro_id": parceiro_id,
            "executivo_id": executivo_id,
            "descricao": descricao[:255],
            "data_lancamento": cls._texto(dados.get("data_lancamento")) or date.today().isoformat(),
            "valor_base": valor_base,
            "percentual_parceiro": percentual_parceiro,
            "percentual_executivo": percentual_executivo,
            "valor_premiacao_parceiro": valor_premiacao_parceiro,
            "valor_premiacao_executivo": valor_premiacao_executivo,
            "valor_total": valor_premiacao_parceiro + valor_premiacao_executivo,
            "status_manual": status_manual,
            "observacoes": cls._texto(dados.get("observacoes")) or None,
            "created_by": usuario_email,
            "updated_by": usuario_email,
        }
        return FinanceiroRepository.inserir_premiacao_adendo(payload)

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
    def filtros_receitas_servidor(dados):

        return {
            "q": FinanceiroService._texto(dados.get("q")),
            "node": FinanceiroService._texto(dados.get("node")),
        }

    @staticmethod
    def receitas_por_servidor(filtros=None):

        return FinanceiroRepository.receitas_por_servidor(filtros)

    @staticmethod
    def produtos_clientes(filtros=None):

        return FinanceiroRepository.produtos_clientes(filtros)

    @staticmethod
    def contexto_dashboard():

        return {
            "parceiros": FinanceiroRepository.listar_parceiros_dashboard(),
            "executivos": FinanceiroRepository.listar_executivos_dashboard(),
            "checklist_beta": FinanceiroService.checklist_beta(),
        }

    @staticmethod
    def checklist_beta():

        return [
            {
                "area": "Comercial",
                "classe": "primary",
                "itens": [
                    "Confirmar CNPJ, email, telefone e localizacao dos clientes ativos.",
                    "Vincular propostas ao cadastro oficial do cliente quando aplicavel.",
                    "Revisar contato e executivo responsavel nas propostas em negociacao.",
                ],
            },
            {
                "area": "Operacoes",
                "classe": "success",
                "itens": [
                    "Conferir implantador, responsavel e prazo das implantacoes abertas.",
                    "Separar contratos diretos de contratos originados por proposta.",
                    "Validar contratos encaminhados para projeto antes da fila de implantacao.",
                ],
            },
            {
                "area": "Financeiro",
                "classe": "warning",
                "itens": [
                    "Manter faturamentos reais pendentes ate carga oficial da Beta.",
                    "Preencher custos homologados de produtos antes de margem definitiva.",
                    "Validar parametros financeiros somente com fonte aprovada.",
                ],
            },
            {
                "area": "Engenharia",
                "classe": "secondary",
                "itens": [
                    "Continuar integracoes em leitura e diagnostico.",
                    "Registrar lacunas tecnicas sem executar automacoes destrutivas.",
                    "Preservar segredos mascarados por padrao.",
                ],
            },
        ]

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
    def _decimal_seguro(valor):

        try:
            return Decimal(str(valor or "0")).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return Decimal("0.00")

    @staticmethod
    def _limpar_params(params):

        return {chave: valor for chave, valor in params.items() if valor not in (None, "")}

