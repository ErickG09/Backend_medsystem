from flask import Blueprint, request
from ..security import roles_required
from ..utils.responses import ok, created, error
from ..schemas.patient import (
    PatientCreateSchema,
    PatientPublicSchema,
    PatientUpdateSchema,
)
from ..services import patient_service
from ..extensions import db
from ..models.patient import Patient

bp = Blueprint("patients", __name__, url_prefix="/patients")

patient_create = PatientCreateSchema()
patient_update = PatientUpdateSchema()
patient_public = PatientPublicSchema()
patient_list = PatientPublicSchema(many=True)


# --------------------------------------------------------------------
# Crear paciente
# --------------------------------------------------------------------
@bp.post("")
@roles_required("admin", "doctor", "manager")
def create_patient():
    payload = request.get_json(force=True) or {}
    data = patient_create.load(payload)
    try:
        p = patient_service.create_patient(data)
        return created(patient_public.dump(p))
    except ValueError as e:
        return error(str(e), 400)


# --------------------------------------------------------------------
# Listar pacientes (q|name, from, to, paginación)
# --------------------------------------------------------------------
@bp.get("")
@roles_required("admin", "doctor", "manager", "nurse")
def list_patients():
    from ..utils.time import parse_date_or_datetime_to_utc

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    raw_name = request.args.get("name") or request.args.get("q") or ""
    terms = [t.strip() for t in raw_name.split() if t.strip()]

    raw_from = request.args.get("from")
    raw_to = request.args.get("to")
    dt_from = parse_date_or_datetime_to_utc(raw_from, as_start=True) if raw_from else None
    dt_to = parse_date_or_datetime_to_utc(raw_to, as_end=True) if raw_to else None

    items, total = patient_service.list_patients(
        page=page,
        page_size=page_size,
        terms=terms,
        created_from=dt_from,
        created_to=dt_to,
    )
    return ok(
        {
            "items": patient_list.dump(items),
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


# --------------------------------------------------------------------
# Detalle de paciente
# --------------------------------------------------------------------
@bp.get("/<int:patient_id>")
@roles_required("admin", "doctor", "manager", "nurse")
def get_patient(patient_id: int):
    p = patient_service.get_patient(patient_id)
    if not p:
        return error("Paciente no encontrado", 404)
    return ok(patient_public.dump(p))


# --------------------------------------------------------------------
# Actualizar paciente (PATCH y PUT)
# --------------------------------------------------------------------
@bp.patch("/<int:patient_id>")
@bp.put("/<int:patient_id>")
@roles_required("admin", "doctor", "manager")
def update_patient_route(patient_id: int):
    p = db.session.get(Patient, patient_id)
    if not p:
        return error("Paciente no encontrado", 404)

    payload = request.get_json(force=True) or {}
    data = patient_update.load(payload)  # valida y normaliza
    p = patient_service.update_patient(p, data)  # este servicio hace commit
    return ok(patient_public.dump(p))


# --------------------------------------------------------------------
# Eliminar paciente (DELETE)
#   - Si prefieres soft-delete, marca p.active=False y haz commit.
#   - Si no tienes cascade configurado en las relaciones, descomenta
#     el bloque para borrar dependencias antes del paciente.
# --------------------------------------------------------------------
@bp.delete("/<int:patient_id>")
@roles_required("admin", "doctor", "manager")
def delete_patient_route(patient_id: int):
    p = db.session.get(Patient, patient_id)
    if not p:
        return error("Paciente no encontrado", 404)

    # ---- Si NO tienes cascade, borra dependencias manualmente --------
    # from ..models.consultation import Consultation
    # from ..models.file import FileAsset
    # db.session.query(Consultation).filter_by(patient_id=patient_id).delete(synchronize_session=False)
    # db.session.query(FileAsset).filter_by(patient_id=patient_id).delete(synchronize_session=False)

    # ---- Borrado duro ------------
    db.session.delete(p)
    db.session.commit()
    return ok({"id": patient_id})

    # ---- Soft delete (alternativa) ----------
    # p.active = False
    # db.session.commit()
    # return ok({"id": patient_id, "active": p.active})


# --------------------------------------------------------------------
# Historial de paciente (datos de cabecera + consultas, marcando última)
# --------------------------------------------------------------------
@bp.get("/<int:patient_id>/history")
@roles_required("admin", "doctor", "manager", "nurse")
def patient_history(patient_id: int):
    p = patient_service.get_patient(patient_id)
    if not p:
        return error("Paciente no encontrado", 404)

    past = p.past_history or "Sin antecedentes patológicos"
    alerg = p.allergies or "Sin alergias"

    from ..models.consultation import Consultation
    cons = (
        db.session.query(Consultation)
        .filter(Consultation.patient_id == patient_id)
        .order_by(Consultation.datetime.desc(), Consultation.id.desc())
        .all()
    )

    from ..schemas.consultation import ConsultationPublicSchema
    cons_schema = ConsultationPublicSchema(many=True)
    cons_dump = cons_schema.dump(cons)
    if cons_dump:
        cons_dump[0]["is_last"] = True

    payload = {
        "patient": patient_public.dump(p),
        "past_history": past,
        "allergies": alerg,
        "consultations": cons_dump,
    }
    return ok(payload)
