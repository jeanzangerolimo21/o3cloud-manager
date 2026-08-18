import gzip

from app.configuracoes.backup_service import BackupSistemaService


def test_localizar_mysqldump_usa_variavel_de_ambiente(monkeypatch, tmp_path):
    mysqldump = tmp_path / "mysqldump"
    mysqldump.write_text("#!/bin/sh\n", encoding="utf-8")
    mysqldump.chmod(0o755)

    monkeypatch.setenv("MYSQLDUMP_PATH", str(mysqldump))
    monkeypatch.setattr("shutil.which", lambda _: None)

    assert BackupSistemaService._localizar_mysqldump() == str(mysqldump)


def test_localizar_mysqldump_usa_path_quando_disponivel(monkeypatch, tmp_path):
    mysqldump = tmp_path / "mysqldump"
    mysqldump.write_text("#!/bin/sh\n", encoding="utf-8")
    mysqldump.chmod(0o755)

    monkeypatch.delenv("MYSQLDUMP_PATH", raising=False)
    monkeypatch.setattr("shutil.which", lambda _: str(mysqldump))

    assert BackupSistemaService._localizar_mysqldump() == str(mysqldump)


def test_localizar_mysqldump_usa_caminho_padrao_com_path_incompleto(monkeypatch):
    monkeypatch.delenv("MYSQLDUMP_PATH", raising=False)
    monkeypatch.setattr("shutil.which", lambda _: None)
    monkeypatch.setattr("app.configuracoes.backup_service.os.path.isfile", lambda path: path == "/usr/bin/mysqldump")
    monkeypatch.setattr("app.configuracoes.backup_service.os.access", lambda path, mode: path == "/usr/bin/mysqldump")

    assert BackupSistemaService._localizar_mysqldump() == "/usr/bin/mysqldump"


class ArquivoUploadFake:
    def __init__(self, nome):
        self.filename = nome
        self.destino = None

    def save(self, destino):
        self.destino = destino
        destino.write_text("backup", encoding="utf-8")


def test_dump_database_gera_gzip_valido(monkeypatch, tmp_path):
    monkeypatch.setenv("DB_HOST", "127.0.0.1")
    monkeypatch.setenv("DB_PORT", "3306")
    monkeypatch.setenv("DB_USER", "root")
    monkeypatch.setenv("DB_PASSWORD", "senha")
    monkeypatch.setenv("DB_NAME", "o3cloud_manager")
    monkeypatch.setattr(BackupSistemaService, "_localizar_mysqldump", lambda: "/usr/bin/mysqldump")

    def fake_run(comando, stdout, stderr, env, timeout):
        stdout.write(b"-- MariaDB dump\nCREATE TABLE teste (id int);\n")

        class Resultado:
            returncode = 0
            stderr = b""

        return Resultado()

    monkeypatch.setattr("app.configuracoes.backup_service.subprocess.run", fake_run)

    destino = tmp_path / "database.sql.gz"
    BackupSistemaService._dump_database(destino)

    with gzip.open(destino, "rb") as arquivo:
        conteudo = arquivo.read()

    assert conteudo.startswith(b"-- MariaDB dump")
    assert b"CREATE TABLE teste" in conteudo


def test_restaurar_upload_exige_confirmacao():
    try:
        BackupSistemaService.restaurar_upload(ArquivoUploadFake("backup.sql.gz"), {"restaurar_banco": "1", "confirmacao": "ERRADO"}, "admin@example.com")
    except ValueError as erro:
        assert "RESTAURAR" in str(erro)
    else:
        raise AssertionError("restauracao sem confirmacao deveria falhar")


def test_restaurar_upload_chama_restore_db_com_skip_service(monkeypatch, tmp_path):
    chamadas = []

    monkeypatch.setattr(BackupSistemaService, "RESTORE_UPLOAD_DIR", tmp_path)
    monkeypatch.setenv("DB_NAME", "o3cloud_manager")
    monkeypatch.setattr("app.configuracoes.backup_service.Path.cwd", lambda: tmp_path)
    script = tmp_path / "deployment" / "restore-db.sh"
    script.parent.mkdir()
    script.write_text("#!/bin/sh\n", encoding="utf-8")

    def fake_run(comando, cwd, env, stdout, stderr, text, timeout):
        chamadas.append((comando, cwd, env, timeout))
        class Resultado:
            returncode = 0
            stdout = "ok"
            stderr = ""
        return Resultado()

    monkeypatch.setattr("app.configuracoes.backup_service.subprocess.run", fake_run)

    resultado = BackupSistemaService.restaurar_upload(
        ArquivoUploadFake("backup.sql.gz"),
        {"restaurar_banco": "1", "confirmacao": "RESTAURAR"},
        "admin@example.com",
    )

    assert resultado.startswith("RESTORE: OK")
    assert chamadas
    comando = chamadas[0][0]
    assert comando[0].endswith("deployment/restore-db.sh")
    assert "--yes" in comando
    assert "--skip-service" in comando
    assert chamadas[0][2]["RESTORE_CONFIRM"] == "o3cloud_manager"


def test_validar_membro_tar_bloqueia_path_traversal():
    import tarfile

    membro = tarfile.TarInfo("../fora")
    try:
        BackupSistemaService._validar_membro_tar(membro)
    except ValueError as erro:
        assert "caminho invalido" in str(erro)
    else:
        raise AssertionError("path traversal deveria ser bloqueado")
