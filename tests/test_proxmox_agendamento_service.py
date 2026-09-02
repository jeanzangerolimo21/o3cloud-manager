from datetime import datetime, timedelta

from app.infraestrutura.agendamentos.service import ProxmoxAgendamentoService


class FakeRepository:
    payload = None

    @classmethod
    def buscar_inventario_qemu(cls, inventario_id):
        return {
            "id": inventario_id,
            "integracao_id": 10,
            "cluster_nome": "Cluster Beta",
            "cluster_base_url": "https://proxmox.local:8006",
            "node": "pve01",
            "vmid": 101,
            "nome": "vm-teste",
            "status": "running",
            "cpu_cores": 2,
            "cpu_sockets": 1,
            "memoria_mb": 4096,
            "raw_payload": "{}",
        }

    @classmethod
    def existe_ativo_vm(cls, integracao_id, node_nome, vmid):
        return False

    @classmethod
    def criar(cls, payload):
        cls.payload = payload
        return 123


def test_criar_agendamento_permite_upgrade_apenas_memoria(monkeypatch):
    FakeRepository.payload = None
    monkeypatch.setattr(ProxmoxAgendamentoService, "repository", FakeRepository)
    monkeypatch.setattr(
        ProxmoxAgendamentoService,
        "topologia_vm_live",
        classmethod(lambda cls, inventario_id: {
            "cpu_total": 2,
            "sockets": 1,
            "cores_por_socket": 2,
            "memoria_mb": 4096,
            "status": "running",
        }),
    )
    monkeypatch.setattr(ProxmoxAgendamentoService, "_validar_backup_pbs_recente", classmethod(lambda cls, vm: True))
    monkeypatch.setattr(ProxmoxAgendamentoService, "_enviar_email_cadastro", classmethod(lambda cls, agendamento_id: None))

    agendamento_id = ProxmoxAgendamentoService.criar({
        "inventario_id": "1",
        "executar_em": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),
        "cpu_nova": "",
        "memoria_nova_gb": "8",
        "desligar_se_necessario": "on",
        "religar_automaticamente": "on",
        "motivo": "Upgrade de memoria",
    }, usuario_email="teste@o3cloud.com.br")

    assert agendamento_id == 123
    assert FakeRepository.payload["cpu_nova"] is None
    assert FakeRepository.payload["memoria_original_mb"] == 4096
    assert FakeRepository.payload["memoria_nova_mb"] == 8192
