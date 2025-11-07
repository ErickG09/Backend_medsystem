# app/config.py
import os
from datetime import timedelta

def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

def _normalize_db_url(url: str | None) -> str | None:
    """
    Normaliza la URL de BD para SQLAlchemy 2.x.
    - postgres://...        -> postgresql+psycopg2://...
    - postgresql://...      -> postgresql+psycopg2://...
    Deja pasar otras (sqlite:/// etc).
    """
    if not url:
        return None
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url

class BaseConfig:
    # Core
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

    # DB
    _DB_URL = _normalize_db_url(os.getenv("DATABASE_URL"))
    # Fallback local (solo para dev) para evitar crash si no está la env
    SQLALCHEMY_DATABASE_URI = _DB_URL or "sqlite:///dev.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Timezone (para utilidades)
    APP_TZ = os.getenv("TZ", "America/Mexico_City")

    # CORS
    CORS_ORIGINS = _split_csv(os.getenv("CORS_ORIGINS", "http://localhost:3000"))
    CORS_SUPPORTS_CREDENTIALS = True

    # JWT (nombres según .env)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("ACCESS_TOKEN_EXPIRES", "900"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("REFRESH_TOKEN_EXPIRES", "2592000"))
    )

    # Rate limit (flask-limiter)
    RATELIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "60 per minute")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    # Password hashing (por si luego se leen en security.py)
    PASSWORD_HASH_TIME_COST = int(os.getenv("PASSWORD_HASH_TIME_COST", "3"))
    PASSWORD_HASH_MEMORY_COST = int(os.getenv("PASSWORD_HASH_MEMORY_COST", "65536"))
    PASSWORD_HASH_PARALLELISM = int(os.getenv("PASSWORD_HASH_PARALLELISM", "2"))

    # Media (placeholder para futuro storage)
    MEDIA_ROOT = os.getenv("MEDIA_ROOT", "./media")
    MEDIA_BASE_URL = os.getenv("MEDIA_BASE_URL", "/media")
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False

def get_config():
    """
    Usa FLASK_ENV para decidir la config.
    FLASK_ENV=production -> ProdConfig, cualquier otro -> DevConfig
    """
    env = os.getenv("FLASK_ENV", "development").lower()
    return ProdConfig if env == "production" else DevConfig
