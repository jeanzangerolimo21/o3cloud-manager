import mimetypes
import shutil
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename


class StorageService:
    
    BASE_STORAGE = Path("/opt/o3cloud-manager/storage")

    PARCEIROS = "parceiros"
    CLIENTES = "clientes"
    CONTRATOS = "contratos"
    DOCUMENTOS = "documentos"
    PROPOSTAS = "propostas"
    ANEXOS = "anexos"
    BACKUPS = "backups"
    IMPLANTACAO = "implantacao"
    TEMPORARIOS = "temporarios"
    LOGS = "logs"

    IMAGE_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
    }

    DOCUMENT_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".csv",
        ".zip",
        ".dwg",
    }

    ALLOWED_EXTENSIONS = (
        IMAGE_EXTENSIONS |
        DOCUMENT_EXTENSIONS
    )

    MAX_FILE_SIZE = 20 * 1024 * 1024

    @classmethod
    def salvar(cls, arquivo, pasta):

        if not arquivo or arquivo.filename == "":
            return None

        extensao = Path(
            secure_filename(arquivo.filename)
        ).suffix.lower()

        if extensao not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Extensão '{extensao}' não permitida."
            )

        arquivo.seek(0, 2)
        tamanho = arquivo.tell()
        arquivo.seek(0)

        if tamanho > cls.MAX_FILE_SIZE:
            raise ValueError(
                "Arquivo excede o tamanho máximo permitido."
            )

        nome = f"{uuid.uuid4()}{extensao}"

        destino = cls.BASE_STORAGE / pasta

        destino.mkdir(
            parents=True,
            exist_ok=True
        )

        caminho = destino / nome

        arquivo.save(caminho)

        return {
            "nome": nome,
            "arquivo_original": arquivo.filename,
            "caminho": str(caminho),
            "url": cls.url(pasta, nome),
            "tamanho": tamanho,
            "extensao": extensao,
            "mime_type": mimetypes.guess_type(nome)[0]
        }

    @classmethod
    def url(cls, pasta, nome):

        if not nome:
            return None

        return f"/storage/{pasta}/{nome}"

    @classmethod
    def excluir(cls, pasta, nome):

        arquivo = cls.BASE_STORAGE / pasta / nome

        if arquivo.exists():
            arquivo.unlink()

    @classmethod
    def existe(cls, pasta, nome):

        return (
            cls.BASE_STORAGE /
            pasta /
            nome
        ).exists()

    @classmethod
    def mover(cls, origem, destino, nome):

        origem = cls.BASE_STORAGE / origem / nome
        destino_dir = cls.BASE_STORAGE / destino

        destino_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.move(
            origem,
            destino_dir / nome
        )

    @classmethod
    def copiar(cls, origem, destino, nome):

        origem = cls.BASE_STORAGE / origem / nome
        destino_dir = cls.BASE_STORAGE / destino

        destino_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(
            origem,
            destino_dir / nome
        )

    @classmethod
    def caminho(cls, pasta, nome):

        return cls.BASE_STORAGE / pasta / nome
