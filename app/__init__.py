from flask import Flask

from app.core.config import Config
from app.core.database import init_db


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    init_db(app)

    # Financeiro
    from app.financeiro.routes import financeiro_bp
    app.register_blueprint(financeiro_bp)

    # Clientes
    from app.clientes.routes import clientes_bp
    app.register_blueprint(clientes_bp)

    return app
