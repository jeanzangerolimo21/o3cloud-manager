import json
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from app.core.email import EmailService
from app.core.storage import StorageService
from app.repositories.sucesso_cliente_repository import SucessoClienteRepository


STATUS_RELACIONAMENTO = {
    "OTIMO": "Otimo",
    "BOM": "Bom",
    "REGULAR": "Regular",
    "CRITICO": "Critico",
}

PERGUNTAS_PADRAO_IMPLANTACAO = [
    "Como você avalia o atendimento e a disponibilidade do técnico durante o processo de implantação?",
    "Como você avalia o conhecimento técnico e a capacidade do profissional em orientar e solucionar as necessidades durante a implantação?",
    "De forma geral, qual é o seu nível de satisfação com o processo de implantação realizado pela nossa equipe técnica?",
]


class SucessoClienteService:
    repository = SucessoClienteRepository

    @classmethod
    def listar(cls, pesquisa=None, curva=None, status_relacionamento=None, pagina=1):
        limit = 50
        offset = (pagina - 1) * limit
        contratos = cls.repository.listar_contratos(pesquisa, curva, status_relacionamento, limit, offset)
        total = cls.repository.total_contratos(pesquisa, curva, status_relacionamento)
        return [cls._decorar_contrato(item) for item in contratos], total

    @classmethod
    def dashboard(cls):
        return cls.repository.dashboard() or {}

    @classmethod
    def dashboard_pesquisas(cls):
        dados = cls.repository.dashboard_pesquisas() or {}
        dados["media_geral"] = cls._decimal(dados.get("media_geral"))
        dados["recentes"] = [cls._decorar_pesquisa(item) for item in cls.repository.listar_pesquisas_recentes()]
        dados["lotes_recentes"] = [cls._decorar_lote_pesquisa(item) for item in cls.repository.listar_lotes_pesquisas_recentes()]
        return dados

    @classmethod
    def detalhe(cls, contrato_id):
        contrato = cls.repository.buscar_contrato(contrato_id)
        if not contrato:
            return None
        contrato = cls._decorar_contrato(contrato)
        contrato["historico"] = cls._historico_com_anexos(contrato_id)
        contrato["pesquisas_implantacao"] = [
            cls._decorar_pesquisa(item) for item in cls.repository.listar_pesquisas_contrato(contrato_id)
        ]
        relacionamento = cls.repository.buscar_relacionamento(contrato_id) or {}
        contrato["relacionamento"] = relacionamento
        contrato["contatos_cliente"] = cls.repository.listar_contatos_cliente([
            contrato.get("cliente_nome_fantasia"),
            contrato.get("cliente_razao_social"),
        ])
        if relacionamento.get("contato_id") and all(str(c.get("id")) != str(relacionamento.get("contato_id")) for c in contrato["contatos_cliente"]):
            contrato["contatos_cliente"].append({
                "id": relacionamento.get("contato_id"),
                "nome": relacionamento.get("contato_nome"),
                "email": relacionamento.get("contato_email"),
                "telefone": relacionamento.get("contato_telefone"),
                "whatsapp": relacionamento.get("contato_whatsapp"),
            })
        return contrato

    @classmethod
    def nova_pesquisa_payload(cls, contrato_id, dados=None):
        contrato = cls.detalhe(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        payload = cls._normalizar_pesquisa(dados or {})
        if not payload["destinatario_emails"] and contrato.get("contato_email"):
            payload["destinatario_emails"] = contrato.get("contato_email")
        return contrato, payload

    @classmethod
    def preview_pesquisa(cls, contrato_id, dados):
        contrato = cls.repository.buscar_contrato(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        return cls._decorar_contrato(contrato), cls._normalizar_pesquisa(dados, validar=True)

    @classmethod
    def enviar_pesquisa(cls, contrato_id, dados, link_resposta, usuario_email=None):
        contrato = cls.repository.buscar_contrato(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        contrato = cls._decorar_contrato(contrato)
        payload = cls._normalizar_pesquisa(dados, validar=True)
        lote_uuid = str(uuid4())
        pesquisas = []
        resultados = []
        links = []
        for destinatario in payload["destinatarios"]:
            pesquisa_id = cls.repository.inserir_pesquisa({
                "token": str(uuid4()),
                "lote_uuid": lote_uuid,
                "contrato_id": contrato_id,
                "cliente_id": contrato.get("cliente_id"),
                "titulo": payload["titulo"],
                "referencia_data": payload["referencia_data"],
                "destinatario_email": destinatario,
                "perguntas_json": json.dumps(payload["perguntas"], ensure_ascii=False),
                "status": "ENVIADA",
                "created_by": usuario_email,
            })
            pesquisa = cls.repository.buscar_pesquisa_por_id(pesquisa_id)
            link = link_resposta(pesquisa["token"])
            resultado = cls._enviar_email_pesquisa(contrato, destinatario, link, payload)
            cls.repository.atualizar_envio_pesquisa(
                pesquisa_id,
                resultado.get("enviado"),
                cls._resumo_resultado_email(resultado, link),
            )
            pesquisas.append(cls.repository.buscar_pesquisa_por_id(pesquisa_id))
            resultados.append(resultado)
            links.append(link)
        return pesquisas, resultados, links

    @classmethod
    def buscar_pesquisa_interna(cls, pesquisa_id):
        pesquisa = cls.repository.buscar_pesquisa_por_id(pesquisa_id)
        if not pesquisa:
            return None
        return cls._decorar_pesquisa(pesquisa)

    @classmethod
    def buscar_pesquisa_publica(cls, token):
        pesquisa = cls.repository.buscar_pesquisa_por_token(token)
        if not pesquisa:
            return None
        return cls._decorar_pesquisa(pesquisa)

    @classmethod
    def registrar_resposta_pesquisa(cls, token, dados, remote_addr=None, user_agent=None):
        pesquisa = cls.repository.buscar_pesquisa_por_token(token)
        if not pesquisa:
            raise ValueError("Pesquisa não encontrada.")
        if pesquisa.get("status") == "RESPONDIDA":
            raise ValueError("Esta pesquisa já foi respondida.")
        perguntas = cls._json_lista(pesquisa.get("perguntas_json"))
        respostas = []
        notas = []
        for idx, pergunta in enumerate(perguntas):
            nota = cls._inteiro(dados.get(f"nota_{idx}"))
            if nota is None or nota < 0 or nota > 10:
                raise ValueError("Todas as perguntas devem receber uma nota de 0 a 10.")
            notas.append(nota)
            respostas.append({"pergunta": pergunta, "nota": nota})
        media = round(sum(notas) / len(notas), 2) if notas else 0
        classificacao = cls._classificacao_nota(media)
        registro = {
            "pesquisa_id": pesquisa.get("id"),
            "token": pesquisa.get("token"),
            "contrato_id": pesquisa.get("contrato_id"),
            "cliente_id": pesquisa.get("cliente_id"),
            "cliente": pesquisa.get("cliente_nome_fantasia") or pesquisa.get("cliente_razao_social"),
            "resposta_nome": (dados.get("resposta_nome") or "").strip(),
            "resposta_email": (dados.get("resposta_email") or "").strip().lower(),
            "respostas": respostas,
            "comentario_texto": (dados.get("comentario_texto") or "").strip(),
            "media_nota": media,
            "classificacao_nota": classificacao,
            "respondido_em": datetime.now().isoformat(timespec="seconds"),
            "ip_origem": remote_addr,
            "user_agent": user_agent,
        }
        arquivo = cls._salvar_resposta_em_disco(pesquisa, registro)
        cls.repository.registrar_resposta_pesquisa(pesquisa["id"], {
            "resposta_nome": registro["resposta_nome"] or None,
            "resposta_email": registro["resposta_email"] or None,
            "respostas_json": json.dumps(respostas, ensure_ascii=False),
            "comentario_texto": registro["comentario_texto"] or None,
            "media_nota": media,
            "classificacao_nota": classificacao,
            "arquivo_resposta": arquivo,
        })
        return registro

    @classmethod
    def registrar_relacionamento(cls, contrato_id, dados, arquivos=None, usuario_email=None):
        contrato = cls.repository.buscar_contrato(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        status = (dados.get("status_relacionamento") or "").strip().upper()
        if status not in STATUS_RELACIONAMENTO:
            raise ValueError("Status de relacionamento inválido.")
        comentario = (dados.get("comentario") or "").strip()
        if not comentario:
            raise ValueError("Comentário é obrigatório.")
        contato_id = cls._inteiro(dados.get("contato_id"))
        arquivos = [arquivo for arquivo in (arquivos or []) if arquivo and arquivo.filename]
        for arquivo in arquivos:
            StorageService.validar(arquivo)
        cls.repository.salvar_relacionamento(contrato_id, contato_id, status, usuario_email)
        historico_id = cls.repository.inserir_historico({
            "contrato_id": contrato_id,
            "contato_id": contato_id,
            "status_relacionamento": status,
            "comentario": comentario,
            "autor_email": usuario_email,
        })
        cls._salvar_anexos(contrato_id, historico_id, arquivos)
        return historico_id

    @classmethod
    def vincular_contato(cls, contrato_id, contato_id, usuario_email=None):
        contrato = cls.repository.buscar_contrato(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        atual = cls.repository.buscar_relacionamento(contrato_id) or {}
        status = atual.get("status_relacionamento") or "BOM"
        cls.repository.salvar_relacionamento(contrato_id, cls._inteiro(contato_id), status, usuario_email)

    @classmethod
    def marcar_critico(cls, contrato_id, usuario_email=None):
        contrato = cls.repository.buscar_contrato(contrato_id)
        if not contrato:
            raise ValueError("Contrato não encontrado.")
        atual = cls.repository.buscar_relacionamento(contrato_id) or {}
        contato_id = cls._inteiro(atual.get("contato_id"))
        cls.repository.salvar_relacionamento(contrato_id, contato_id, "CRITICO", usuario_email)
        return cls.repository.inserir_historico({
            "contrato_id": contrato_id,
            "contato_id": contato_id,
            "status_relacionamento": "CRITICO",
            "comentario": "Marcado como crítico pela tela principal de Sucesso do Cliente.",
            "autor_email": usuario_email,
        })

    @classmethod
    def _historico_com_anexos(cls, contrato_id):
        historico = cls.repository.listar_historico(contrato_id)
        anexos = cls.repository.listar_anexos(contrato_id)
        por_historico = {}
        for anexo in anexos:
            por_historico.setdefault(anexo.get("historico_id"), []).append(anexo)
        for item in historico:
            item["anexos"] = por_historico.get(item.get("id"), [])
        return historico

    @classmethod
    def _salvar_anexos(cls, contrato_id, historico_id, arquivos):
        pasta = f"sucesso_cliente/{contrato_id}/comentarios"
        for arquivo in arquivos:
            salvo = StorageService.salvar(arquivo, pasta)
            if not salvo:
                continue
            cls.repository.inserir_anexo({
                "historico_id": historico_id,
                "contrato_id": contrato_id,
                "arquivo_original": salvo.get("arquivo_original"),
                "nome_arquivo": salvo.get("nome"),
                "caminho": f"{pasta}/{salvo.get('nome')}",
                "url": salvo.get("url"),
                "mime_type": salvo.get("mime_type"),
                "tamanho": salvo.get("tamanho"),
            })

    @classmethod
    def _decorar_contrato(cls, contrato):
        contrato = dict(contrato)
        valor = cls._decimal(contrato.get("valor_servicos_bruto") or contrato.get("valor_mensal"))
        contrato["valor_bruto_cs"] = valor
        contrato["curva"] = cls._curva(valor)
        contrato["status_relacionamento_label"] = STATUS_RELACIONAMENTO.get(contrato.get("status_relacionamento"), "Sem registro")
        return contrato

    @classmethod
    def _decorar_pesquisa(cls, pesquisa):
        pesquisa = dict(pesquisa)
        pesquisa["perguntas"] = cls._json_lista(pesquisa.get("perguntas_json"))
        pesquisa["respostas"] = cls._json_lista(pesquisa.get("respostas_json"))
        pesquisa["classificacao_label"] = cls._classificacao_label(pesquisa.get("classificacao_nota"))
        return pesquisa

    @classmethod
    def _decorar_lote_pesquisa(cls, lote):
        lote = dict(lote)
        lote["media_lote"] = cls._decimal(lote.get("media_lote")) if lote.get("media_lote") is not None else None
        lote["classificacao_label"] = cls._classificacao_label(cls._classificacao_nota(lote["media_lote"])) if lote.get("media_lote") is not None else "Sem respostas"
        return lote

    @classmethod
    def _normalizar_pesquisa(cls, dados, validar=False):
        origem_perguntas = dados.getlist("perguntas") if hasattr(dados, "getlist") else dados.get("perguntas", [])
        perguntas = []
        for pergunta in origem_perguntas:
            texto = (pergunta or "").strip()
            if texto:
                perguntas.append(texto[:500])
        if not perguntas:
            perguntas = PERGUNTAS_PADRAO_IMPLANTACAO.copy()
        destinatario_emails = (dados.get("destinatario_emails") or dados.get("destinatario_email") or "").strip().lower()
        destinatarios = cls._parse_emails(destinatario_emails)
        titulo = (dados.get("titulo") or "Pesquisa de satisfação da implantação").strip()[:160]
        referencia_data = cls._data_iso(dados.get("referencia_data")) or date.today().isoformat()
        if validar:
            if not destinatarios:
                raise ValueError("Informe ao menos um e-mail de destinatário válido.")
            if not perguntas:
                raise ValueError("Informe ao menos uma pergunta.")
        return {
            "destinatario_email": destinatario_emails,
            "destinatario_emails": destinatario_emails,
            "destinatarios": destinatarios,
            "titulo": titulo,
            "referencia_data": referencia_data,
            "perguntas": perguntas,
        }

    @staticmethod
    def _parse_emails(valor):
        emails = []
        for parte in (valor or "").replace(";", ",").replace("\n", ",").split(","):
            email = parte.strip().lower()
            if email and "@" in email and email not in emails:
                emails.append(email)
        return emails

    @staticmethod
    def _data_iso(valor):
        texto = (valor or "").strip()
        if not texto:
            return None
        try:
            return date.fromisoformat(texto).isoformat()
        except ValueError:
            return None

    @staticmethod
    def _json_lista(valor):
        if not valor:
            return []
        if isinstance(valor, list):
            return valor
        try:
            dados = json.loads(valor)
        except (TypeError, ValueError):
            return []
        return dados if isinstance(dados, list) else []

    @staticmethod
    def _enviar_email_pesquisa(contrato, destinatario, link, payload=None):
        cliente = contrato.get("cliente_nome_fantasia") or contrato.get("cliente_razao_social") or "cliente"
        contrato_numero = contrato.get("numero") or contrato.get("id")
        payload = payload or {}
        titulo = payload.get("titulo") or "Pesquisa de satisfação da implantação"
        referencia_data = payload.get("referencia_data") or ""
        assunto = f"{titulo} - {cliente}"
        corpo = (
            "Olá,\n\n"
            "A implantação do seu ambiente foi concluída e queremos entender como foi sua experiência com a nossa equipe técnica.\n\n"
            f"Cliente: {cliente}\n"
            f"Contrato: {contrato_numero}\n\n"
            "A pesquisa é rápida e ajuda nosso time de Sucesso do Cliente a identificar pontos fortes e oportunidades de melhoria.\n\n"
            f"Responder pesquisa: {link}\n\n"
            "Obrigado pela parceria.\n"
            "Equipe O3Cloud"
        )
        html = f"""
        <div style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,Helvetica,sans-serif;color:#17202a;">
          <div style="max-width:640px;margin:0 auto;padding:28px 16px;">
            <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
              <div style="padding:22px 26px;border-bottom:1px solid #eef0f2;">
                <div style="font-size:13px;color:#667085;text-transform:uppercase;letter-spacing:.04em;">O3Cloud</div>
                <h2 style="margin:8px 0 0;font-size:22px;line-height:1.3;color:#101828;">{titulo}</h2>
              </div>
              <div style="padding:26px;">
                <p style="margin:0 0 14px;font-size:15px;line-height:1.6;">Olá,</p>
                <p style="margin:0 0 18px;font-size:15px;line-height:1.6;">A implantação do seu ambiente foi concluída e queremos entender como foi sua experiência com a nossa equipe técnica.</p>
                <div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;padding:14px 16px;margin:18px 0;">
                  <div style="font-size:13px;color:#667085;margin-bottom:4px;">Cliente</div>
                  <div style="font-size:15px;font-weight:700;color:#101828;">{cliente}</div>
                  <div style="font-size:13px;color:#667085;margin-top:12px;margin-bottom:4px;">Contrato</div>
                  <div style="font-size:15px;font-weight:700;color:#101828;">{contrato_numero}</div>
                  <div style="font-size:13px;color:#667085;margin-top:12px;margin-bottom:4px;">Data de referência</div>
                  <div style="font-size:15px;font-weight:700;color:#101828;">{referencia_data}</div>
                </div>
                <p style="margin:0 0 22px;font-size:15px;line-height:1.6;">A pesquisa é rápida e ajuda nosso time de Sucesso do Cliente a identificar pontos fortes e oportunidades de melhoria.</p>
                <p style="margin:0 0 26px;">
                  <a href="{link}" style="display:inline-block;background:#0d6efd;color:#ffffff;text-decoration:none;font-weight:700;border-radius:6px;padding:12px 18px;font-size:15px;">Responder pesquisa</a>
                </p>
                <p style="margin:0;font-size:14px;line-height:1.6;color:#475467;">Obrigado pela parceria.<br><strong>Equipe O3Cloud</strong></p>
              </div>
            </div>
            <p style="margin:14px 4px 0;font-size:12px;line-height:1.5;color:#667085;">Se o botão não abrir, copie e cole este link no navegador:<br><a href="{link}" style="color:#0d6efd;">{link}</a></p>
          </div>
        </div>
        """
        return EmailService.enviar(assunto, corpo, [destinatario], corpo_html=html, finalidade="PESQUISA_SATISFACAO")

    @staticmethod
    def _resumo_resultado_email(resultado, link):
        if resultado.get("enviado"):
            return "Enviado para " + ", ".join(resultado.get("destinatarios") or [])
        return f"Não enviado: {resultado.get('motivo') or 'erro_desconhecido'}. Link: {link}"

    @staticmethod
    def _salvar_resposta_em_disco(pesquisa, registro):
        pasta = StorageService.BASE_STORAGE / "sucesso_cliente" / str(pesquisa.get("contrato_id")) / "pesquisas"
        pasta.mkdir(parents=True, exist_ok=True)
        nome = f"pesquisa-{pesquisa.get('id')}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        caminho = pasta / nome
        caminho.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(Path("sucesso_cliente") / str(pesquisa.get("contrato_id")) / "pesquisas" / nome)

    @staticmethod
    def _classificacao_nota(media):
        if media <= 3:
            return 0
        if media <= 7:
            return 5
        return 10

    @staticmethod
    def _classificacao_label(valor):
        return {
            0: "Muito insatisfeito",
            5: "Satisfatório",
            10: "Muito satisfeito",
        }.get(valor, "Sem resposta")

    @staticmethod
    def _curva(valor):
        if valor >= 2999.99:
            return "A"
        if valor >= 1000:
            return "B"
        return "C"

    @staticmethod
    def _decimal(valor):
        try:
            return float(valor or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor) if valor not in (None, "") else None
        except (TypeError, ValueError):
            return None
