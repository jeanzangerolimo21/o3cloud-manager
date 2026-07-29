import logging
import os
import smtplib
from email.message import EmailMessage


logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def enviar(assunto, corpo, destinatarios):
        destinatarios = sorted({email.strip().lower() for email in destinatarios if email and email.strip()})
        if not destinatarios:
            return {"enviado": False, "motivo": "sem_destinatarios"}

        config = EmailService._configuracao()
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

        with smtplib.SMTP(host, port, timeout=20) as smtp:
            if usar_tls:
                smtp.starttls()
            if usuario and senha:
                smtp.login(usuario, senha)
            smtp.send_message(mensagem)

        return {"enviado": True, "destinatarios": destinatarios, "origem_config": config.get("origem")}

    @staticmethod
    def _configuracao():
        banco = EmailService._configuracao_banco()
        if banco:
            return banco
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
    def _configuracao_banco():
        try:
            from app.configuracoes.email_service import EmailConfigService

            config = EmailConfigService.buscar_ativo(incluir_senha=True)
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
