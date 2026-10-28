import os
from datetime import timedelta

from dotenv import load_dotenv
from pathlib import Path


load_dotenv()


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "o3cloud-dev"
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "1") != "0"
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv("SESSION_LIFETIME_HOURS", "8")))
    WTF_CSRF_TIME_LIMIT = int(os.getenv("CSRF_TIME_LIMIT_SECONDS", "7200"))

    DB_HOST = os.getenv("DB_HOST")

    DB_PORT = int(
        os.getenv(
            "DB_PORT",
            "3306"
        )
    )

    DB_NAME = os.getenv("DB_NAME")

    DB_USER = os.getenv("DB_USER")

    DB_PASSWORD = os.getenv("DB_PASSWORD")

    STORAGE_PATH = Path("/opt/o3cloud-manager/storage")

    COFRE_SENHAS_KEY = os.getenv("COFRE_SENHAS_KEY")

    COFRE_SENHA_GERADOR_TAMANHO = int(os.getenv("COFRE_SENHA_GERADOR_TAMANHO", "20"))
    COFRE_SENHA_GERADOR_MAIUSCULAS = os.getenv("COFRE_SENHA_GERADOR_MAIUSCULAS", "1") != "0"
    COFRE_SENHA_GERADOR_MINUSCULAS = os.getenv("COFRE_SENHA_GERADOR_MINUSCULAS", "1") != "0"
    COFRE_SENHA_GERADOR_NUMEROS = os.getenv("COFRE_SENHA_GERADOR_NUMEROS", "1") != "0"
    COFRE_SENHA_GERADOR_SIMBOLOS = os.getenv("COFRE_SENHA_GERADOR_SIMBOLOS", "1") != "0"

    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
    SECURITY_CONTACT_EMAIL = os.getenv("SECURITY_CONTACT_EMAIL", "contato@o3cloud.com.br")
    TRUST_PROXY = os.getenv("TRUST_PROXY", "0") != "0"
    PROXY_FIX_HOPS = int(os.getenv("PROXY_FIX_HOPS", "1"))
    COFRE_COMPARTILHAMENTO_TTL_MINUTOS = int(os.getenv("COFRE_COMPARTILHAMENTO_TTL_MINUTOS", "5"))
