from flask import Blueprint, Response, flash, redirect, render_template, request, session, url_for

from app.core.access_control import pode_editar
from app.relatorios.service import RelatorioService


relatorios_bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")


@relatorios_bp.route("/")
def index():
    usuario = _usuario()
    return render_template("relatorios/index.html", **RelatorioService.contexto(usuario.get("id"), session.get("usuario_perfil")))


@relatorios_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        acao = request.form.get("acao")
        try:
            if acao == "segundo_plano":
                job_id = RelatorioService.solicitar_job(request.form, _usuario())
                flash(f"Relatório extenso solicitado. Você receberá um link por e-mail quando o job #{job_id} for concluído.", "info")
                return redirect(url_for("relatorios.index"))
            RelatorioService.validar_execucao_sincrona(request.form, limite=500)
            resultado = RelatorioService.executar(request.form, _usuario(), limite=500)
            if acao == "salvar":
                if not pode_editar("relatorios"):
                    flash("Seu perfil pode executar relatórios, mas não pode salvar modelos.", "danger")
                else:
                    modelo_id = RelatorioService.salvar_modelo(request.form, _usuario())
                    flash("Modelo de relatório salvo.", "success")
                    return redirect(url_for("relatorios.visualizar_modelo", modelo_id=modelo_id))
        except ValueError as erro:
            flash(str(erro), "danger")
            resultado = None
        return render_template("relatorios/form.html", resultado=resultado, form=request.form, modelo=None, **RelatorioService.contexto(_usuario().get("id"), session.get("usuario_perfil")))
    return render_template("relatorios/form.html", resultado=None, form={}, modelo=None, **RelatorioService.contexto(_usuario().get("id"), session.get("usuario_perfil")))


@relatorios_bp.route("/modelos/<int:modelo_id>", methods=["GET", "POST"])
def visualizar_modelo(modelo_id):
    modelo = RelatorioService.buscar_modelo(modelo_id)
    if not modelo:
        flash("Modelo de relatório não encontrado.", "danger")
        return redirect(url_for("relatorios.index"))
    dados = request.form if request.method == "POST" else _config_para_form(modelo)
    if request.method == "POST" and request.form.get("acao") == "salvar":
        if not pode_editar("relatorios"):
            flash("Acesso não autorizado para editar modelos.", "danger")
        else:
            try:
                RelatorioService.salvar_modelo(request.form, _usuario(), modelo_id=modelo_id)
                flash("Modelo atualizado.", "success")
                return redirect(url_for("relatorios.visualizar_modelo", modelo_id=modelo_id))
            except ValueError as erro:
                flash(str(erro), "danger")
    try:
        if request.method == "POST" and request.form.get("acao") == "segundo_plano":
            job_id = RelatorioService.solicitar_job(request.form, _usuario(), modelo_id=modelo_id)
            flash(f"Relatório extenso solicitado. Você receberá um link por e-mail quando o job #{job_id} for concluído.", "info")
            return redirect(url_for("relatorios.index"))
        RelatorioService.validar_execucao_sincrona(dados, limite=500)
        resultado = RelatorioService.executar(dados, _usuario(), modelo_id=modelo_id, limite=500)
    except ValueError as erro:
        flash(str(erro), "danger")
        resultado = None
    return render_template("relatorios/form.html", resultado=resultado, form=dados, modelo=modelo, **RelatorioService.contexto(_usuario().get("id"), session.get("usuario_perfil")))


@relatorios_bp.route("/modelos/<int:modelo_id>/salvar", methods=["POST"])
def salvar_modelo(modelo_id):
    if not pode_editar("relatorios"):
        flash("Acesso não autorizado para editar modelos.", "danger")
        return redirect(url_for("relatorios.visualizar_modelo", modelo_id=modelo_id))
    try:
        RelatorioService.salvar_modelo(request.form, _usuario(), modelo_id=modelo_id)
        flash("Modelo atualizado.", "success")
    except ValueError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("relatorios.visualizar_modelo", modelo_id=modelo_id))


@relatorios_bp.route("/modelos/<int:modelo_id>/excluir", methods=["POST"])
def excluir_modelo(modelo_id):
    if not pode_editar("relatorios"):
        flash("Acesso não autorizado para excluir modelos.", "danger")
        return redirect(url_for("relatorios.index"))
    RelatorioService.repository.excluir_modelo(modelo_id, _usuario().get("email"))
    flash("Modelo removido.", "success")
    return redirect(url_for("relatorios.index"))


@relatorios_bp.route("/segundo-plano/<formato>", methods=["POST"])
def solicitar_exportacao(formato):
    if formato not in ("csv", "xlsx", "docx", "pdf"):
        flash("Formato de exportação inválido.", "danger")
        return redirect(url_for("relatorios.novo"))
    try:
        job_id = RelatorioService.solicitar_job(request.form, _usuario(), formato=formato.upper())
        flash(f"Relatório extenso solicitado. Você receberá um link por e-mail quando o job #{job_id} for concluído.", "info")
    except ValueError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("relatorios.index"))


@relatorios_bp.route("/exportar/<formato>", methods=["POST"])
def exportar(formato):
    try:
        RelatorioService.validar_execucao_sincrona(request.form, limite=5000)
        resultado = RelatorioService.executar(request.form, _usuario(), limite=5000, formato=formato.upper())
    except ValueError as erro:
        flash(str(erro), "warning")
        return redirect(url_for("relatorios.novo"))
    nome = "relatorio_o3cloud"
    if formato == "csv":
        return Response(RelatorioService.exportar_csv(resultado), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={nome}.csv"})
    if formato == "xlsx":
        return Response(RelatorioService.exportar_xlsx(resultado, _usuario().get("email")), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename={nome}.xlsx"})
    if formato == "docx":
        return Response(RelatorioService.exportar_docx(resultado, _usuario().get("email")), mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": f"attachment; filename={nome}.docx"})
    if formato == "pdf":
        return Response(RelatorioService.exportar_pdf(resultado, _usuario().get("email")), mimetype="application/pdf", headers={"Content-Disposition": f"attachment; filename={nome}.pdf"})
    flash("Formato de exportação inválido.", "danger")
    return redirect(url_for("relatorios.novo"))


def _usuario():
    return {
        "id": session.get("usuario_id"),
        "email": session.get("usuario_email") or session.get("email") or session.get("login_email"),
    }


def _config_para_form(modelo):
    config = modelo.get("configuracao") or {}
    class FormDict(dict):
        def getlist(self, key):
            valor = self.get(key, [])
            return valor if isinstance(valor, list) else [valor]
    dados = FormDict(config)
    dados["nome"] = modelo.get("nome")
    dados["descricao"] = modelo.get("descricao")
    dados["visibilidade"] = modelo.get("visibilidade")
    dados["perfis"] = ",".join(modelo.get("perfis") or [])
    dados["ordem_campo"] = (config.get("ordenacao") or {}).get("campo")
    dados["ordem_direcao"] = (config.get("ordenacao") or {}).get("direcao")
    dados["filtro_campo"] = [f.get("campo") for f in config.get("filtros", [])]
    dados["filtro_operador"] = [f.get("operador") for f in config.get("filtros", [])]
    dados["filtro_valor"] = [f.get("valor") for f in config.get("filtros", [])]
    dados["filtro_valor_final"] = [f.get("valor_final") for f in config.get("filtros", [])]
    dados["agregacao_campo"] = [a.get("campo") for a in config.get("agregacoes", [])]
    dados["agregacao_funcao"] = [a.get("funcao") for a in config.get("agregacoes", [])]
    return dados
