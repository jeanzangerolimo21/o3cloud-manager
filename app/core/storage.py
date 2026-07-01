import uuid
from pathlib import Path

from werkzeug.utils import secure_filename


class StorageService:

    BASE_UPLOAD = Path(__file__).resolve().parents[2] / "uploads"

    PARCEIROS = "parceiros"

    CLIENTES = "clientes"

    CONTRATOS = "contratos"

    DOCUMENTOS = "documentos"

    IMPLANTACAO = "implantacao"

    ALLOWED_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".svg"
    }

    MAX_FILE_SIZE = 2 * 1024 * 1024

    @classmethod
    def salvar(cls, arquivo, pasta):

        if not arquivo:
            return None

        if arquivo.filename == "":
            return None
        
        extensao = Path(
            secure_filename(
                arquivo.filename
            )
        ).suffix.lower()

        if extensao not in cls.ALLOWED_EXTENSIONS:

            raise ValueError(
                f"Extensão '{extensao}' não permitida."
            )

        nome = f"{uuid.uuid4()}{extensao}"

        arquivo.seek(0, 2)

        tamanho = arquivo.tell()

        arquivo.seek(0)

        if tamanho > cls.MAX_FILE_SIZE:

            raise ValueError(
                "Arquivo maior que 2 MB."
            )

        destino = cls.BASE_UPLOAD / pasta

        destino.mkdir(
            parents=True,
            exist_ok=True
        )

        arquivo.save(
            destino / nome
        )

        return nome

    @classmethod
    def url(cls, pasta, nome):

        if not nome:
            return None

        return f"/uploads/{pasta}/{nome}"

    @classmethod
    def excluir(cls, pasta, nome):

        if not nome:
            return

        arquivo = cls.BASE_UPLOAD / pasta / nome

        if arquivo.exists():

            arquivo.unlink()

    @classmethod
    def caminho(cls, pasta, nome):

        if not nome:
            return None

        return f"{pasta}/{nome}"
