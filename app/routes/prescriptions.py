from flask import Blueprint, request, make_response
from ..security import roles_required
from ..utils.responses import ok, created, error
from ..extensions import db
from ..models.prescription import Prescription
from ..models.patient import Patient, Sex
from ..models.consultation import Consultation
from ..schemas.prescription import (
    PrescriptionCreateSchema, PrescriptionUpdateSchema, PrescriptionPublicSchema
)
from ..utils.time import now_cdmx, to_utc

bp = Blueprint("prescriptions", __name__, url_prefix="/prescriptions")

presc_create = PrescriptionCreateSchema()
presc_update = PrescriptionUpdateSchema()
presc_public = PrescriptionPublicSchema()
presc_list = PrescriptionPublicSchema(many=True)

# Helper: crear “paciente rápido” desde la receta (mínimos)
def _create_quick_patient(data: dict) -> Patient:
    """
    Crea un paciente mínimo desde la receta.
    Acepta date_of_birth como string ISO y normaliza sex a F/M/O.
    """
    from datetime import date
    from dateutil import parser as dtparser

    required = ("first_name", "last_name", "date_of_birth", "sex", "phone", "email")
    for r in required:
        if r not in data or data[r] in (None, ""):
            raise ValueError(f"new_patient.{r} requerido")

    # Parse de fecha (acepta string o date)
    dob = data["date_of_birth"]
    if isinstance(dob, str):
        try:
            dob = dtparser.isoparse(dob).date()
        except Exception:
            raise ValueError("new_patient.date_of_birth inválido (usa YYYY-MM-DD)")

    # Normaliza sexo
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
    db.session.flush()  # obtiene p.id sin commit aún
    return p


# Crear receta
@bp.post("")
@roles_required("admin", "doctor", "manager")
def create_prescription():
    payload = request.get_json(force=True) or {}
    data = presc_create.load(payload)

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

    # issued_at por defecto = ahora CDMX → guardamos UTC
    issued_at = data.get("issued_at")
    if issued_at is None:
        issued_at = to_utc(now_cdmx())
    else:
        issued_at = to_utc(issued_at)

    # Si no envían bmi, autocompleta desde el paciente
    bmi = data.get("bmi")
    if bmi is None:
        bmi = patient.bmi

    c_id = data.get("consultation_id")
    if c_id:
        c = db.session.get(Consultation, c_id)
        if not c or c.patient_id != patient.id:
            return error("Consulta inválida para este paciente", 400)

    presc = Prescription(
        patient_id=patient.id,
        consultation_id=c_id,
        professional_id=data.get("professional_id"),
        issued_at=issued_at,
        temp_c=data.get("temp_c"),
        bp_sys=data.get("bp_sys"),
        bp_dia=data.get("bp_dia"),
        heart_rate=data.get("heart_rate"),
        resp_rate=data.get("resp_rate"),
        bmi=bmi,
        spo2=data.get("spo2"),
        diagnosis=data.get("diagnosis"),
        prescription_text=data.get("prescription_text"),
        care_instructions=data.get("care_instructions"),
        products=data.get("products"),
    )
    db.session.add(presc)
    db.session.commit()
    return created(presc_public.dump(presc))

# Listado
@bp.get("")
@roles_required("admin", "doctor", "manager", "nurse")
def list_prescriptions():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))
    patient_id = request.args.get("patient_id", type=int)

    q = db.session.query(Prescription).order_by(Prescription.issued_at.desc(), Prescription.id.desc())
    if patient_id:
        q = q.filter(Prescription.patient_id == patient_id)

    total = q.count()
    items = q.limit(page_size).offset((page - 1) * page_size).all()
    return ok({"items": presc_list.dump(items), "total": total, "page": page, "page_size": page_size})

# Detalle
@bp.get("/<int:presc_id>")
@roles_required("admin", "doctor", "manager", "nurse")
def get_prescription(presc_id: int):
    p = db.session.get(Prescription, presc_id)
    if not p:
        return error("Receta no encontrada", 404)
    return ok(presc_public.dump(p))

# Editar
@bp.patch("/<int:presc_id>")
@roles_required("admin", "doctor", "manager")
def update_prescription(presc_id: int):
    p = db.session.get(Prescription, presc_id)
    if not p:
        return error("Receta no encontrada", 404)
    data = presc_update.load(request.get_json(force=True) or {})
    for k, v in data.items():
        setattr(p, k, v)
    db.session.add(p)
    db.session.commit()
    return ok(presc_public.dump(p))

# Eliminar
@bp.delete("/<int:presc_id>")
@roles_required("admin", "doctor", "manager")
def delete_prescription(presc_id: int):
    p = db.session.get(Prescription, presc_id)
    if not p:
        return error("Receta no encontrada", 404)
    db.session.delete(p)
    db.session.commit()
    return ok({"deleted": True, "id": presc_id})

# Imprimir (HTML media carta)
@bp.get("/<int:presc_id>/print")
@roles_required("admin", "doctor", "manager", "nurse")
def print_prescription(presc_id: int):
    p: Prescription = db.session.get(Prescription, presc_id)
    if not p:
        return error("Receta no encontrada", 404)

    patient = p.patient
    pro = p.professional
    ta = f"{p.bp_sys}/{p.bp_dia} mmHg" if p.bp_sys and p.bp_dia else "—"

    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<title>Receta #{p.id}</title>
<style>
@page {{
  size: 8.5in 5.5in;   /* media carta (horizontal por defecto de la impresora) */
  margin: 12mm;
}}
body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; color:#111; }}
.header {{
  display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;
}}
.h1 {{ font-size:20px; font-weight:700; letter-spacing:0.4px; }}
.small {{ color:#555; font-size:12px; }}
.block {{ margin-top:10px; }}
hr {{ border:0; height:1px; background:#ddd; margin:10px 0; }}
ul {{ margin:6px 0 0 18px; }}
.label {{ font-weight:600; }}
.table {{
  width:100%; border-collapse:collapse; font-size:14px;
}}
.table td {{ padding:3px 6px; vertical-align:top; }}
.right {{ text-align:right; }}
.print-btn {{ display:none; }}
@media screen {{
  .print-btn {{ display:inline-block; margin:8px 0; padding:6px 10px; border:1px solid #ddd; border-radius:6px; }}
}}
</style>
</head>
<body>
  <button class="print-btn" onclick="window.print()">Imprimir</button>

  <div class="header">
    <div>
      <div class="h1">CIMEDYC</div>
      <div class="small">Centro Integral de Medicina y Clínica<br/>Puebla, México</div>
    </div>
    <div class="small right">
      <div><b>Fecha:</b> {p.issued_at.isoformat()}</div>
      <div><b>Doctor(a):</b> { (pro.first_name + " " + pro.last_name) if pro else "-" }</div>
      <div><b>Receta #</b> {p.id}</div>
    </div>
  </div>
  <hr/>

  <div class="block">
    <table class="table">
      <tr>
        <td><span class="label">Paciente:</span> {patient.first_name} {patient.last_name}</td>
        <td class="right"><span class="label">ID:</span> {patient.id}</td>
      </tr>
      <tr class="small">
        <td><span class="label">Edad:</span> {patient.age_years or ""} años</td>
        <td class="right"><span class="label">Sexo:</span> {patient.sex.value if hasattr(patient.sex,'value') else patient.sex}</td>
      </tr>
    </table>
  </div>

  <div class="block small">
    <span class="label">Signos:</span>
    Temp. {p.temp_c or "—"} °C &nbsp; | &nbsp; T.A. {ta} &nbsp; | &nbsp; F.C. {p.heart_rate or "—"} lpm
    &nbsp; | &nbsp; F.R. {p.resp_rate or "—"} rpm &nbsp; | &nbsp; IMC {p.bmi or (patient.bmi or "—")}
    &nbsp; | &nbsp; SATO { (str(p.spo2) + "%") if p.spo2 is not None else "—" }
  </div>

  <div class="block">
    <div class="label">Diagnóstico</div>
    <div class="small">{p.diagnosis or "—"}</div>
  </div>

  <div class="block">
    <div class="label">Analgésico y cuidados</div>
    <div class="small">{p.prescription_text or "—"}</div>
  </div>

  <div class="block">
    <div class="label">Cuidados / Indicaciones</div>
    <div class="small">{p.care_instructions or "—"}</div>
  </div>

  <div class="block small"><span class="label">Productos:</span> {p.products or "—"}</div>

  <hr/>
  <div class="small">Firma y cédula profesional</div>
</body>
</html>"""
    resp = make_response(html, 200)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp
