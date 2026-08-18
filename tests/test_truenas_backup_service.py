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


def test_varredura_consulta_data_dos_subdiretorios_sem_entrar_neles():
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

    subdiretorios = TrueNASBackupService._listar_subdiretorios_monitorados(
        cliente,
        "/mnt/BKP1/AJFlores",
        corte=0,
    )

    assert len(subdiretorios) == 1
    assert subdiretorios[0]["nome"] == "[DIR] integraw"
    assert subdiretorios[0]["recente"] is True
    assert cliente.listagens == ["/mnt/BKP1/AJFlores"]
