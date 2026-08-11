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
