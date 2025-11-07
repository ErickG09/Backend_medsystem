from datetime import timedelta
from flask import Blueprint, request
from sqlalchemy import or_
from ..security import roles_required
from ..utils.responses import ok, created, error
from ..extensions import db
from ..models.appointment import Appointment, AppointmentStatus, AppointmentType
from ..models.patient import Patient, Sex
from ..schemas.appointment import (
    AppointmentCreateSchema, AppointmentUpdateSchema, AppointmentPublicSchema
)
from ..utils.time import parse_date_or_datetime_to_utc, to_utc

bp = Blueprint("appointments", __name__, url_prefix="/appointments")

appt_create = AppointmentCreateSchema()
appt_update = AppointmentUpdateSchema()
appt_public = AppointmentPublicSchema()
appt_list = AppointmentPublicSchema(many=True)

# Helper: crear paciente rápido (mínimos), igual que en prescriptions
def _create_quick_patient(data: dict) -> Patient:
    from datetime import date
    from dateutil import parser as dtparser

    required = ("first_name", "last_name", "date_of_birth", "sex", "phone", "email")
    for r in required:
        if r not in data or data[r] in (None, ""):
            raise ValueError(f"new_patient.{r} requerido")

    dob = data["date_of_birth"]
    if isinstance(dob, str):
        try:
            dob = dtparser.isoparse(dob).date()
        except Exception:
            raise ValueError("new_patient.date_of_birth inválido (usa YYYY-MM-DD)")

    sex_raw = (data.get("sex") or "").strip().upper()
    if sex_raw not in ("F", "M", "O"):
        raise ValueError("new_patient.sex inválido (usa F, M u O)")

    p = Patient(
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
        date_of_birth=dob,
        sex=Sex(sex_raw),
        phone=str(data["phone"]).strip(),
        email=str(data["email"]).lower().strip(),
        weight_kg=data.get("weight_kg"),
        height_m=data.get("height_m"),
        treatments_of_interest=data.get("treatments_of_interest") or "",
        past_history=(data.get("past_history") or "Sin antecedentes patológicos"),
        allergies=(data.get("allergies") or "Sin alergias"),
        privacy_notice_accepted=bool(data.get("privacy_notice_accepted", False)),
        informed_consent_accepted=bool(data.get("informed_consent_accepted", False)),
        emergency_full_name=data.get("emergency_full_name"),
        emergency_phone=data.get("emergency_phone"),
        emergency_relation=data.get("emergency_relation"),
    )
    p.recalc_age_and_bmi()
    db.session.add(p)
    db.session.flush()
    return p

# Crear cita (admin/doctor/manager) — nurses: solo lectura
@bp.post("")
@roles_required("admin", "doctor", "manager")
def create_appointment():
    payload = request.get_json(force=True) or {}
    data = appt_create.load(payload)

    patient_id = data.get("patient_id")
    if not patient_id and data.get("new_patient"):
        try:
            p = _create_quick_patient(data["new_patient"])
            patient_id = p.id
        except ValueError as e:
            db.session.rollback()
            return error(str(e), 400)
    if not patient_id:
        return error("Debe indicar patient_id o new_patient", 400)

    patient = db.session.get(Patient, patient_id)
    if not patient:
        db.session.rollback()
        return error("Paciente no encontrado", 404)

    start_at = to_utc(data["start_at"])  # asume CDMX si viene naive
    duration = int(data["duration_min"])
    end_at = start_at + timedelta(minutes=duration)

    status = data.get("status") or AppointmentStatus.PENDING.value
    appt_type = data.get("appt_type") or AppointmentType.CONSULTA.value

    appt = Appointment(
        patient_id=patient.id,
        professional_id=data.get("professional_id"),
        title=data["title"].strip(),
        start_at=start_at,
        end_at=end_at,
        duration_min=duration,
        status=AppointmentStatus(status),
        appt_type=AppointmentType(appt_type),
        treatment=data.get("treatment"),
        notes=data.get("notes"),
    )
    db.session.add(appt)
    db.session.commit()
    return created(appt_public.dump(appt))

# Listar por rango y filtros (para mes/semana/día basta cambiar el rango)
@bp.get("")
@roles_required("admin", "doctor", "manager", "nurse")
def list_appointments():
    # Rango: start= & end= (obligatorio para vistas del calendario)
    raw_start = request.args.get("start")
    raw_end = request.args.get("end")
    if not raw_start or not raw_end:
        return error("Parámetros 'start' y 'end' son obligatorios (ISO o YYYY-MM-DD)", 400)

    dt_start = parse_date_or_datetime_to_utc(raw_start, as_start=True)
    dt_end   = parse_date_or_datetime_to_utc(raw_end, as_end=True)

    doctor_id = request.args.get("doctor_id", type=int)  # professional_id
    status = request.args.get("status")  # pending|confirmed|...
    name = request.args.get("name") or request.args.get("q")

    q = db.session.query(Appointment).filter(
        Appointment.start_at <= dt_end,
        Appointment.end_at >= dt_start
    ).order_by(Appointment.start_at.asc())

    if doctor_id:
        q = q.filter(Appointment.professional_id == doctor_id)
    if status:
        q = q.filter(Appointment.status == status)

    if name:
        like = f"%{name.lower()}%"
        q = q.join(Patient).filter(or_(Patient.first_name.ilike(like), Patient.last_name.ilike(like)))

    items = q.all()
    return ok({"items": appt_list.dump(items)})

# Detalle
@bp.get("/<int:appt_id>")
@roles_required("admin", "doctor", "manager", "nurse")
def get_appointment(appt_id: int):
    a = db.session.get(Appointment, appt_id)
    if not a:
        return error("Cita no encontrada", 404)
    return ok(appt_public.dump(a))

# Editar (mover/resize/estado/notas)
@bp.patch("/<int:appt_id>")
@roles_required("admin", "doctor", "manager")
def update_appointment(appt_id: int):
    a = db.session.get(Appointment, appt_id)
    if not a:
        return error("Cita no encontrada", 404)

    data = appt_update.load(request.get_json(force=True) or {})

    if "start_at" in data:
        start_at = to_utc(data["start_at"])
        a.start_at = start_at
        # si no mandan duration, mantenemos, si sí, recalculamos
        dur = data.get("duration_min", a.duration_min)
        a.duration_min = dur
        a.end_at = start_at + timedelta(minutes=dur)
    elif "duration_min" in data:
        a.duration_min = int(data["duration_min"])
        a.end_at = a.start_at + timedelta(minutes=a.duration_min)

    for k in ("professional_id", "title", "status", "appt_type", "treatment", "notes"):
        if k in data:
            if k == "status":
                setattr(a, k, AppointmentStatus(data[k]))
            elif k == "appt_type":
                setattr(a, k, AppointmentType(data[k]))
            else:
                setattr(a, k, data[k])

    db.session.add(a)
    db.session.commit()
    return ok(appt_public.dump(a))

# Borrar
@bp.delete("/<int:appt_id>")
@roles_required("admin", "doctor", "manager")
def delete_appointment(appt_id: int):
    a = db.session.get(Appointment, appt_id)
    if not a:
        return error("Cita no encontrada", 404)
    db.session.delete(a)
    db.session.commit()
    return ok({"deleted": True, "id": appt_id})
