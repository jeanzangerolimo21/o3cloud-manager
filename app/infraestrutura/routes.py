from flask import Blueprint
from flask import render_template
from flask import url_for


infraestrutura_bp = Blueprint(
    "infraestrutura",
    __name__,
    url_prefix="/infraestrutura",
)


CONSULTAS = {
    "backups-pbs": {
        "titulo": "Backups PBS",
        "descricao": "Consulta de snapshots dos clientes no Proxmox Backup Server.",
        "icone": "bi-server",
        "origem": "PBS",
        "objetivo": "Snapshots dos clientes",
        "status": "Preparado para consulta",
        "campos": (
            "Cliente",
            "Ambiente",
            "VM/Container",
            "Snapshot",
            "Data do backup",
            "Retencao",
            "Status",
        ),
    },
    "monitoramento-zabbix": {
        "titulo": "Monitoramento Zabbix",
        "descricao": "Consulta operacional do monitoramento dos clientes no Zabbix.",
        "icone": "bi-activity",
        "origem": "Zabbix",
        "objetivo": "Hosts, alertas e disponibilidade",
        "status": "Preparado para consulta",
        "campos": (
            "Cliente",
            "Host",
            "Grupo",
            "Disponibilidade",
            "Alertas abertos",
            "Severidade",
            "Ultima coleta",
        ),
    },
    "backup-nas": {
        "titulo": "Backup NAS",
        "descricao": "Consulta de backups NAS dos clientes no TrueNAS.",
        "icone": "bi-device-hdd",
        "origem": "TrueNAS",
        "objetivo": "Backups NAS dos clientes",
        "status": "Preparado para consulta",
        "campos": (
            "Cliente",
            "Dataset",
            "Share",
            "Job",
            "Ultima execucao",
            "Retencao",
            "Status",
        ),
    },
}


@infraestrutura_bp.route("/backups-pbs")
def backups_pbs():
    return _render_consulta("backups-pbs")


@infraestrutura_bp.route("/monitoramento-zabbix")
def monitoramento_zabbix():
    return _render_consulta("monitoramento-zabbix")


@infraestrutura_bp.route("/backup-nas")
def backup_nas():
    return _render_consulta("backup-nas")


def _render_consulta(chave):
    consulta = CONSULTAS[chave]
    return render_template(
        "infraestrutura/consulta.html",
        consulta=consulta,
        integracoes_url=url_for("implantacao.integracoes_tecnicas"),
    )
