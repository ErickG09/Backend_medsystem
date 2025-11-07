from flask import Blueprint
from .health import bp as health_bp
from .auth import bp as auth_bp
from .users import bp as users_bp
from .patients import bp as patients_bp
from .files import bp as files_bp
from .consultations import bp as consultations_bp
from .prescriptions import bp as prescriptions_bp
from .appointments import bp as appointments_bp  # <-- NEW

def register_routes(app):
    prefix = app.config.get("API_PREFIX", "/api/v1")
    api = Blueprint("api", __name__, url_prefix=prefix)

    api.register_blueprint(health_bp)
    api.register_blueprint(auth_bp)
    api.register_blueprint(users_bp)
    api.register_blueprint(patients_bp)
    api.register_blueprint(files_bp)
    api.register_blueprint(consultations_bp)
    api.register_blueprint(prescriptions_bp)
    api.register_blueprint(appointments_bp)  # <-- NEW

    app.register_blueprint(api)
