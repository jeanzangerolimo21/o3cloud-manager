import logging
import mimetypes
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def enviar(assunto, corpo, destinatarios, corpo_html=None, finalidade="GERAL", anexos=None):
        destinatarios = sorted({email.strip().lower() for email in destinatarios if email and email.strip()})
        if not destinatarios:
            return {"enviado": False, "motivo": "sem_destinatarios"}

        config = EmailService._configuracao(finalidade)
        host = config.get("host")
        if not host:
            logger.info("SMTP nao configurado. E-mail nao enviado: %s", assunto)
            return {"enviado": False, "motivo": "smtp_nao_configurado", "destinatarios": destinatarios}

        port = int(config.get("port") or 587)
        usuario = config.get("usuario")
        senha = config.get("senha")
        remetente = config.get("remetente") or usuario
        usar_tls = bool(config.get("usar_tls"))

        if not remetente:
            return {"enviado": False, "motivo": "remetente_nao_configurado", "destinatarios": destinatarios}

        mensagem = EmailMessage()
        mensagem["Subject"] = assunto
        mensagem["From"] = remetente
        mensagem["To"] = ", ".join(destinatarios)
        mensagem.set_content(corpo)
        if corpo_html:
            mensagem.add_alternative(corpo_html, subtype="html")
        EmailService._adicionar_anexos(mensagem, anexos or [])

        with smtplib.SMTP(host, port, timeout=20) as smtp:
            if usar_tls:
                smtp.starttls()
            if usuario and senha:
                smtp.login(usuario, senha)
            smtp.send_message(mensagem)

        return {"enviado": True, "destinatarios": destinatarios, "origem_config": config.get("origem")}

    @staticmethod
    def _adicionar_anexos(mensagem, anexos):
        for anexo in anexos:
            caminho = Path(anexo.get("caminho") or "")
            if not caminho.is_file():
                logger.warning("Anexo de e-mail ignorado porque o arquivo não existe: %s", caminho)
                continue
            nome = anexo.get("nome") or anexo.get("arquivo_original") or caminho.name
            mime_type = anexo.get("mime_type") or mimetypes.guess_type(nome)[0] or "application/octet-stream"
            maintype, subtype = mime_type.split("/", 1) if "/" in mime_type else ("application", "octet-stream")
            mensagem.add_attachment(caminho.read_bytes(), maintype=maintype, subtype=subtype, filename=nome)

    @staticmethod
    def _configuracao(finalidade="GERAL"):
        banco = EmailService._configuracao_banco(finalidade)
        if banco:
            return banco
        if finalidade != "GERAL":
            return {"origem": "banco", "host": None}
        return {
            "origem": "env",
            "host": os.getenv("SMTP_HOST"),
            "port": os.getenv("SMTP_PORT", "587"),
            "usuario": os.getenv("SMTP_USER"),
            "senha": os.getenv("SMTP_PASSWORD"),
            "remetente": os.getenv("SMTP_FROM") or os.getenv("SMTP_USER"),
            "usar_tls": os.getenv("SMTP_TLS", "1") != "0",
        }

    @staticmethod
    def _configuracao_banco(finalidade="GERAL"):
        try:
            from app.configuracoes.email_service import EmailConfigService

            config = EmailConfigService.buscar_ativo(incluir_senha=True, finalidade=finalidade)
        except Exception as erro:
            logger.debug("Configuração SMTP do banco indisponível: %s", erro)
            return None
        if not config:
            return None
        return {
            "origem": "banco",
            "host": config.get("smtp_host"),
            "port": config.get("smtp_port") or 587,
            "usuario": config.get("smtp_user"),
            "senha": config.get("smtp_password"),
            "remetente": config.get("smtp_from") or config.get("smtp_user"),
            "usar_tls": bool(config.get("usar_tls")),
        }
