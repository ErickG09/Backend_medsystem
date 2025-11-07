from flask import Blueprint, request
from ..utils.responses import ok
from ..extensions import db
from sqlalchemy import text

bp = Blueprint("health", __name__, url_prefix="/health")

@bp.get("")
def health():
    """
    /api/v1/health
    Opcional: ?db=1 para probar conexión a base de datos.
    """
    db_ok = None
    if request.args.get("db") == "1":
        try:
            db.session.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            db_ok = False
    return ok({"service": "up", "db": db_ok})
