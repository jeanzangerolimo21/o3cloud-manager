from datetime import datetime

from app.infraestrutura.truenas_backup_service import TrueNASBackupService


class ClienteTrueNASTeste:
    def __init__(self, arvore):
        self.arvore = arvore

    def listar_diretorio(self, path):
        return self.arvore.get(path, [])

    def stat(self, path):
        return {"mtime": datetime.now().timestamp(), "size": 42}


def test_varredura_inclui_arquivos_em_subdiretorios():
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
    assert arquivos[0]["path"] == "/mnt/BKP1/AJFlores/integraw/retorno.txt"
    assert arquivos[0]["recente"] is True
