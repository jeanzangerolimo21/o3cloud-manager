from app import create_app
from app.infraestrutura.agendamentos.executor import ProxmoxAgendamentoExecutor


app = create_app()

with app.app_context():
    resultados = ProxmoxAgendamentoExecutor.processar_pendentes()
    if not resultados:
        print("Nenhum agendamento Proxmox pendente.")
    for resultado in resultados:
        print(resultado)
