import os

from dotenv import load_dotenv
from pathlib import Path


load_dotenv()


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "o3cloud-dev"
    )

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
