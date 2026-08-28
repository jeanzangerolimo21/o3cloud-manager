import os

import click
from flask.cli import with_appcontext

from app.configuracoes.auth_service import AuthConfigService


@click.command("bootstrap-admin")
@click.option("--email", envvar="O3_BOOTSTRAP_ADMIN_EMAIL", help="E-mail do administrador inicial.")
@click.option("--name", "nome", envvar="O3_BOOTSTRAP_ADMIN_NAME", default="Administrador", show_default=True, help="Nome do administrador inicial.")
@click.option("--login", envvar="O3_BOOTSTRAP_ADMIN_LOGIN", help="Login alternativo. Usa o e-mail se vazio.")
@click.option("--password", "senha", envvar="O3_BOOTSTRAP_ADMIN_PASSWORD", help="Senha inicial. Pode vir de O3_BOOTSTRAP_ADMIN_PASSWORD.")
@click.option("--force", is_flag=True, help="Permite promover/atualizar o usuário informado mesmo já existindo ADMIN ativo.")
def bootstrap_admin_command(email, nome, login, senha, force):
    """Cria ou promove o primeiro administrador local de forma controlada."""
    if not senha:
        senha = click.prompt("Senha inicial", hide_input=True, confirmation_prompt=True)
    try:
        resultado = AuthConfigService.bootstrap_admin(
            nome=nome,
            email=email,
            login=login,
            senha=senha,
            permitir_atualizar=force,
        )
    except ValueError as erro:
        raise click.ClickException(str(erro)) from erro
    click.echo(f"{resultado['acao']}: usuário #{resultado['usuario_id']} ({resultado['email']})")


def init_cli(app):
    app.cli.add_command(bootstrap_admin_command)
    app.cli.add_command(relatorios_processar_jobs_command)
    app.cli.add_command(sincronismos_processar_agendados_command)
    app.cli.add_command(sincronismos_executar_worker_command)
    app.cli.add_command(backups_processar_agendados_command)
    app.cli.add_command(aso_processar_lembretes_command)
    app.cli.add_command(operacao_alertas_enviar_command)
    app.cli.add_command(reajustes_processar_alertas_command)


@click.command("relatorios-processar-jobs")
@with_appcontext
@click.option("--limite", default=1, show_default=True, help="Quantidade maxima de jobs pendentes para processar.")
def relatorios_processar_jobs_command(limite):
    """Processa jobs pendentes de relatorios em segundo plano."""
    from app.relatorios.service import RelatorioService

    resultados = RelatorioService.processar_jobs(limite)
    if not resultados:
        click.echo("Nenhum job pendente.")
        return
    for resultado in resultados:
        click.echo(resultado)

@click.command("sincronismos-processar-agendados")
@with_appcontext
@click.option("--limite", default=5, show_default=True, help="Quantidade maxima de sincronismos pendentes para processar.")
def sincronismos_processar_agendados_command(limite):
    """Processa sincronismos agendados pendentes."""
    from app.configuracoes.sincronismos_service import SincronismosAgendadosService

    resultados = SincronismosAgendadosService.processar_pendentes(limite)
    if not resultados:
        click.echo("Nenhum sincronismo pendente.")
        return
    for resultado in resultados:
        click.echo(resultado)


@click.command("sincronismos-executar-worker")
@with_appcontext
@click.option("--execucao-id", required=True, type=int, help="ID da execucao de sincronismo a processar.")
def sincronismos_executar_worker_command(execucao_id):
    """Executa uma execucao de sincronismo ja registrada."""
    from app.configuracoes.sincronismos_service import SincronismosAgendadosService

    click.echo(SincronismosAgendadosService.executar_worker(execucao_id))


@click.command("backups-processar-agendados")
@with_appcontext
@click.option("--limite", default=1, show_default=True, help="Quantidade maxima de backups pendentes para processar.")
def backups_processar_agendados_command(limite):
    """Processa backups agendados pendentes."""
    from app.configuracoes.backup_service import BackupSistemaService

    resultados = BackupSistemaService.processar_pendentes(limite)
    if not resultados:
        click.echo("Nenhum backup pendente.")
        return
    for resultado in resultados:
        click.echo(resultado)


@click.command("aso-processar-lembretes")
@with_appcontext
@click.option("--limite", default=20, show_default=True, help="Quantidade maxima de lembretes ASO pendentes para processar.")
def aso_processar_lembretes_command(limite):
    """Envia e-mails de lembrete de ASO na antecedencia configurada."""
    from app.administrativo.aso_service import AdministrativoAsoService

    resultados = AdministrativoAsoService.processar_lembretes_email(limite)
    if not resultados:
        click.echo("Nenhum lembrete ASO pendente.")
        return
    for resultado in resultados:
        click.echo(resultado)


@click.command("operacao-alertas-enviar")
@with_appcontext
@click.option("--limite", default=20, show_default=True, help="Quantidade maxima de usuarios para processar.")
@click.option("--forcar", is_flag=True, help="Envia para usuarios habilitados ignorando periodicidade/horario.")
def operacao_alertas_enviar_command(limite, forcar):
    """Envia alertas criticos de operacao por e-mail."""
    from app.infraestrutura.alertas_operacao_service import AlertasOperacaoService

    resultados = AlertasOperacaoService.processar_pendentes(limite=limite, forcar=forcar)
    for resultado in resultados:
        click.echo(resultado)


@click.command("reajustes-processar-alertas")
@with_appcontext
def reajustes_processar_alertas_command():
    """Processa alertas de reajustes contratuais."""
    from app.financeiro.reajuste_service import ReajusteContratoService

    resultado = ReajusteContratoService.processar_alertas("cron")
    click.echo(
        "Verificacao de reajustes: {} alerta(s), {} e-mail(s).".format(
            resultado.get("criados", 0), resultado.get("emails", 0)
        )
    )
    for mensagem in resultado.get("mensagens", [])[:50]:
        click.echo(mensagem)
