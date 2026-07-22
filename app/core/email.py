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

        host = os.getenv("SMTP_HOST")
        if not host:
            logger.info("SMTP_HOST nao configurado. E-mail nao enviado: %s", assunto)
            return {"enviado": False, "motivo": "smtp_nao_configurado", "destinatarios": destinatarios}

        port = int(os.getenv("SMTP_PORT", "587"))
        usuario = os.getenv("SMTP_USER")
        senha = os.getenv("SMTP_PASSWORD")
        remetente = os.getenv("SMTP_FROM") or usuario
        usar_tls = os.getenv("SMTP_TLS", "1") != "0"

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

        return {"enviado": True, "destinatarios": destinatarios}
