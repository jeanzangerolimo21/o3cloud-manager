from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from app.infraestrutura.agendamentos.service import ProxmoxAgendamentoService, STATUS_LABELS


proxmox_agendamentos_bp = Blueprint(
    "proxmox_agendamentos",
    __name__,
    url_prefix="/infraestrutura/agendamentos",
)


@proxmox_agendamentos_bp.route("")
def index():
    filtros = {
        "status": request.args.get("status") or "",
        "integracao_id": request.args.get("integracao_id") or "",
        "node": request.args.get("node") or "",
        "q": request.args.get("q") or "",
    }
    contexto = ProxmoxAgendamentoService.contexto_form()
    return render_template(
        "infraestrutura/agendamentos/index.html",
        agendamentos=ProxmoxAgendamentoService.listar(filtros),
        dashboard=ProxmoxAgendamentoService.dashboard(),
        filtros=filtros,
        status_options=STATUS_LABELS,
        clusters=contexto["clusters"],
        nodes=contexto["nodes"],
    )


@proxmox_agendamentos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    contexto = ProxmoxAgendamentoService.contexto_form()
    if request.method == "POST":
        try:
            agendamento_id = ProxmoxAgendamentoService.criar(request.form, _usuario_email())
            flash("Agendamento criado. A execução será feita pelo worker no horário configurado.", "success")
            return redirect(url_for("proxmox_agendamentos.visualizar", agendamento_id=agendamento_id))
        except ValueError as erro:
            flash(str(erro), "danger")
    return render_template(
        "infraestrutura/agendamentos/form.html",
        form=request.form,
        clusters=contexto["clusters"],
        nodes=contexto["nodes"],
        vms=contexto["vms"],
    )


@proxmox_agendamentos_bp.route("/vm/<int:inventario_id>/topologia")
def topologia_vm(inventario_id):
    try:
        return jsonify({"ok": True, "topologia": ProxmoxAgendamentoService.topologia_vm_live(inventario_id)})
    except ValueError as erro:
        return jsonify({"ok": False, "erro": str(erro)}), 400


@proxmox_agendamentos_bp.route("/<int:agendamento_id>")
def visualizar(agendamento_id):
    agendamento = ProxmoxAgendamentoService.buscar(agendamento_id)
    if not agendamento:
        flash("Agendamento não encontrado.", "warning")
        return redirect(url_for("proxmox_agendamentos.index"))
    return render_template(
        "infraestrutura/agendamentos/view.html",
        agendamento=agendamento,
        eventos=ProxmoxAgendamentoService.eventos(agendamento_id),
    )


@proxmox_agendamentos_bp.route("/<int:agendamento_id>/cancelar", methods=["POST"])
def cancelar(agendamento_id):
    try:
        ProxmoxAgendamentoService.cancelar(agendamento_id, _usuario_email())
        flash("Agendamento cancelado.", "success")
    except ValueError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("proxmox_agendamentos.visualizar", agendamento_id=agendamento_id))


def _usuario_email():
    return session.get("usuario_email") or session.get("email") or "sistema"
