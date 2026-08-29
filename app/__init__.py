from flask import Flask
from app.core.filters import cnpj_br, date_br, datetime_br, moeda
from app.core.config import Config
from app.core.access_control import init_access_control
from app.core.database import init_db
from app.core.logging_config import init_request_logging
from flask import send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)
    init_request_logging(app)

    if app.config.get("TRUST_PROXY"):
        hops = max(1, int(app.config.get("PROXY_FIX_HOPS", 1)))
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=hops, x_proto=hops, x_host=hops, x_prefix=hops)

    init_db(app)

    #Moeda e Data/Hora
    app.jinja_env.filters["date_br"] = date_br
    app.jinja_env.filters["datetime_br"] = datetime_br
    app.jinja_env.filters["moeda"] = moeda
    app.jinja_env.filters["cnpj_br"] = cnpj_br
    from app.core.filters import telefone_br
    app.jinja_env.filters["telefone_br"] = telefone_br
    init_access_control(app)

    from app.cli import init_cli
    init_cli(app)

    # Autenticação
    from app.autenticacao.routes import autenticacao_bp
    app.register_blueprint(autenticacao_bp)

    # Cadastros
    from app.financeiro.routes import financeiro_bp
    app.register_blueprint(financeiro_bp)

    # Clientes
    from app.clientes.routes import clientes_bp
    app.register_blueprint(clientes_bp)

    # Contratos
    from app.contratos.routes import contratos_bp
    app.register_blueprint(contratos_bp)

    #Parceiros
    from app.parceiros.routes import parceiros_bp
    app.register_blueprint(parceiros_bp)

    # Regras de Campanhas
    from app.regras_campanhas.routes import regras_campanhas_bp
    app.register_blueprint(regras_campanhas_bp)

    # Leads CRM
    from app.leads.routes import leads_bp
    app.register_blueprint(leads_bp)
    from app.leads.evento_routes import eventos_bp
    app.register_blueprint(eventos_bp)

    # Contatos CRM
    from app.contatos.routes import contatos_bp
    app.register_blueprint(contatos_bp)

    # Oportunidades CRM
    from app.oportunidades.routes import oportunidades_bp
    app.register_blueprint(oportunidades_bp)

    # Pipeline CRM
    from app.pipeline.routes import pipeline_bp
    app.register_blueprint(pipeline_bp)

    # Propostas CRM
    from app.propostas.routes import propostas_bp
    app.register_blueprint(propostas_bp)

    # Sucesso do Cliente
    from app.sucesso_cliente.routes import sucesso_cliente_bp
    app.register_blueprint(sucesso_cliente_bp)

    # Implantação
    from app.implantacao.routes import implantacao_bp
    app.register_blueprint(implantacao_bp)

    # Ambientes
    from app.ambientes.routes import ambientes_bp
    app.register_blueprint(ambientes_bp)

    # Catálogo Técnico
    from app.catalogo.routes import catalogo_bp
    app.register_blueprint(catalogo_bp)

    # Configurações
    from app.configuracoes.routes import configuracoes_bp
    app.register_blueprint(configuracoes_bp)

    # Infraestrutura
    from app.infraestrutura.routes import infraestrutura_bp
    app.register_blueprint(infraestrutura_bp)
    from app.infraestrutura.agendamentos.routes import proxmox_agendamentos_bp
    app.register_blueprint(proxmox_agendamentos_bp)

    from app.conhecimentos.routes import conhecimentos_bp
    app.register_blueprint(conhecimentos_bp)

    from app.administrativo.routes import administrativo_bp
    app.register_blueprint(administrativo_bp)

    from app.relatorios.routes import relatorios_bp
    app.register_blueprint(relatorios_bp)


    @app.route("/storage/<path:filename>")
    def storage(filename):

        return send_from_directory(
            "/opt/o3cloud-manager/storage",
            filename
        )


    #print(app.url_map)

    return app

