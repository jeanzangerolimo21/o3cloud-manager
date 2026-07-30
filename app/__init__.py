from flask import Flask
from app.core.filters import date_br, moeda
from app.core.config import Config
from app.core.database import init_db
from flask import send_from_directory

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    init_db(app)

    #Moeda e Data/Hora
    app.jinja_env.filters["date_br"] = date_br
    app.jinja_env.filters["moeda"] = moeda

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

    # Leads CRM
    from app.leads.routes import leads_bp
    app.register_blueprint(leads_bp)

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


    @app.route("/storage/<path:filename>")
    def storage(filename):

        return send_from_directory(
            "/opt/o3cloud-manager/storage",
            filename
        )


    #print(app.url_map)

    return app

