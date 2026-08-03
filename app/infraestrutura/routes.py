from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from app.infraestrutura.proxmox_service import ProxmoxInventoryService
from app.infraestrutura.pbs_backup_service import DEFAULT_DATASTORE, PBSBackupService
from app.infraestrutura.zabbix_service import ZabbixMonitoramentoService
from app.infraestrutura.truenas_backup_service import TrueNASBackupService


infraestrutura_bp = Blueprint(
    "infraestrutura",
    __name__,
    url_prefix="/infraestrutura",
)


ZABBIX_FILTROS_STATUS = (
    {"valor": "", "label": "Todos"},
    {"valor": "abertos", "label": "Abertos"},
    {"valor": "resolvidos", "label": "Resolvidos"},
    {"valor": "media", "label": "Média"},
    {"valor": "alta_media", "label": "Alta média"},
    {"valor": "alta", "label": "Alta"},
    {"valor": "critica", "label": "Crítica"},
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


@infraestrutura_bp.route("/clusters")
def clusters():
    return render_template(
        "infraestrutura/proxmox_clusters.html",
        clusters=ProxmoxInventoryService.clusters(),
        dashboard=ProxmoxInventoryService.dashboard_clusters(),
        execucoes=ProxmoxInventoryService.execucoes_recentes(),
        integracoes_url=url_for("implantacao.integracoes_tecnicas"),
        novo_cluster_url=url_for("implantacao.nova_integracao_config", grupo="tecnicas", tipo="proxmox"),
    )


@infraestrutura_bp.route("/nodes")
def nodes():
    return render_template(
        "infraestrutura/proxmox_nodes.html",
        nodes=ProxmoxInventoryService.listar_nodes_dashboard(),
        dashboard=ProxmoxInventoryService.dashboard_nodes(),
        execucoes=ProxmoxInventoryService.execucoes_recentes(),
        integracoes_url=url_for("implantacao.integracoes_tecnicas"),
    )


@infraestrutura_bp.route("/maquinas-virtuais")
def maquinas_virtuais():
    return _render_proxmox_inventory("qemu")


@infraestrutura_bp.route("/containers")
def containers():
    return _render_proxmox_inventory("lxc")


@infraestrutura_bp.route("/proxmox/<int:inventario_id>/cliente", methods=["POST"])
def vincular_cliente_proxmox(inventario_id):
    try:
        ProxmoxInventoryService.vincular_cliente(inventario_id, request.form.get("cliente_id"))
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Vínculo com cliente atualizado.", "success")
    return redirect(request.referrer or url_for("infraestrutura.maquinas_virtuais"))


@infraestrutura_bp.route("/proxmox/<int:integracao_id>/sincronizar", methods=["POST"])
def sincronizar_cluster_proxmox(integracao_id):
    try:
        resultado = ProxmoxInventoryService.sincronizar_integracao(integracao_id, "sistema")
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        categoria = "success" if resultado.get("status") == "OK" else "danger"
        flash(resultado.get("mensagem"), categoria)
    return redirect(request.referrer or url_for("infraestrutura.clusters"))


@infraestrutura_bp.route("/proxmox/sincronizar", methods=["POST"])
def sincronizar_proxmox():
    try:
        resultado = ProxmoxInventoryService.sincronizar("sistema")
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        categoria = "success" if resultado.get("status") == "OK" else "danger"
        flash(resultado.get("mensagem"), categoria)
    return redirect(request.referrer or url_for("infraestrutura.maquinas_virtuais"))


@infraestrutura_bp.route("/backups-pbs")
def backups_pbs():
    escopos = PBSBackupService.escopos(ativo=True)
    selected_escopo_id = request.args.get("escopo_id", type=int)
    escopo = PBSBackupService.buscar_escopo(selected_escopo_id) if selected_escopo_id else (escopos[0] if escopos else None)
    status = request.args.get("status") or None
    tipo = request.args.get("tipo") or None
    node = request.args.get("node") or None
    pesquisa = request.args.get("q") or None
    return render_template(
        "infraestrutura/pbs_backups.html",
        recursos=PBSBackupService.listar(pesquisa=pesquisa, status=status, tipo=tipo, node=node),
        dashboard=PBSBackupService.dashboard(),
        nodes=PBSBackupService.nodes(),
        execucoes=PBSBackupService.execucoes_recentes(),
        escopos=escopos,
        escopo=escopo,
        integracoes_pbs=PBSBackupService.integracoes_pbs(),
        datastore=(escopo.get("datastore") if escopo else DEFAULT_DATASTORE),
        selected_escopo_id=escopo.get("id") if escopo else None,
        selected_status=status or "",
        selected_tipo=tipo or "",
        selected_node=node or "",
        pesquisa=pesquisa or "",
        integracoes_url=url_for("implantacao.integracoes_tecnicas"),
        novo_pbs_url=url_for("implantacao.nova_integracao_config", grupo="tecnicas", tipo="pbs"),
    )


@infraestrutura_bp.route("/pbs/escopos/novo", methods=["GET", "POST"])
def novo_escopo_pbs():
    integracoes_pbs = PBSBackupService.integracoes_pbs()
    if request.method == "POST":
        try:
            escopo_id = PBSBackupService.salvar_escopo(_dados_escopo_pbs())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("infraestrutura/pbs_escopo_form.html", escopo=request.form, modo="novo", integracoes_pbs=integracoes_pbs)
        flash("Escopo PBS cadastrado com sucesso.", "success")
        return redirect(url_for("infraestrutura.backups_pbs", escopo_id=escopo_id))
    return render_template("infraestrutura/pbs_escopo_form.html", escopo={"ativo": 1}, modo="novo", integracoes_pbs=integracoes_pbs)


@infraestrutura_bp.route("/pbs/escopos/<int:escopo_id>/editar", methods=["GET", "POST"])
def editar_escopo_pbs(escopo_id):
    escopo = PBSBackupService.buscar_escopo(escopo_id)
    if not escopo:
        flash("Escopo PBS não encontrado.", "danger")
        return redirect(url_for("infraestrutura.backups_pbs"))
    integracoes_pbs = PBSBackupService.integracoes_pbs()
    if request.method == "POST":
        try:
            PBSBackupService.salvar_escopo(_dados_escopo_pbs(), escopo_id=escopo_id)
        except ValueError as erro:
            flash(str(erro), "danger")
            escopo = {**escopo, **request.form}
            return render_template("infraestrutura/pbs_escopo_form.html", escopo=escopo, modo="editar", integracoes_pbs=integracoes_pbs)
        flash("Escopo PBS atualizado com sucesso.", "success")
        return redirect(url_for("infraestrutura.backups_pbs", escopo_id=escopo_id))
    return render_template("infraestrutura/pbs_escopo_form.html", escopo=escopo, modo="editar", integracoes_pbs=integracoes_pbs)


@infraestrutura_bp.route("/pbs/escopos/<int:escopo_id>/excluir")
def excluir_escopo_pbs(escopo_id):
    PBSBackupService.inativar_escopo(escopo_id)
    flash("Escopo PBS inativado.", "success")
    return redirect(url_for("infraestrutura.backups_pbs"))


@infraestrutura_bp.route("/pbs/sincronizar", methods=["POST"])
def sincronizar_pbs():
    escopo_id = request.form.get("escopo_id", type=int)
    try:
        resultado = PBSBackupService.sincronizar(escopo_id=escopo_id, usuario_email="sistema")
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        categoria = "success" if resultado.get("status") == "OK" else "danger"
        flash(resultado.get("mensagem"), categoria)
    return redirect(request.referrer or url_for("infraestrutura.backups_pbs", escopo_id=escopo_id))


@infraestrutura_bp.route("/pbs/sincronizar-todos", methods=["POST"])
def sincronizar_todos_pbs():
    try:
        resultado = PBSBackupService.sincronizar_todos(usuario_email="sistema")
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        categoria = "success" if resultado.get("status") == "OK" else "danger"
        flash(resultado.get("mensagem"), categoria)
    return redirect(request.referrer or url_for("infraestrutura.backups_pbs"))


@infraestrutura_bp.route("/pbs/politicas", methods=["POST"])
def atualizar_politicas_pbs():
    PBSBackupService.atualizar_politicas(request.form.getlist("recurso_ids_semanais"))
    flash("Políticas de backup PBS atualizadas.", "success")
    escopo_id = request.form.get("escopo_id", type=int)
    return redirect(request.referrer or url_for("infraestrutura.backups_pbs", escopo_id=escopo_id))


def _dados_escopo_pbs():
    return {
        "integracao_id": request.form.get("integracao_id"),
        "nome": request.form.get("nome"),
        "datastore": request.form.get("datastore"),
        "namespaces": request.form.get("namespaces"),
        "observacoes": request.form.get("observacoes"),
        "ativo": 1 if request.form.get("ativo") else 0,
    }


@infraestrutura_bp.route("/monitoramento-zabbix/sincronizar", methods=["POST"])
def sincronizar_zabbix():
    integracao_id = request.form.get("integracao_id", type=int)
    limite = request.form.get("limite", default=80, type=int)
    filtro_status = request.form.get("status") or ""
    try:
        resultado = ZabbixMonitoramentoService.sincronizar(integracao_id=integracao_id, limite=limite)
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        categoria = "success" if resultado.get("status") == "OK" else "danger"
        flash(resultado.get("mensagem"), categoria)
    return redirect(url_for("infraestrutura.monitoramento_zabbix", integracao_id=integracao_id, limite=limite, status=filtro_status))


@infraestrutura_bp.route("/monitoramento-zabbix")
def monitoramento_zabbix():
    integracao_id = request.args.get("integracao_id", type=int)
    limite = request.args.get("limite", default=80, type=int)
    filtro_status = request.args.get("status") or ""
    resultado = ZabbixMonitoramentoService.listar_alarmes(integracao_id=integracao_id, limite=limite)
    alarmes_cache = resultado.get("alarmes") or []
    alarmes = _filtrar_zabbix_status(alarmes_cache, filtro_status)
    return render_template(
        "infraestrutura/zabbix_alarmes.html",
        alarmes=alarmes,
        dashboard=ZabbixMonitoramentoService.dashboard(alarmes),
        status=resultado.get("status"),
        mensagem=resultado.get("mensagem"),
        integracao=resultado.get("integracao"),
        integracoes_zabbix=ZabbixMonitoramentoService.integracoes_zabbix(),
        selected_integracao_id=(resultado.get("integracao") or {}).get("id"),
        ultimo_sync=resultado.get("ultimo_sync"),
        limite=max(1, min(int(limite or 80), 200)),
        selected_status=filtro_status,
        filtros_status=ZABBIX_FILTROS_STATUS,
        integracoes_url=url_for("implantacao.integracoes_tecnicas"),
        novo_zabbix_url=url_for("implantacao.nova_integracao_config", grupo="tecnicas", tipo="zabbix"),
    )


def _filtrar_zabbix_status(alarmes, filtro_status):
    filtro = (filtro_status or "").strip()
    severidades = {
        "media": {2},
        "alta_media": {3},
        "alta": {4},
        "critica": {5},
    }
    if not filtro:
        return alarmes
    if filtro == "abertos":
        return [item for item in alarmes if item.get("aberto")]
    if filtro == "resolvidos":
        return [item for item in alarmes if not item.get("aberto")]
    if filtro in severidades:
        return [item for item in alarmes if item.get("severidade") in severidades[filtro]]
    return alarmes


@infraestrutura_bp.route("/backup-nas/sincronizar", methods=["POST"])
def sincronizar_backup_nas():
    integracao_id = request.form.get("integracao_id", type=int)
    periodo_horas = request.form.get("periodo_horas", default=24, type=int)
    pesquisa = request.form.get("q") or ""
    aba = request.form.get("aba") if request.form.get("aba") in {"alertas", "ok"} else "alertas"
    resultado = TrueNASBackupService.sincronizar(integracao_id=integracao_id, periodo_horas=periodo_horas)
    categoria = "success" if resultado.get("status") == "OK" else "danger"
    flash(resultado.get("mensagem"), categoria)
    return redirect(url_for("infraestrutura.backup_nas", integracao_id=integracao_id, periodo_horas=periodo_horas, q=pesquisa, aba=aba))


@infraestrutura_bp.route("/backup-nas")
def backup_nas():
    integracao_id = request.args.get("integracao_id", type=int)
    periodo_horas = request.args.get("periodo_horas", default=24, type=int)
    pesquisa = (request.args.get("q") or "").strip()
    aba = request.args.get("aba") if request.args.get("aba") in {"alertas", "ok"} else "alertas"
    resultado = TrueNASBackupService.listar(integracao_id=integracao_id)
    registros_cache = resultado.get("registros") or []
    registros = _filtrar_truenas_cache(registros_cache, pesquisa)
    return render_template(
        "infraestrutura/truenas_backups.html",
        registros=registros,
        registros_alerta=[item for item in registros if item.get("status") == "ALERTA"],
        registros_ok=[item for item in registros if item.get("status") == "OK"],
        dashboard=resultado.get("dashboard") or {},
        status=resultado.get("status"),
        mensagem=resultado.get("mensagem"),
        integracao=resultado.get("integracao"),
        integracoes_truenas=TrueNASBackupService.integracoes_truenas(),
        selected_integracao_id=(resultado.get("integracao") or {}).get("id"),
        periodo_horas=max(1, int(periodo_horas or 24)),
        pesquisa=pesquisa,
        aba=aba,
        integracoes_url=url_for("implantacao.integracoes_tecnicas"),
        novo_truenas_url=url_for("implantacao.nova_integracao_config", grupo="tecnicas", tipo="truenas"),
    )


def _filtrar_truenas_cache(registros, pesquisa):
    termo = (pesquisa or "").strip().lower()
    if not termo:
        return registros
    filtrados = []
    for item in registros:
        campos = [
            item.get("prefixo_proxmox"),
            item.get("cliente_nome"),
            item.get("pasta_path"),
            item.get("ultimo_arquivo"),
        ]
        campos.extend(detalhe.get("nome") for detalhe in item.get("detalhes_lista") or [])
        if any(termo in str(valor or "").lower() for valor in campos):
            filtrados.append(item)
    return filtrados


def _render_consulta(chave):
    consulta = CONSULTAS[chave]
    return render_template(
        "infraestrutura/consulta.html",
        consulta=consulta,
        integracoes_url=url_for("implantacao.integracoes_tecnicas"),
    )


def _render_proxmox_inventory(tipo):
    status = request.args.get("status") or None
    node = request.args.get("node") or None
    pesquisa = request.args.get("q") or None
    titulo = "Máquinas Virtuais" if tipo == "qemu" else "Containers"
    descricao = "Inventário sincronizado do Proxmox VE em modo somente leitura."
    return render_template(
        "infraestrutura/proxmox_inventory.html",
        tipo=tipo,
        titulo=titulo,
        descricao=descricao,
        recursos=ProxmoxInventoryService.listar(tipo=tipo, status=status, node=node, pesquisa=pesquisa),
        dashboard=ProxmoxInventoryService.dashboard(tipo=tipo),
        nodes=ProxmoxInventoryService.nodes(),
        execucoes=ProxmoxInventoryService.execucoes_recentes(),
        clientes=ProxmoxInventoryService.clientes(),
        selected_status=status or "",
        selected_node=node or "",
        pesquisa=pesquisa or "",
        integracoes_url=url_for("implantacao.integracoes_tecnicas"),
    )
