from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..models.patient import Patient

DEFAULT_PAST_HISTORY = "Sin antecedentes patológicos"
DEFAULT_ALLERGIES = "Sin alergias"

def create_patient(data: dict) -> Patient:
    # Defaults de texto si no vienen
    if not data.get("past_history"):
        data["past_history"] = DEFAULT_PAST_HISTORY
    if not data.get("allergies"):
        data["allergies"] = DEFAULT_ALLERGIES

    p = Patient(**data)
    p.recalc_age_and_bmi()

    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError("Error al crear paciente") from e
    return p

def update_patient(p: Patient, data: dict) -> Patient:
    for k, v in data.items():
        setattr(p, k, v)

    # Asignar defaults si quedaron vacíos
    if p.past_history is None or p.past_history.strip() == "":
        p.past_history = DEFAULT_PAST_HISTORY
    if p.allergies is None or p.allergies.strip() == "":
        p.allergies = DEFAULT_ALLERGIES

    p.recalc_age_and_bmi()
    db.session.add(p)
    db.session.commit()
    return p

def get_patient(patient_id: int) -> Patient | None:
    return db.session.get(Patient, patient_id)

def list_patients(page: int = 1, page_size: int = 20, terms: list[str] | None = None,
                  created_from=None, created_to=None):
    q = select(Patient).order_by(Patient.id.desc())

    # nombre completo: cada término debe aparecer en first_name o last_name
    if terms:
        for term in terms:
            like = f"%{term.lower()}%"
            q = q.filter(or_(Patient.first_name.ilike(like), Patient.last_name.ilike(like)))

    if created_from is not None:
        q = q.filter(Patient.created_at >= created_from)
    if created_to is not None:
        q = q.filter(Patient.created_at <= created_to)

    total = db.session.scalar(select(db.func.count()).select_from(q.subquery()))
    items = db.session.execute(q.limit(page_size).offset((page - 1) * page_size)).scalars().all()
    return items, total
