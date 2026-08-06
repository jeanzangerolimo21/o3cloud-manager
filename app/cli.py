import os

import click

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
