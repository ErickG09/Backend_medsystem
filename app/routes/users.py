from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..security import roles_required
from ..services import user_service
from ..schemas.user import UserCreateSchema, UserPublicSchema, UserUpdateSchema
from ..utils.responses import ok, created, error
from ..models.user import User
from ..extensions import db

bp = Blueprint("users", __name__, url_prefix="/users")

user_public = UserPublicSchema()
user_create = UserCreateSchema()
user_update = UserUpdateSchema()
user_list = UserPublicSchema(many=True)

@bp.post("")
@roles_required("admin")  # solo admin crea usuarios
def create_user():
    json = request.get_json(force=True)
    data = user_create.load(json)
    try:
        u = user_service.create_user(data)
        return created(user_public.dump(u))
    except ValueError as e:
        return error(str(e), 400)

@bp.get("")
@roles_required("admin", "doctor", "manager")
def list_users():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))
    search = request.args.get("search")
    items, total = user_service.list_users(page, page_size, search)
    return ok({"items": user_list.dump(items), "total": total, "page": page, "page_size": page_size})

@bp.get("/<int:user_id>")
@roles_required("admin", "doctor", "manager")
def get_user(user_id: int):
    u = user_service.get_user(user_id)
    if not u:
        return error("Usuario no encontrado", 404)
    return ok(user_public.dump(u))

@bp.patch("/<int:user_id>")
@roles_required("admin")
def update_user_route(user_id: int):
    u = db.session.get(User, user_id)
    if not u:
        return error("Usuario no encontrado", 404)
    data = user_update.load(request.get_json(force=True) or {})
    try:
        u = user_service.update_user(u, data)
        return ok(user_public.dump(u))
    except ValueError as e:
        return error(str(e), 400)

@bp.delete("/<int:user_id>")
@roles_required("admin")
def delete_user(user_id: int):
    u = db.session.get(User, user_id)
    if not u:
        return error("Usuario no encontrado", 404)
    db.session.delete(u)
    db.session.commit()
    return ok({"deleted": True, "id": user_id})
