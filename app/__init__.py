from flask import Flask
from app.core.filters import date_br, moeda
from app.core.config import Config
from app.core.database import init_db

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
    return app
