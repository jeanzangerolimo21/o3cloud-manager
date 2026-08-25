from datetime import datetime

from app.infraestrutura.truenas_backup_service import TrueNASBackupService


class ClienteTrueNASTeste:
    def __init__(self, arvore):
        self.arvore = arvore
        self.listagens = []

    def listar_diretorio(self, path):
        self.listagens.append(path)
        return self.arvore.get(path, [])

    def stat(self, path):
        return {"mtime": datetime.now().timestamp(), "size": 42}


def test_varredura_busca_arquivos_recursivamente_nos_subdiretorios():
    cliente = ClienteTrueNASTeste(
        {
            "/mnt/BKP1/AJFlores": [
                {"name": "integraw", "path": "/mnt/BKP1/AJFlores/integraw", "type": "DIRECTORY"},
            ],
            "/mnt/BKP1/AJFlores/integraw": [
                {"name": "retorno.txt", "path": "/mnt/BKP1/AJFlores/integraw/retorno.txt", "type": "FILE"},
            ],
        }
    )

    arquivos = TrueNASBackupService._listar_arquivos_monitorados(
        cliente,
        "/mnt/BKP1/AJFlores",
        corte=0,
    )

    assert len(arquivos) == 1
    assert arquivos[0]["nome"] == "retorno.txt"
    assert arquivos[0]["recente"] is True
    assert cliente.listagens == [
        "/mnt/BKP1/AJFlores",
        "/mnt/BKP1/AJFlores/integraw",
    ]


def test_storage_valido_e_normalizado():
    assert TrueNASBackupService._normalizar_storage("/mnt/bkp1") == "/mnt/BKP1"


def test_storage_invalido_e_rejeitado():
    try:
        TrueNASBackupService._normalizar_storage("/mnt/OUTRO")
    except ValueError:
        pass
    else:
        raise AssertionError("storage invalido deveria ser rejeitado")
