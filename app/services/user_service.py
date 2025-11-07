from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..models.user import User, UserRole
from ..security import hash_password, password_is_strong

def create_user(data: dict) -> User:
    password = data.pop("password", None)
    if not password or not password_is_strong(password):
        raise ValueError("Contraseña no cumple política (min 12, Aa1!)")

    u = User(
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
        date_of_birth=data.get("date_of_birth"),
        photo_url=data.get("photo_url"),
        email=data["email"].lower().strip(),
        username=data["username"].strip(),
        password_hash=hash_password(password),
        role=UserRole(data["role"]),
        is_active=True,
    )
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError("Email o usuario ya existe") from e
    return u

def update_user(user: User, data: dict) -> User:
    for field in ["first_name", "last_name", "photo_url", "role", "is_active"]:
        if field in data and data[field] is not None:
            setattr(user, field, data[field])

    if "date_of_birth" in data:
        user.date_of_birth = data["date_of_birth"]
    if "email" in data and data["email"]:
        user.email = data["email"].lower().strip()
    if "username" in data and data["username"]:
        user.username = data["username"].strip()

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Datos en uso por otro usuario")
    return user

def get_user(user_id: int) -> User | None:
    return db.session.get(User, user_id)

def list_users(page: int = 1, page_size: int = 20, search: str | None = None):
    q = select(User).order_by(User.id.desc())
    if search:
        like = f"%{search.lower()}%"
        q = q.filter((User.email.ilike(like)) | (User.username.ilike(like)) |
                     (User.first_name.ilike(like)) | (User.last_name.ilike(like)))
    total = db.session.scalar(select(db.func.count()).select_from(q.subquery()))
    items = db.session.execute(q.limit(page_size).offset((page - 1) * page_size)).scalars().all()
    return items, total
