import smtplib
from email.message import EmailMessage
from app.implantacao.cofre_senhas_service import CofreSenhaService
from app.repositories.email_config_repository import EmailConfigRepository


FINALIDADES_EMAIL = {
    "GERAL": "Geral do sistema",
    "PESQUISA_SATISFACAO": "Pesquisa de satisfação",
}


class EmailConfigService:
    repository = EmailConfigRepository

    @classmethod
    def listar(cls):
        return cls.repository.listar()

    @classmethod
    def buscar_ativo(cls, incluir_senha=False, provedor="SMTP", finalidade="GERAL"):
        config = cls.repository.buscar_ativo(provedor, finalidade)
        if config and incluir_senha:
            config["smtp_password"] = cls._decrypt_password(config.get("smtp_password_encrypted"))
            config["brevo_api_key"] = cls._decrypt_password(config.get("brevo_api_key_encrypted"))
        return config

    @classmethod
    def buscar_por_id(cls, id):
        return cls.repository.buscar_por_id(id)

    @classmethod
    def criar(cls, dados, usuario_email="sistema"):
        payload = cls._normalizar(dados)
        smtp = payload.pop("smtp_password", None)
        api = payload.pop("brevo_api_key", None)
        payload["smtp_password_encrypted"] = CofreSenhaService._encrypt(smtp) if smtp else None
        payload["brevo_api_key_encrypted"] = CofreSenhaService._encrypt(api) if api else None
        payload["created_by"] = usuario_email or "sistema"
        payload["updated_by"] = usuario_email or "sistema"
        id = cls.repository.inserir(payload)
        if payload.get("ativo"):
            cls.repository.desativar_outros(id, payload["provedor"], payload["finalidade"])
        return id

    @classmethod
    def atualizar(cls, id, dados, usuario_email="sistema"):
        if not cls.repository.buscar_por_id(id):
            raise ValueError("Serviço de e-mail não encontrado.")
        payload = cls._normalizar(dados)
        smtp = payload.pop("smtp_password", None)
        api = payload.pop("brevo_api_key", None)
        payload["smtp_password_encrypted"] = CofreSenhaService._encrypt(smtp) if smtp else None
        payload["brevo_api_key_encrypted"] = CofreSenhaService._encrypt(api) if api else None
        payload["updated_by"] = usuario_email or "sistema"
        cls.repository.atualizar(id, payload)
        if payload.get("ativo"):
            cls.repository.desativar_outros(id, payload["provedor"], payload["finalidade"])

    @classmethod
    def testar(cls, id, destinatario=None):
        config = cls.repository.buscar_por_id(id)
        if not config:
            raise ValueError("Serviço de e-mail não encontrado.")
        if config.get("provedor") == "BREVO":
            raise ValueError("O teste da Brevo é feito pelo disparo de teste do CRM.")
        senha = cls._decrypt_password(config.get("smtp_password_encrypted"))
        remetente = config.get("smtp_from") or config.get("smtp_user")
        destino = (destinatario or remetente or "").strip()
        if not remetente or not destino:
            raise ValueError("Remetente e destinatário são obrigatórios.")
        msg = EmailMessage()
        msg["Subject"] = "Teste de e-mail - O3Cloud Manager"
        msg["From"] = remetente
        msg["To"] = destino
        msg.set_content("Teste de envio SMTP do O3Cloud Manager.")
        try:
            with smtplib.SMTP(config.get("smtp_host"), int(config.get("smtp_port") or 587), timeout=20) as smtp:
                if config.get("usar_tls"):
                    smtp.starttls()
                if config.get("smtp_user") and senha:
                    smtp.login(config["smtp_user"], senha)
                smtp.send_message(msg)
        except Exception as e:
            cls.repository.registrar_teste(id, "ERRO", str(e))
            raise ValueError(f"Falha no envio de teste: {e}") from e
        cls.repository.registrar_teste(id, "OK", f"Teste enviado para {destino}.")
        return {"enviado": True, "destinatario": destino}

    @classmethod
    def _normalizar(cls, d):
        prov = (d.get("provedor") or "SMTP").strip().upper()
        if prov not in ("SMTP", "BREVO"):
            raise ValueError("Provedor de e-mail inválido.")
        finalidade = (d.get("finalidade") or "GERAL").strip().upper()
        if finalidade not in FINALIDADES_EMAIL:
            raise ValueError("Finalidade de e-mail inválida.")
        nome = (d.get("nome") or "Serviço de E-mail").strip()
        if not nome:
            raise ValueError("Nome é obrigatório.")
        payload = {
            "nome": nome[:120],
            "provedor": prov,
            "finalidade": finalidade,
            "smtp_host": (d.get("smtp_host") or "").strip(),
            "smtp_port": cls._int(d.get("smtp_port")) or 587,
            "smtp_user": (d.get("smtp_user") or "").strip(),
            "smtp_password": d.get("smtp_password") or "",
            "smtp_from": (d.get("smtp_from") or "").strip(),
            "brevo_sender_email": (d.get("brevo_sender_email") or "").strip(),
            "brevo_sender_name": (d.get("brevo_sender_name") or "").strip(),
            "brevo_reply_to": (d.get("brevo_reply_to") or "").strip(),
            "brevo_daily_limit": cls._int(d.get("brevo_daily_limit")),
            "brevo_environment": (d.get("brevo_environment") or "production").strip(),
            "brevo_api_url": (d.get("brevo_api_url") or "https://api.brevo.com/v3").strip(),
            "brevo_api_key": d.get("brevo_api_key") or "",
            "usar_tls": cls._flag(d, "usar_tls"),
            "ativo": cls._flag(d, "ativo"),
            "observacoes": (d.get("observacoes") or "").strip(),
        }
        if prov == "SMTP" and not payload["smtp_host"]:
            raise ValueError("Host SMTP é obrigatório para o provedor SMTP.")
        if prov == "BREVO":
            if not payload["brevo_sender_email"] or "@" not in payload["brevo_sender_email"]:
                raise ValueError("BREVO_SENDER_EMAIL inválido.")
            if not payload["brevo_api_url"]:
                raise ValueError("BREVO_API_URL é obrigatório.")
            if payload["brevo_daily_limit"] is not None and payload["brevo_daily_limit"] < 1:
                raise ValueError("BREVO_DAILY_LIMIT deve ser maior que zero.")
        return payload

    @staticmethod
    def _decrypt_password(v):
        return CofreSenhaService._decrypt(v) if v else None

    @staticmethod
    def _flag(d, k):
        if hasattr(d, "getlist"):
            return any(str(v).lower() in ("1", "true", "on", "sim") for v in d.getlist(k))
        return str(d.get(k) or "").lower() in ("1", "true", "on", "sim")

    @staticmethod
    def _int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None
