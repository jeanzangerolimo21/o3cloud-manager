from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.administrativo.aso_service import AdministrativoAsoService
from app.administrativo.service import AdministrativoService
from app.core.auditoria import registrar_evento


administrativo_bp = Blueprint("administrativo", __name__, url_prefix="/administrativo")


def _usuario_email(): return session.get("usuario_email") or "sistema"
def _usuario_id(): return session.get("usuario_id")
def _colaborador(): return session.get("usuario_perfil") == "ADMINISTRATIVO_COLABORADOR"
def _agenda_corporativa(): return session.get("usuario_perfil") in ("ADMIN", "DIRETORIA", "ADMINISTRATIVO_GESTOR")
def _possui_agenda(): return bool(session.get("usuario_possui_agenda"))
def _moderador(): return session.get("usuario_perfil") in ("ADMIN", "DIRETORIA", "GESTOR", "ADMINISTRATIVO_GESTOR")
def _pode_excluir_demanda(): return session.get("usuario_perfil") in ("ADMIN", "DIRETORIA", "ADMINISTRATIVO_GESTOR")
def _pode_excluir_agendamento_aso(): return session.get("usuario_perfil") in ("ADMIN", "ADMINISTRATIVO_GESTOR")


@administrativo_bp.route("/")
def index():
    if _colaborador() or (_possui_agenda() and not _agenda_corporativa()):
        return redirect(url_for("administrativo.agenda"))
    filtros = {"q": request.args.get("q"), "status": request.args.get("status"), "responsavel_id": request.args.get("responsavel_id"), "departamento_id": request.args.get("departamento_id")}
    if _colaborador():
        filtros["responsavel_id"] = _usuario_id()
    contexto = AdministrativoService.contexto_index(filtros, _usuario_id())
    contexto.update(filtros=filtros, categorias=AdministrativoService.CATEGORIAS, prioridades=AdministrativoService.PRIORIDADES, status_options=AdministrativoService.STATUS)
    return render_template("administrativo/index.html", **contexto)


@administrativo_bp.route("/aso")
def aso():
    filtros = {"q": request.args.get("q"), "cliente_id": request.args.get("cliente_id"), "status": request.args.get("status")}
    return render_template("administrativo/aso/index.html", **AdministrativoAsoService.contexto_index(filtros, _usuario_id()))


@administrativo_bp.route("/aso/colaboradores/novo", methods=["GET", "POST"])
def novo_colaborador_aso():
    contexto = AdministrativoAsoService.contexto_index(usuario_id=_usuario_id())
    contexto.update(colaborador={"status": "ATIVO"}, modo="novo")
    if request.method == "POST":
        try:
            resultado = AdministrativoAsoService.criar_colaborador(request.form, request.files.getlist("exames"), _usuario_email())
        except (ValueError, OSError) as erro:
            flash(str(erro), "danger")
            contexto["colaborador"] = request.form
            return render_template("administrativo/aso/form.html", **contexto)
        colaborador_id = resultado["colaborador_id"]
        registrar_evento("ADMIN_ASO_COLABORADOR_CRIADO", "administrativo_aso_colaboradores", colaborador_id, {"nome": request.form.get("nome_completo"), "demandas": resultado.get("demanda_ids", [])})
        flash("Colaborador ASO cadastrado com agendamento na agenda." if resultado.get("demanda_ids") else "Colaborador ASO cadastrado.", "success")
        return redirect(url_for("administrativo.detalhe_colaborador_aso", colaborador_id=colaborador_id))
    return render_template("administrativo/aso/form.html", **contexto)


@administrativo_bp.route("/aso/colaboradores/<int:colaborador_id>")
def detalhe_colaborador_aso(colaborador_id):
    colaborador = AdministrativoAsoService.detalhe_colaborador(colaborador_id)
    if not colaborador:
        flash("Colaborador ASO não encontrado.", "danger")
        return redirect(url_for("administrativo.aso"))
    contexto = AdministrativoAsoService.contexto_index(usuario_id=_usuario_id())
    contexto["colaborador"] = colaborador
    contexto["pode_excluir_agendamento_aso"] = _pode_excluir_agendamento_aso()
    return render_template("administrativo/aso/detalhe.html", **contexto)


@administrativo_bp.route("/aso/colaboradores/<int:colaborador_id>/editar", methods=["GET", "POST"])
def editar_colaborador_aso(colaborador_id):
    colaborador = AdministrativoAsoService.detalhe_colaborador(colaborador_id)
    if not colaborador:
        flash("Colaborador ASO não encontrado.", "danger")
        return redirect(url_for("administrativo.aso"))
    contexto = AdministrativoAsoService.contexto_index(usuario_id=_usuario_id())
    contexto.update(colaborador=colaborador, modo="editar")
    if request.method == "POST":
        try:
            AdministrativoAsoService.atualizar_colaborador(colaborador_id, request.form, request.files.getlist("exames"), _usuario_email())
        except (ValueError, OSError) as erro:
            flash(str(erro), "danger")
            contexto["colaborador"] = {**colaborador, **request.form}
            return render_template("administrativo/aso/form.html", **contexto)
        registrar_evento("ADMIN_ASO_COLABORADOR_ATUALIZADO", "administrativo_aso_colaboradores", colaborador_id, {"nome": request.form.get("nome_completo")})
        flash("Colaborador ASO atualizado.", "success")
        return redirect(url_for("administrativo.detalhe_colaborador_aso", colaborador_id=colaborador_id))
    return render_template("administrativo/aso/form.html", **contexto)


@administrativo_bp.route("/aso/colaboradores/<int:colaborador_id>/excluir", methods=["POST"])
def excluir_colaborador_aso(colaborador_id):
    if not _pode_excluir_demanda():
        flash("Apenas Administrador, Diretoria ou Gestor Administrativo podem excluir colaboradores ASO.", "danger")
        return redirect(url_for("administrativo.detalhe_colaborador_aso", colaborador_id=colaborador_id))
    try:
        AdministrativoAsoService.excluir_colaborador(colaborador_id, _usuario_email())
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(url_for("administrativo.detalhe_colaborador_aso", colaborador_id=colaborador_id))
    else:
        registrar_evento("ADMIN_ASO_COLABORADOR_EXCLUIDO", "administrativo_aso_colaboradores", colaborador_id)
        flash("Colaborador ASO excluído.", "success")
        return redirect(url_for("administrativo.aso"))

@administrativo_bp.route("/aso/colaboradores/<int:colaborador_id>/lembretes", methods=["POST"])
def criar_lembrete_aso(colaborador_id):
    try:
        demanda_ids = AdministrativoAsoService.criar_lembrete(colaborador_id, request.form, _usuario_email())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        registrar_evento("ADMIN_ASO_LEMBRETE_CRIADO", "administrativo_aso_lembretes", colaborador_id, {"demandas": demanda_ids})
        flash("Lembrete ASO criado na agenda.", "success")
    return redirect(url_for("administrativo.detalhe_colaborador_aso", colaborador_id=colaborador_id))


@administrativo_bp.route("/aso/colaboradores/<int:colaborador_id>/exames", methods=["POST"])
def anexar_exames_aso(colaborador_id):
    try:
        AdministrativoAsoService.anexar_exames(colaborador_id, request.files.getlist("exames"))
    except (ValueError, OSError) as erro:
        flash(str(erro), "danger")
    else:
        registrar_evento("ADMIN_ASO_EXAMES_ANEXADOS", "administrativo_aso_exames", colaborador_id)
        flash("Arquivo(s) anexado(s).", "success")
    return redirect(url_for("administrativo.detalhe_colaborador_aso", colaborador_id=colaborador_id))


@administrativo_bp.route("/aso/colaboradores/<int:colaborador_id>/exames/<int:exame_id>/excluir", methods=["POST"])
def excluir_exame_aso(colaborador_id, exame_id):
    if not _pode_excluir_demanda():
        flash("Apenas Administrador, Diretoria ou Gestor Administrativo podem excluir arquivos ASO.", "danger")
        return redirect(url_for("administrativo.detalhe_colaborador_aso", colaborador_id=colaborador_id))
    try:
        AdministrativoAsoService.excluir_exame(colaborador_id, exame_id)
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        registrar_evento("ADMIN_ASO_EXAME_EXCLUIDO", "administrativo_aso_exames", exame_id, {"colaborador_id": colaborador_id})
        flash("Arquivo excluído.", "success")
    return redirect(url_for("administrativo.detalhe_colaborador_aso", colaborador_id=colaborador_id))


@administrativo_bp.route("/aso/colaboradores/<int:colaborador_id>/lembretes/<int:lembrete_id>/excluir", methods=["POST"])
def excluir_lembrete_aso(colaborador_id, lembrete_id):
    if not _pode_excluir_agendamento_aso():
        flash("Apenas Administrador ou Gestor Administrativo podem excluir agendamentos ASO.", "danger")
        return redirect(url_for("administrativo.detalhe_colaborador_aso", colaborador_id=colaborador_id))
    try:
        AdministrativoAsoService.excluir_lembrete(colaborador_id, lembrete_id, _usuario_email())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        registrar_evento("ADMIN_ASO_LEMBRETE_EXCLUIDO", "administrativo_aso_lembretes", lembrete_id, {"colaborador_id": colaborador_id})
        flash("Agendamento ASO excluído.", "success")
    return redirect(url_for("administrativo.detalhe_colaborador_aso", colaborador_id=colaborador_id))


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
    if demanda and _colaborador() and int(demanda.get("responsavel_id") or 0) != int(_usuario_id() or 0):
        demanda = None
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
    if not _pode_excluir_demanda():
        flash("Apenas Administrador, Diretoria ou Gestor Administrativo podem excluir demandas.", "danger")
        return redirect(request.referrer or url_for("administrativo.index"))
    try: AdministrativoService.cancelar(demanda_id, _usuario_email())
    except ValueError as erro: flash(str(erro), "danger")
    else: registrar_evento("ADMIN_DEMANDA_CANCELADA", "administrativo_demandas", demanda_id); flash("Demanda excluída.", "success")
    return redirect(request.referrer or url_for("administrativo.index"))


@administrativo_bp.route("/demandas/<int:demanda_id>/comentarios", methods=["POST"])
def comentar(demanda_id):
    try: AdministrativoService.comentar(demanda_id, request.form.get("comentario"), request.files.getlist("anexos"), _usuario_email(), _usuario_id(), _colaborador())
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
    gestor = _agenda_corporativa()
    usuario_id = request.args.get("usuario_id", type=int) if gestor else _usuario_id()
    visao = request.args.get("visao", "hoje")
    if visao not in ("hoje", "semana", "mes", "lista"):
        visao = "hoje"
    formato = request.args.get("formato", "lista")
    if formato not in ("lista", "calendario"):
        formato = "lista"
    referencia = _data_query(request.args.get("data")) or date.today()
    inicio, fim = _intervalo_agenda(visao, referencia)
    if visao == "semana" and inicio:
        dias_semana = [inicio + timedelta(days=indice) for indice in range(5)]
    elif visao == "mes" and inicio and fim:
        primeiro = inicio - timedelta(days=inicio.weekday())
        ultimo = fim + timedelta(days=6 - fim.weekday())
        dias_semana = [primeiro + timedelta(days=indice) for indice in range((ultimo - primeiro).days + 1)]
    elif visao == "hoje" and inicio:
        dias_semana = [inicio]
    else:
        dias_semana = []
    demandas = AdministrativoService.repository.listar_agenda(usuario_id, inicio, fim)
    demandas_por_dia = {}
    for item in demandas:
        data_agenda = item.get("data_inicial") or item.get("data_limite")
        chave = data_agenda.isoformat()[:10] if hasattr(data_agenda, "isoformat") else str(data_agenda or "")[:10]
        if chave:
            demandas_por_dia.setdefault(chave, []).append(item)
    return render_template("administrativo/agenda.html", demandas=demandas, usuarios=AdministrativoService.repository.listar_usuarios_ativos(), usuario_id=usuario_id, gestor=gestor, visao=visao, formato=formato, referencia=referencia, data_inicio=inicio, data_fim=fim, dias_semana=dias_semana, demandas_por_dia=demandas_por_dia)

@administrativo_bp.route("/demandas/<int:demanda_id>/reagendar", methods=["POST"])
def reagendar(demanda_id):
    demanda = AdministrativoService.detalhe(demanda_id)
    if not demanda:
        flash("Demanda não encontrada.", "danger")
        return redirect(url_for("administrativo.agenda"))
    dados = {"titulo": demanda.get("titulo"), "descricao": demanda.get("descricao"), "categoria": demanda.get("categoria"), "prioridade": demanda.get("prioridade"), "responsavel_id": demanda.get("responsavel_id"), "departamento_id": demanda.get("departamento_id"), "data_inicial": demanda.get("data_inicial"), "data_limite": request.form.get("data_limite"), "hora": demanda.get("hora"), "status": demanda.get("status"), "observacoes": demanda.get("observacoes"), "permitir_comentarios": demanda.get("permitir_comentarios"), "recorrente": demanda.get("recorrente"), "recorrencia_tipo": demanda.get("recorrencia_tipo"), "recorrencia_dia_semana": demanda.get("recorrencia_dia_semana"), "recorrencia_dia_mes": demanda.get("recorrencia_dia_mes"), "recorrencia_mes": demanda.get("recorrencia_mes"), "recorrencia_data_fim": demanda.get("recorrencia_data_fim")}
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
        return inicio, inicio + timedelta(days=4)
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
    AdministrativoService.marcar_notificacao(notificacao_id, _usuario_id()); registrar_evento("ADMIN_NOTIFICACAO_LIDA", "administrativo_notificacoes", notificacao_id); return redirect(request.referrer or url_for("administrativo.notificacoes"))


@administrativo_bp.route("/notificacoes/ler-todas", methods=["POST"])
def ler_todas_notificacoes():
    AdministrativoService.marcar_notificacoes(_usuario_id())
    registrar_evento("ADMIN_NOTIFICACOES_LIDAS", "administrativo_notificacoes", None, {"usuario_id": _usuario_id()})
    flash("Notificações marcadas como lidas.", "success")
    return redirect(request.referrer or url_for("administrativo.notificacoes"))


@administrativo_bp.route("/relatorios")
def relatorios():
    usuario_id = None if session.get("usuario_perfil") in ("ADMIN", "DIRETORIA", "ADMINISTRATIVO_GESTOR") else _usuario_id()
    inicio = request.args.get("data_inicio") or None
    fim = request.args.get("data_fim") or None
    return render_template("administrativo/relatorios.html", dashboard=AdministrativoService.repository.dashboard_completo(usuario_id), linhas=AdministrativoService.repository.relatorio_periodo(usuario_id, inicio, fim), data_inicio=inicio, data_fim=fim)
