from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.administrativo.service import AdministrativoService
from app.core.auditoria import registrar_evento


administrativo_bp = Blueprint("administrativo", __name__, url_prefix="/administrativo")


def _usuario_email(): return session.get("usuario_email") or "sistema"
def _usuario_id(): return session.get("usuario_id")
def _moderador(): return session.get("usuario_perfil") in ("ADMIN", "DIRETORIA", "GESTOR")


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

@administrativo_bp.route("/demandas/<int:demanda_id>/comentarios/<int:comentario_id>/editar", methods=["POST"])
def editar_comentario(demanda_id, comentario_id):
    try: AdministrativoService.editar_comentario(demanda_id, comentario_id, request.form.get("comentario"), _usuario_email(), _moderador())
    except ValueError as erro: flash(str(erro), "danger")
    else: registrar_evento("ADMIN_COMENTARIO_EDITADO", "administrativo_comentarios", comentario_id, {"demanda_id": demanda_id}); flash("Comentário atualizado.", "success")
    return redirect(url_for("administrativo.detalhe", demanda_id=demanda_id))

@administrativo_bp.route("/demandas/<int:demanda_id>/comentarios/<int:comentario_id>/excluir", methods=["POST"])
def excluir_comentario(demanda_id, comentario_id):
    try: AdministrativoService.excluir_comentario(demanda_id, comentario_id, _usuario_email(), _moderador())
    except ValueError as erro: flash(str(erro), "danger")
    else: registrar_evento("ADMIN_COMENTARIO_INATIVADO", "administrativo_comentarios", comentario_id, {"demanda_id": demanda_id}); flash("Comentário inativado.", "success")
    return redirect(url_for("administrativo.detalhe", demanda_id=demanda_id))


@administrativo_bp.route("/agenda")
def agenda():
    gestor = session.get("usuario_perfil") in ("ADMIN", "DIRETORIA", "GESTOR")
    usuario_id = request.args.get("usuario_id", type=int) if gestor else _usuario_id()
    visao = request.args.get("visao", "hoje")
    if visao not in ("hoje", "semana", "mes", "lista"):
        visao = "hoje"
    referencia = _data_query(request.args.get("data")) or date.today()
    inicio, fim = _intervalo_agenda(visao, referencia)
    return render_template("administrativo/agenda.html", demandas=AdministrativoService.repository.listar_agenda(usuario_id, inicio, fim), usuarios=AdministrativoService.repository.listar_usuarios_ativos(), usuario_id=usuario_id, gestor=gestor, visao=visao, referencia=referencia, data_inicio=inicio, data_fim=fim)

@administrativo_bp.route("/demandas/<int:demanda_id>/reagendar", methods=["POST"])
def reagendar(demanda_id):
    demanda = AdministrativoService.detalhe(demanda_id)
    if not demanda:
        flash("Demanda não encontrada.", "danger")
        return redirect(url_for("administrativo.agenda"))
    dados = {"titulo": demanda.get("titulo"), "descricao": demanda.get("descricao"), "categoria": demanda.get("categoria"), "prioridade": demanda.get("prioridade"), "responsavel_id": demanda.get("responsavel_id"), "departamento_id": demanda.get("departamento_id"), "data_inicial": demanda.get("data_inicial"), "data_limite": request.form.get("data_limite"), "hora": demanda.get("hora"), "status": demanda.get("status"), "observacoes": demanda.get("observacoes"), "permitir_comentarios": demanda.get("permitir_comentarios")}
    try:
        AdministrativoService.atualizar(demanda_id, dados, [], _usuario_email())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        registrar_evento("ADMIN_DEMANDA_REAGENDADA", "administrativo_demandas", demanda_id, {"data_limite": request.form.get("data_limite")})
        flash("Demanda reagendada.", "success")
    return redirect(request.referrer or url_for("administrativo.agenda"))


def _data_query(valor):
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return None


def _intervalo_agenda(visao, referencia):
    if visao == "hoje":
        return referencia, referencia
    if visao == "semana":
        inicio = referencia - timedelta(days=referencia.weekday())
        return inicio, inicio + timedelta(days=6)
    if visao == "mes":
        inicio = referencia.replace(day=1)
        proximo = inicio.replace(year=inicio.year + 1, month=1) if inicio.month == 12 else inicio.replace(month=inicio.month + 1)
        return inicio, proximo - timedelta(days=1)
    return None, None

@administrativo_bp.route("/notificacoes")
def notificacoes():
    return render_template("administrativo/notificacoes.html", notificacoes=AdministrativoService.notificar_pendencias(_usuario_id()))


@administrativo_bp.route("/notificacoes/<int:notificacao_id>/ler", methods=["POST"])
def ler_notificacao(notificacao_id):
    AdministrativoService.marcar_notificacao(notificacao_id, _usuario_id()); return redirect(request.referrer or url_for("administrativo.notificacoes"))


@administrativo_bp.route("/notificacoes/ler-todas", methods=["POST"])
def ler_todas_notificacoes():
    AdministrativoService.marcar_notificacoes(_usuario_id())
    flash("Notificações marcadas como lidas.", "success")
    return redirect(request.referrer or url_for("administrativo.notificacoes"))


@administrativo_bp.route("/relatorios")
def relatorios():
    usuario_id = None if session.get("usuario_perfil") in ("ADMIN", "DIRETORIA", "GESTOR") else _usuario_id()
    inicio = request.args.get("data_inicio") or None
    fim = request.args.get("data_fim") or None
    return render_template("administrativo/relatorios.html", dashboard=AdministrativoService.repository.dashboard_completo(usuario_id), linhas=AdministrativoService.repository.relatorio_periodo(usuario_id, inicio, fim), data_inicio=inicio, data_fim=fim)
