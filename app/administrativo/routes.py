from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.administrativo.service import AdministrativoService
from app.core.auditoria import registrar_evento


administrativo_bp = Blueprint("administrativo", __name__, url_prefix="/administrativo")


def _usuario_email(): return session.get("usuario_email") or "sistema"
def _usuario_id(): return session.get("usuario_id")


@administrativo_bp.route("/")
def index():
    filtros = {"q": request.args.get("q"), "status": request.args.get("status"), "responsavel_id": request.args.get("responsavel_id"), "departamento_id": request.args.get("departamento_id")}
    contexto = AdministrativoService.contexto_index(filtros, _usuario_id())
    contexto.update(filtros=filtros, categorias=AdministrativoService.CATEGORIAS, prioridades=AdministrativoService.PRIORIDADES, status_options=AdministrativoService.STATUS)
    return render_template("administrativo/index.html", **contexto)


@administrativo_bp.route("/demandas/nova", methods=["GET", "POST"])
def nova_demanda():
    contexto = {"demanda": {"status": "PENDENTE", "permitir_comentarios": 1}, "usuarios": AdministrativoService.repository.listar_usuarios_ativos(), "departamentos": AdministrativoService.repository.listar_departamentos(), "categorias": AdministrativoService.CATEGORIAS, "prioridades": AdministrativoService.PRIORIDADES, "status_options": AdministrativoService.STATUS, "modo": "novo"}
    if request.method == "POST":
        try: demanda_id = AdministrativoService.criar(request.form, request.files.getlist("anexos"), _usuario_email())
        except (ValueError, OSError) as erro:
            flash(str(erro), "danger"); contexto["demanda"] = request.form; return render_template("administrativo/form.html", **contexto)
        registrar_evento("ADMIN_DEMANDA_CRIADA", "administrativo_demandas", demanda_id, {"titulo": request.form.get("titulo"), "responsavel_id": request.form.get("responsavel_id")})
        flash("Demanda criada.", "success"); return redirect(url_for("administrativo.detalhe", demanda_id=demanda_id))
    return render_template("administrativo/form.html", **contexto)


@administrativo_bp.route("/demandas/<int:demanda_id>")
def detalhe(demanda_id):
    demanda = AdministrativoService.detalhe(demanda_id)
    if not demanda: flash("Demanda não encontrada.", "danger"); return redirect(url_for("administrativo.index"))
    return render_template("administrativo/detalhe.html", demanda=demanda)


@administrativo_bp.route("/demandas/<int:demanda_id>/editar", methods=["GET", "POST"])
def editar(demanda_id):
    demanda = AdministrativoService.detalhe(demanda_id)
    if not demanda: flash("Demanda não encontrada.", "danger"); return redirect(url_for("administrativo.index"))
    contexto = {"demanda": demanda, "usuarios": AdministrativoService.repository.listar_usuarios_ativos(), "departamentos": AdministrativoService.repository.listar_departamentos(), "categorias": AdministrativoService.CATEGORIAS, "prioridades": AdministrativoService.PRIORIDADES, "status_options": AdministrativoService.STATUS, "modo": "editar"}
    if request.method == "POST":
        try: AdministrativoService.atualizar(demanda_id, request.form, request.files.getlist("anexos"), _usuario_email())
        except (ValueError, OSError) as erro:
            flash(str(erro), "danger"); contexto["demanda"] = {**demanda, **request.form}; return render_template("administrativo/form.html", **contexto)
        registrar_evento("ADMIN_DEMANDA_ATUALIZADA", "administrativo_demandas", demanda_id, {"titulo": request.form.get("titulo"), "status": request.form.get("status")})
        flash("Demanda atualizada.", "success"); return redirect(url_for("administrativo.detalhe", demanda_id=demanda_id))
    return render_template("administrativo/form.html", **contexto)


@administrativo_bp.route("/demandas/<int:demanda_id>/cancelar", methods=["POST"])
def cancelar(demanda_id):
    try: AdministrativoService.cancelar(demanda_id, _usuario_email())
    except ValueError as erro: flash(str(erro), "danger")
    else: registrar_evento("ADMIN_DEMANDA_CANCELADA", "administrativo_demandas", demanda_id); flash("Demanda cancelada.", "success")
    return redirect(url_for("administrativo.detalhe", demanda_id=demanda_id))


@administrativo_bp.route("/demandas/<int:demanda_id>/comentarios", methods=["POST"])
def comentar(demanda_id):
    try: AdministrativoService.comentar(demanda_id, request.form.get("comentario"), request.files.getlist("anexos"), _usuario_email())
    except (ValueError, OSError) as erro: flash(str(erro), "danger")
    else: registrar_evento("ADMIN_COMENTARIO_CRIADO", "administrativo_comentarios", demanda_id); flash("Comentário registrado.", "success")
    return redirect(url_for("administrativo.detalhe", demanda_id=demanda_id))


@administrativo_bp.route("/agenda")
def agenda():
    usuario_id = request.args.get("usuario_id", type=int) if session.get("usuario_perfil") in ("ADMIN", "DIRETORIA", "GESTOR") else _usuario_id()
    return render_template("administrativo/agenda.html", demandas=AdministrativoService.repository.listar_agenda(usuario_id), usuarios=AdministrativoService.repository.listar_usuarios_ativos(), usuario_id=usuario_id)


@administrativo_bp.route("/notificacoes")
def notificacoes():
    return render_template("administrativo/notificacoes.html", notificacoes=AdministrativoService.notificar_pendencias(_usuario_id()))


@administrativo_bp.route("/notificacoes/<int:notificacao_id>/ler", methods=["POST"])
def ler_notificacao(notificacao_id):
    AdministrativoService.marcar_notificacao(notificacao_id, _usuario_id()); return redirect(request.referrer or url_for("administrativo.notificacoes"))


@administrativo_bp.route("/relatorios")
def relatorios():
    usuario_id = None if session.get("usuario_perfil") in ("ADMIN", "DIRETORIA", "GESTOR") else _usuario_id()
    return render_template("administrativo/relatorios.html", dashboard=AdministrativoService.repository.dashboard(usuario_id), linhas=AdministrativoService.repository.relatorio(usuario_id))
