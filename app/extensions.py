from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()

# storage_uri se configura luego con app.config
limiter = Limiter(key_func=get_remote_address, default_limits=[])

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # CORS: solo los orígenes permitidos de tu .env
    cors.init_app(
        app,
        resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=False,
    )

    # Rate limit
    limiter._default_limits = [app.config.get("RATELIMIT_DEFAULT")] if app.config.get("RATELIMIT_DEFAULT") else []
    storage_uri = app.config.get("RATELIMIT_STORAGE_URI")
    if storage_uri:
        limiter._storage_uri = storage_uri
    limiter.init_app(app)

    @app.errorhandler(ValidationError)
    def handle_marshmallow_error(err):
        return {"message": "Validation error", "errors": err.messages}, 400
