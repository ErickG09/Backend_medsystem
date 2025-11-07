from datetime import timedelta
from typing import Optional
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import or_
from ..extensions import db
from ..models.user import User
from ..security import verify_password

def authenticate(identifier: str, password: str) -> Optional[User]:
    """identifier puede ser email o username"""
    user = (
        db.session.query(User)
        .filter(or_(User.email == identifier.lower(), User.username == identifier))
        .first()
    )
    if not user or not user.is_active:
        return None
    if not verify_password(user.password_hash, password):
        return None
    return user

def build_tokens(user: User) -> dict:
    claims = {"role": user.role.value, "uid": user.id, "username": user.username}
    access = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(user.id), additional_claims=claims)
    return {"access_token": access, "refresh_token": refresh}
