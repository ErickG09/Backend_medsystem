from flask import Blueprint, request
from sqlalchemy import and_
from ..security import roles_required
from ..utils.responses import ok, created, error
from ..extensions import db
from ..models.consultation import Consultation
from ..models.patient import Patient
from ..schemas.consultation import (
    ConsultationCreateSchema, ConsultationUpdateSchema, ConsultationPublicSchema
)
from ..utils.time import parse_date_or_datetime_to_utc  

bp = Blueprint("consultations", __name__, url_prefix="/consultations")

cons_create = ConsultationCreateSchema()
cons_update = ConsultationUpdateSchema()
cons_public = ConsultationPublicSchema()
cons_list = ConsultationPublicSchema(many=True)

# Crear consulta (admin/doctor/manager). Enfermera puede crear si quieres; por ahora lee solamente.
@bp.post("")
@roles_required("admin", "doctor", "manager")
def create_consultation():
    payload = request.get_json(force=True)
    data = cons_create.load(payload)

    # validación de paciente
    patient = db.session.get(Patient, data["patient_id"])
    if not patient:
        return error("Paciente no encontrado", 404)

    c = Consultation(**data)
    db.session.add(c)
    db.session.commit()
    return created(cons_public.dump(c))

# Listado general con filtros por nombre de paciente y rango de fechas
@bp.get("")
@roles_required("admin", "doctor", "manager", "nurse")
def list_consultations():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    name = request.args.get("name") or request.args.get("q")
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    q = db.session.query(Consultation).order_by(
        Consultation.datetime.desc(), Consultation.id.desc()
    )

    # Fechas: convertimos a UTC y filtramos correctamente
    if date_from:
        dt_from = parse_date_or_datetime_to_utc(date_from, as_start=True)
        q = q.filter(Consultation.datetime >= dt_from)
    if date_to:
        dt_to = parse_date_or_datetime_to_utc(date_to, as_end=True)
        q = q.filter(Consultation.datetime <= dt_to)

    if name:
        like = f"%{name.lower()}%"
        q = (
            q.join(Patient)
            .filter(
                (Patient.first_name.ilike(like)) | (Patient.last_name.ilike(like))
            )
        )

    total = q.count()
    items = q.limit(page_size).offset((page - 1) * page_size).all()
    return ok(
        {"items": cons_list.dump(items), "total": total, "page": page, "page_size": page_size}
    )

# Detalle
@bp.get("/<int:cons_id>")
@roles_required("admin", "doctor", "manager", "nurse")
def get_consultation(cons_id: int):
    c = db.session.get(Consultation, cons_id)
    if not c:
        return error("Consulta no encontrada", 404)
    return ok(cons_public.dump(c))

# Editar
@bp.patch("/<int:cons_id>")
@roles_required("admin", "doctor", "manager")
def update_consultation(cons_id: int):
    c = db.session.get(Consultation, cons_id)
    if not c:
        return error("Consulta no encontrada", 404)
    data = cons_update.load(request.get_json(force=True) or {})
    for k, v in data.items():
        setattr(c, k, v)
    db.session.add(c)
    db.session.commit()
    return ok(cons_public.dump(c))

# Borrar
@bp.delete("/<int:cons_id>")
@roles_required("admin", "doctor", "manager")
def delete_consultation(cons_id: int):
    c = db.session.get(Consultation, cons_id)
    if not c:
        return error("Consulta no encontrada", 404)
    db.session.delete(c)
    db.session.commit()
    return ok({"deleted": True, "id": cons_id})
