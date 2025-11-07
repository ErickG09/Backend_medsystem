from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.auth_service import authenticate, build_tokens
from ..utils.responses import ok, error
from ..schemas.user import LoginSchema
from ..extensions import limiter

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.post("/login")
@limiter.limit("5 per minute")  # rate limit por IP
def login():
    payload = request.get_json(silent=True) or {}
    # Permitimos login con email o username
    identifier = payload.get("username") or payload.get("email")
    password = payload.get("password") or ""
    if not identifier or not password:
        return error("Faltan credenciales", 400)

    user = authenticate(identifier, password)
    if not user:
        return error("Credenciales inválidas", 401)

    tokens = build_tokens(user)
    return ok({"user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role.value,
                    "photo_url": user.photo_url,
                },
               **tokens})

@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    # identidad ya validada por JWT refresh
    identity = get_jwt_identity()
    # en un caso real buscaríamos el user por id para reinyectar claims
    from ..models.user import User
    from ..extensions import db
    user = db.session.get(User, int(identity)) if identity else None
    if not user or not user.is_active:
        return error("Usuario no disponible", 401)
    return ok(build_tokens(user))

@bp.post("/logout")
@jwt_required()
def logout():
    # stateless: el front solo descarta tokens
    return ok({"logged_out": True})
