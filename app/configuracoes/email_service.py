import smtplib
from email.message import EmailMessage

from app.implantacao.cofre_senhas_service import CofreSenhaService
from app.repositories.email_config_repository import EmailConfigRepository


class EmailConfigService:
    repository = EmailConfigRepository

    @classmethod
    def listar(cls):
        return cls.repository.listar()

    @classmethod
    def buscar_ativo(cls, incluir_senha=False):
        config = cls.repository.buscar_ativo()
        if not config:
            return None
        if incluir_senha:
            config["smtp_password"] = cls._decrypt_password(config.get("smtp_password_encrypted"))
        return config

    @classmethod
    def buscar_por_id(cls, config_id):
        return cls.repository.buscar_por_id(config_id)

    @classmethod
    def criar(cls, dados, usuario_email="sistema"):
        payload = cls._normalizar(dados, exigir_senha=False)
        senha = payload.pop("smtp_password", None)
        payload["smtp_password_encrypted"] = CofreSenhaService._encrypt(senha) if senha else None
        payload["created_by"] = usuario_email or "sistema"
        payload["updated_by"] = usuario_email or "sistema"
        config_id = cls.repository.inserir(payload)
        if payload.get("ativo"):
            cls.repository.desativar_outros(config_id)
        return config_id

    @classmethod
    def atualizar(cls, config_id, dados, usuario_email="sistema"):
        existente = cls.repository.buscar_por_id(config_id)
        if not existente:
            raise ValueError("Serviço de e-mail não encontrado.")
        payload = cls._normalizar(dados, exigir_senha=False)
        senha = payload.pop("smtp_password", None)
        payload["smtp_password_encrypted"] = CofreSenhaService._encrypt(senha) if senha else None
        payload["updated_by"] = usuario_email or "sistema"
        cls.repository.atualizar(config_id, payload)
        if payload.get("ativo"):
            cls.repository.desativar_outros(config_id)

    @classmethod
    def testar(cls, config_id, destinatario=None):
        config = cls.repository.buscar_por_id(config_id)
        if not config:
            raise ValueError("Serviço de e-mail não encontrado.")
        senha = cls._decrypt_password(config.get("smtp_password_encrypted"))
        remetente = config.get("smtp_from") or config.get("smtp_user")
        if not remetente:
            raise ValueError("Remetente não configurado.")
        destino = (destinatario or remetente or "").strip()
        if not destino:
            raise ValueError("Informe um destinatário para teste.")

        mensagem = EmailMessage()
        mensagem["Subject"] = "Teste de e-mail - O3Cloud Manager"
        mensagem["From"] = remetente
        mensagem["To"] = destino
        mensagem.set_content("Teste de envio SMTP do O3Cloud Manager.")

        try:
            with smtplib.SMTP(config.get("smtp_host"), int(config.get("smtp_port") or 587), timeout=20) as smtp:
                if config.get("usar_tls"):
                    smtp.starttls()
                if config.get("smtp_user") and senha:
                    smtp.login(config.get("smtp_user"), senha)
                smtp.send_message(mensagem)
        except Exception as erro:
            cls.repository.registrar_teste(config_id, "ERRO", str(erro))
            raise ValueError(f"Falha no envio de teste: {erro}") from erro

        cls.repository.registrar_teste(config_id, "OK", f"Teste enviado para {destino}.")
        return {"enviado": True, "destinatario": destino}

    @classmethod
    def _normalizar(cls, dados, exigir_senha=False):
        nome = cls._texto(dados.get("nome")) or "SMTP Principal"
        smtp_host = cls._texto(dados.get("smtp_host"))
        smtp_port = cls._inteiro(dados.get("smtp_port")) or 587
        smtp_user = cls._texto(dados.get("smtp_user"))
        smtp_password = dados.get("smtp_password") or ""
        smtp_from = cls._texto(dados.get("smtp_from"))
        if not smtp_host:
            raise ValueError("Host SMTP é obrigatório.")
        if smtp_port < 1 or smtp_port > 65535:
            raise ValueError("Porta SMTP inválida.")
        if exigir_senha and not smtp_password:
            raise ValueError("Senha SMTP é obrigatória.")
        return {
            "nome": nome,
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "smtp_user": smtp_user,
            "smtp_password": smtp_password,
            "smtp_from": smtp_from,
            "usar_tls": cls._flag(dados, "usar_tls"),
            "ativo": cls._flag(dados, "ativo"),
            "observacoes": cls._texto(dados.get("observacoes")),
        }

    @staticmethod
    def _decrypt_password(valor):
        if not valor:
            return None
        return CofreSenhaService._decrypt(valor)

    @staticmethod
    def _flag(dados, chave):
        if hasattr(dados, "getlist"):
            valores = dados.getlist(chave)
            return any(str(valor).lower() in ("1", "true", "on", "sim") for valor in valores)
        return str(dados.get(chave) or "").lower() in ("1", "true", "on", "sim")

    @staticmethod
    def _texto(valor):
        return (valor or "").strip() or None

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor)
        except (TypeError, ValueError):
            return None
