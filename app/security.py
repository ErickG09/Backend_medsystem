from functools import wraps
from typing import Iterable
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from argon2 import PasswordHasher
import re

# Argon2id configurado (puedes subir costo en producción)
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)

def hash_password(plain: str) -> str:
    return ph.hash(plain)

def verify_password(hash_value: str, plain: str) -> bool:
    try:
        return ph.verify(hash_value, plain)
    except Exception:
        return False

# Política mínima de contraseña segura
_pw_regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$")
def password_is_strong(pw: str) -> bool:
    return bool(_pw_regex.match(pw or ""))

def roles_required(*roles: Iterable[str]):
    """
    Decorator RBAC por rol. Requiere JWT y valida que 'role' esté en el claim.
    Uso: @roles_required('admin', 'manager')
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()  # <-- ahora obligatorio
            claims = get_jwt() or {}
            user_role = claims.get("role")
            if roles and user_role not in roles:
                return jsonify({"message": "Forbidden", "required_roles": roles}), 403
            return fn(*args, **kwargs)
        return decorated
    return wrapper
