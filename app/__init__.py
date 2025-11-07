# app/__init__.py
from flask import Flask
from dotenv import load_dotenv

from .config import get_config
from .extensions import init_extensions
from .routes import register_routes

def create_app() -> Flask:
    # Carga variables del .env en la raíz del proyecto
    load_dotenv()

    app = Flask(__name__)

    # Aplica la configuración (DevConfig o ProdConfig según FLASK_ENV)
    app.config.from_object(get_config())

    # Inicializa extensiones (db, migrate, limiter, cors, jwt, etc.)
    init_extensions(app)

    # Registra blueprints de la API
    register_routes(app)

    return app
