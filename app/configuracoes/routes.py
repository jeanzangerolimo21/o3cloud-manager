from flask import Blueprint
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import send_file
from flask import request
from flask import session
from flask import url_for

from app.configuracoes.auth_service import AuthConfigService
from app.configuracoes.backup_service import BackupSistemaService
from app.configuracoes.cache_service import CacheRetencaoService
from app.configuracoes.email_service import EmailConfigService
from app.configuracoes.sincronismos_service import SincronismosAgendadosService


configuracoes_bp = Blueprint("configuracoes", __name__, url_prefix="/configuracoes")


def _email_usuario_logado():
    return session.get("usuario_email") or session.get("email") or "sistema"


@configuracoes_bp.route("/usuarios/perfis/novo", methods=["GET", "POST"])
def usuarios_perfil_novo():
    if request.method == "POST":
        try:
            perfil_id = AuthConfigService.criar_perfil(request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template(
                "configuracoes/usuarios/perfil_form.html",
                perfil={**request.form, "permissoes": request.form.getlist("menu_keys")},
                grupos_menus=AuthConfigService.menus_por_grupo(),
                dashboards_principais=AuthConfigService.DASHBOARDS_PRINCIPAIS,
                modo="novo",
                admin_bloqueado=False,
            )
        flash("Perfil cadastrado.", "success")
        return redirect(url_for("configuracoes.usuarios_perfil_editar", perfil_id=perfil_id))
    return render_template(
        "configuracoes/usuarios/perfil_form.html",
        perfil=AuthConfigService.novo_perfil_payload(),
        grupos_menus=AuthConfigService.menus_por_grupo(),
        dashboards_principais=AuthConfigService.DASHBOARDS_PRINCIPAIS,
        modo="novo",
        admin_bloqueado=False,
    )


@configuracoes_bp.route("/usuarios/perfis/<int:perfil_id>/editar", methods=["GET", "POST"])
def usuarios_perfil_editar(perfil_id):
    perfil = AuthConfigService.buscar_perfil(perfil_id)
    if not perfil:
        flash("Perfil não encontrado.", "danger")
        return redirect(url_for("configuracoes.usuarios_index"))
    admin_bloqueado = perfil.get("codigo") == "ADMIN"
    if request.method == "POST":
        try:
            AuthConfigService.atualizar_perfil(perfil_id, request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            perfil = {**perfil, **request.form, "permissoes": request.form.getlist("menu_keys")}
        else:
            flash("Perfil atualizado.", "success")
            return redirect(url_for("configuracoes.usuarios_index"))
    return render_template(
        "configuracoes/usuarios/perfil_form.html",
        perfil=perfil,
        grupos_menus=AuthConfigService.menus_por_grupo(),
        modo="editar",
        admin_bloqueado=admin_bloqueado,
        dashboards_principais=AuthConfigService.DASHBOARDS_PRINCIPAIS,
    )


@configuracoes_bp.route("/usuarios")
def usuarios_index():
    contexto = AuthConfigService.dashboard()
    return render_template(
        "configuracoes/usuarios/index.html",
        **contexto,
        page_title="Usuários e Acessos",
        page_description="Gestão de usuários, perfis, convites e permissões. Provedores externos ficam em Integrações Técnicas.",
        page_icon="bi-person-gear",
        page_button_text="Novo Usuário",
        page_button_icon="bi-person-plus",
        page_button_url=url_for("configuracoes.usuarios_novo"),
    )


@configuracoes_bp.route("/usuarios/novo", methods=["GET", "POST"])
def usuarios_novo():
    perfis = AuthConfigService.repository.listar_perfis()
    if request.method == "POST":
        try:
            usuario_id = AuthConfigService.criar_usuario(request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("configuracoes/usuarios/form.html", usuario=request.form, perfis=perfis, modo="novo")
        flash("Usuário cadastrado. Convite por e-mail é enviado apenas para usuário Local com status Convidado.", "success")
        return redirect(url_for("configuracoes.usuarios_editar", usuario_id=usuario_id))
    return render_template("configuracoes/usuarios/form.html", usuario=AuthConfigService.novo_usuario_payload(), perfis=perfis, modo="novo")


@configuracoes_bp.route("/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
def usuarios_editar(usuario_id):
    usuario = AuthConfigService.buscar_usuario(usuario_id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("configuracoes.usuarios_index"))
    perfis = AuthConfigService.repository.listar_perfis()
    if request.method == "POST":
        try:
            AuthConfigService.atualizar_usuario(usuario_id, request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            usuario = {**usuario, **request.form}
        else:
            flash("Usuário atualizado.", "success")
            return redirect(url_for("configuracoes.usuarios_index"))
    return render_template("configuracoes/usuarios/form.html", usuario=usuario, perfis=perfis, modo="editar")


@configuracoes_bp.route("/usuarios/<int:usuario_id>/remover", methods=["POST"])
def usuarios_remover(usuario_id):
    try:
        AuthConfigService.remover_usuario(
            usuario_id,
            usuario_logado_id=session.get("usuario_id"),
            perfil_logado=session.get("usuario_perfil"),
            usuario_email=_email_usuario_logado(),
        )
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Usuário removido.", "success")
    return redirect(url_for("configuracoes.usuarios_index"))

@configuracoes_bp.route("/usuarios/<int:usuario_id>/convidar", methods=["POST"])
def usuarios_convidar(usuario_id):
    try:
        resultado = AuthConfigService.enviar_convite(usuario_id, _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        envio = resultado.get("email_resultado") or {}
        if envio.get("enviado"):
            flash("Convite enviado para {}.".format(resultado.get("email")), "success")
        else:
            motivo = envio.get("motivo") or "SMTP indisponível"
            flash("Convite gerado, mas o e-mail não foi enviado ({}).".format(motivo), "warning")
    return redirect(request.referrer or url_for("configuracoes.usuarios_index"))


@configuracoes_bp.route("/usuarios/convite/<token>", methods=["GET", "POST"])
def usuarios_aceitar_convite(token):
    convite = AuthConfigService.buscar_convite(token)
    if request.method == "POST":
        try:
            AuthConfigService.aceitar_convite(token, request.form.get("senha"), request.form.get("confirmacao_senha"))
        except ValueError as erro:
            flash(str(erro), "danger")
        else:
            flash("Senha cadastrada. Seu usuário está ativo.", "success")
            return redirect(url_for("configuracoes.usuarios_aceitar_convite", token=token))
    return render_template("configuracoes/usuarios/convite.html", convite=convite)


@configuracoes_bp.route("/usuarios/grupos/novo", methods=["GET", "POST"])
def usuarios_grupo_mapa_novo():
    perfis = AuthConfigService.repository.listar_perfis()
    integracoes_identidade = AuthConfigService.repository.listar_integracoes_identidade()
    if request.method == "POST":
        try:
            AuthConfigService.criar_grupo_perfil_mapa(request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template(
                "configuracoes/usuarios/grupo_mapa_form.html",
                mapa=request.form,
                perfis=perfis,
                integracoes_identidade=integracoes_identidade,
                modo="novo",
            )
        flash("Mapeamento de grupo externo cadastrado.", "success")
        return redirect(url_for("configuracoes.usuarios_index"))
    return render_template(
        "configuracoes/usuarios/grupo_mapa_form.html",
        mapa=AuthConfigService.novo_grupo_perfil_mapa_payload(),
        perfis=perfis,
        integracoes_identidade=integracoes_identidade,
        modo="novo",
    )


@configuracoes_bp.route("/usuarios/grupos/<int:mapa_id>/editar", methods=["GET", "POST"])
def usuarios_grupo_mapa_editar(mapa_id):
    mapa = AuthConfigService.buscar_grupo_perfil_mapa(mapa_id)
    if not mapa:
        flash("Mapeamento de grupo externo não encontrado.", "danger")
        return redirect(url_for("configuracoes.usuarios_index"))
    perfis = AuthConfigService.repository.listar_perfis()
    integracoes_identidade = AuthConfigService.repository.listar_integracoes_identidade()
    if request.method == "POST":
        try:
            AuthConfigService.atualizar_grupo_perfil_mapa(mapa_id, request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            mapa = {**mapa, **request.form}
        else:
            flash("Mapeamento de grupo externo atualizado.", "success")
            return redirect(url_for("configuracoes.usuarios_index"))
    return render_template(
        "configuracoes/usuarios/grupo_mapa_form.html",
        mapa=mapa,
        perfis=perfis,
        integracoes_identidade=integracoes_identidade,
        modo="editar",
    )


@configuracoes_bp.route("/usuarios/grupos/<int:mapa_id>/excluir", methods=["POST"])
def usuarios_grupo_mapa_excluir(mapa_id):
    try:
        AuthConfigService.inativar_grupo_perfil_mapa(mapa_id, _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Mapeamento de grupo externo inativado.", "success")
    return redirect(url_for("configuracoes.usuarios_index"))


@configuracoes_bp.route("/usuarios/provedores/novo", methods=["GET", "POST"])
def usuarios_provedor_novo():
    flash("Provedores FreeIPA, LDAP e Active Directory agora devem ser cadastrados em Integrações Técnicas.", "info")
    return redirect(url_for("implantacao.integracoes_tecnicas"))


@configuracoes_bp.route("/usuarios/provedores/<int:provedor_id>/editar", methods=["GET", "POST"])
def usuarios_provedor_editar(provedor_id):
    flash("Provedores externos agora devem ser mantidos em Integrações Técnicas.", "info")
    return redirect(url_for("implantacao.integracoes_tecnicas"))


@configuracoes_bp.route("/usuarios/provedores/<int:provedor_id>/testar", methods=["POST"])
def usuarios_provedor_testar(provedor_id):
    flash("Valide FreeIPA, LDAP e Active Directory em Integrações Técnicas.", "info")
    return redirect(url_for("implantacao.integracoes_tecnicas"))


@configuracoes_bp.route("/backups")
def backups_index():
    _exigir_admin()
    return render_template(
        "configuracoes/backups/index.html",
        **BackupSistemaService.contexto(),
        page_title="Backups do Sistema",
        page_description="Backup do banco, storage, retenção e destino local ou caminho montado.",
        page_icon="bi-database-down",
        page_button_text=None,
    )


@configuracoes_bp.route("/backups/salvar", methods=["POST"])
def backups_salvar():
    _exigir_admin()
    try:
        BackupSistemaService.salvar_config(request.form, _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Configuração de backup atualizada.", "success")
    return redirect(url_for("configuracoes.backups_index"))


@configuracoes_bp.route("/backups/executar", methods=["POST"])
def backups_executar():
    _exigir_admin()
    try:
        resultado = BackupSistemaService.executar_manual(_email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash(resultado, "success" if ": OK" in resultado else "warning")
    return redirect(url_for("configuracoes.backups_index"))


@configuracoes_bp.route("/backups/<int:execucao_id>/download")
def backups_download(execucao_id):
    _exigir_admin()
    try:
        item, caminho = BackupSistemaService.caminho_download(execucao_id)
    except ValueError as erro:
        flash(str(erro), "danger")
        return redirect(url_for("configuracoes.backups_index"))
    return send_file(caminho, as_attachment=True, download_name=item.get("arquivo_nome") or caminho.name)


@configuracoes_bp.route("/cache")
def cache_index():
    _exigir_admin()
    return render_template(
        "configuracoes/cache/index.html",
        **CacheRetencaoService.contexto(),
        page_title="Retencao e Limpeza de Cache",
        page_description="Politicas de retencao para caches de infraestrutura, relatorios e sincronismos.",
        page_icon="bi-database-fill-gear",
        page_button_text=None,
    )


@configuracoes_bp.route("/cache/<cache_key>/retencao", methods=["POST"])
def cache_retencao(cache_key):
    _exigir_admin()
    try:
        CacheRetencaoService.salvar_retencao(cache_key, request.form.get("retencao_dias"), _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Retencao de cache atualizada.", "success")
    return redirect(url_for("configuracoes.cache_index"))


@configuracoes_bp.route("/cache/<cache_key>/limpar", methods=["POST"])
def cache_limpar(cache_key):
    _exigir_admin()
    try:
        removidos = CacheRetencaoService.limpar(cache_key, request.form.get("modo"), _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash(f"Limpeza concluida. {removidos} registro(s) removido(s).", "success")
    return redirect(url_for("configuracoes.cache_index"))


@configuracoes_bp.route("/sincronismos")
def sincronismos_index():
    _exigir_admin()
    return render_template(
        "configuracoes/sincronismos/index.html",
        **SincronismosAgendadosService.contexto(),
        page_title="Automações de Sincronismo",
        page_description="Agendador de sincronizações periodicas das integrações de negócio e infraestrutura.",
        page_icon="bi-arrow-repeat",
        page_button_text=None,
    )


@configuracoes_bp.route("/sincronismos/<tipo>/salvar", methods=["POST"])
def sincronismos_salvar(tipo):
    _exigir_admin()
    try:
        SincronismosAgendadosService.salvar(tipo, request.form, _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash("Agendamento de sincronismo atualizado.", "success")
    return redirect(url_for("configuracoes.sincronismos_index"))


@configuracoes_bp.route("/sincronismos/<int:agendamento_id>/executar", methods=["POST"])
def sincronismos_executar(agendamento_id):
    _exigir_admin()
    try:
        resultado = SincronismosAgendadosService.executar_manual(agendamento_id, _email_usuario_logado())
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash(resultado, "success" if ": OK" in resultado else "warning")
    return redirect(url_for("configuracoes.sincronismos_index"))


def _exigir_admin():
    if session.get("usuario_perfil") != "ADMIN":
        abort(403)


@configuracoes_bp.route("/auditoria")
def auditoria():
    contexto = AuthConfigService.contexto_auditoria(request.args)
    return render_template(
        "configuracoes/auditoria/index.html",
        **contexto,
        page_title="Auditoria",
        page_description="Eventos dos últimos 30 dias com filtros por usuário, ação e entidade.",
        page_icon="bi-clipboard-data",
        page_button_text=None,
    )


@configuracoes_bp.route("/email")
def email_index():
    return render_template(
        "configuracoes/email/index.html",
        configuracoes=EmailConfigService.listar(),
        page_title="Serviços de Email",
        page_description="Conta SMTP usada pelos avisos automáticos do sistema.",
        page_icon="bi-envelope-gear-fill",
        page_button_text="Novo Serviço",
        page_button_icon="bi-plus-circle",
        page_button_url=url_for("configuracoes.email_novo"),
    )


@configuracoes_bp.route("/email/novo", methods=["GET", "POST"])
def email_novo():
    if request.method == "POST":
        try:
            config_id = EmailConfigService.criar(request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            return render_template("configuracoes/email/form.html", config=request.form, modo="novo")
        flash("Serviço de e-mail cadastrado.", "success")
        return redirect(url_for("configuracoes.email_editar", config_id=config_id))
    return render_template(
        "configuracoes/email/form.html",
        config={"nome": "SMTP Principal", "provedor": "SMTP", "smtp_port": 587, "usar_tls": 1, "ativo": 1, "brevo_api_url": "https://api.brevo.com/v3", "brevo_environment": "production"},
        modo="novo",
    )


@configuracoes_bp.route("/email/<int:config_id>/editar", methods=["GET", "POST"])
def email_editar(config_id):
    config = EmailConfigService.buscar_por_id(config_id)
    if not config:
        flash("Serviço de e-mail não encontrado.", "danger")
        return redirect(url_for("configuracoes.email_index"))
    if request.method == "POST":
        try:
            EmailConfigService.atualizar(config_id, request.form, _email_usuario_logado())
        except ValueError as erro:
            flash(str(erro), "danger")
            config = {**config, **request.form}
        else:
            flash("Serviço de e-mail atualizado.", "success")
            return redirect(url_for("configuracoes.email_index"))
    return render_template("configuracoes/email/form.html", config=config, modo="editar")


@configuracoes_bp.route("/email/<int:config_id>/testar", methods=["POST"])
def email_testar(config_id):
    try:
        resultado = EmailConfigService.testar(config_id, request.form.get("destinatario"))
    except ValueError as erro:
        flash(str(erro), "danger")
    else:
        flash(f"E-mail de teste enviado para {resultado.get('destinatario')}.", "success")
    return redirect(request.referrer or url_for("configuracoes.email_index"))
