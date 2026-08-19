from app.repositories.pbs_backup_repository import PBSBackupRepository


class CursorFake:
    def __init__(self):
        self.sqls = []
        self.params = []
        self.select_called = False

    def execute(self, sql, params=None):
        self.sqls.append(sql)
        self.params.append(params)
        if "SELECT id FROM proxmox_vm_inventory" in sql:
            self.select_called = True

    def fetchall(self):
        return [(1,), (2,), (3,)]

    def close(self):
        pass


class ConnectionFake:
    def __init__(self):
        self.cursor_fake = CursorFake()
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.cursor_fake

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        pass


def test_atualizar_politicas_altera_apenas_recursos_visiveis(monkeypatch):
    conn = ConnectionFake()
    monkeypatch.setattr(PBSBackupRepository, "connection", classmethod(lambda cls: conn))
    monkeypatch.setattr(PBSBackupRepository, "generate_uuid", staticmethod(lambda: "uuid-teste"))

    PBSBackupRepository.atualizar_politicas(["5"], recurso_ids_visiveis=["2", "5"])

    assert conn.cursor_fake.select_called is False
    inserts = [params for params in conn.cursor_fake.params if params]
    assert inserts == [("uuid-teste", 2, 24), ("uuid-teste", 5, 168)]
    assert conn.commits == 1
    assert conn.rollbacks == 0


def test_atualizar_politicas_sem_visiveis_mantem_fluxo_legado_todos_ativos(monkeypatch):
    conn = ConnectionFake()
    monkeypatch.setattr(PBSBackupRepository, "connection", classmethod(lambda cls: conn))
    monkeypatch.setattr(PBSBackupRepository, "generate_uuid", staticmethod(lambda: "uuid-teste"))

    PBSBackupRepository.atualizar_politicas(["2"])

    assert conn.cursor_fake.select_called is True
    inserts = [params for params in conn.cursor_fake.params if params]
    assert inserts == [("uuid-teste", 1, 24), ("uuid-teste", 2, 168), ("uuid-teste", 3, 24)]
