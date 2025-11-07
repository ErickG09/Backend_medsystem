from flask import Blueprint, request
from ..security import roles_required
from ..utils.responses import ok, created, error
from ..schemas.file_asset import FileCreateSchema, FilePublicSchema
from ..extensions import db
from ..models.file_asset import FileAsset, FileKind, PhotoPhase
from ..models.patient import Patient
from ..services.image_service import validate_and_prepare

bp = Blueprint("files", __name__, url_prefix="")

file_create = FileCreateSchema()
file_public = FilePublicSchema()
file_list = FilePublicSchema(many=True)

# Crear documento/foto por URL
@bp.post("/patients/<int:patient_id>/files")
@roles_required("admin", "doctor", "manager")
def add_file(patient_id: int):
    p = db.session.get(Patient, patient_id)
    if not p:
        return error("Paciente no encontrado", 404)

    payload = request.get_json(force=True) or {}
    data = file_create.load(payload)

    kind = FileKind(data["kind"])
    url_norm, mime = validate_and_prepare(kind, data["url"])

    asset = FileAsset(
        patient_id=patient_id,
        kind=kind,
        url=url_norm,
        mime_type=mime,
        title=data.get("title"),
        note=data.get("note"),
        size_bytes=data.get("size_bytes"),
        photo_phase=PhotoPhase(data["photo_phase"]) if data.get("photo_phase") else None,
        photo_order=data.get("photo_order"),
    )

    db.session.add(asset)
    db.session.commit()
    return created(file_public.dump(asset))

# Listar archivos de un paciente
@bp.get("/patients/<int:patient_id>/files")
@roles_required("admin", "doctor", "manager", "nurse")
def list_files(patient_id: int):
    p = db.session.get(Patient, patient_id)
    if not p:
        return error("Paciente no encontrado", 404)
    assets = (
        db.session.query(FileAsset)
        .filter(FileAsset.patient_id == patient_id)
        .order_by(FileAsset.kind.asc(), FileAsset.photo_phase.asc().nullsfirst(), FileAsset.photo_order.asc().nullsfirst(), FileAsset.id.desc())
        .all()
    )
    return ok({"items": file_list.dump(assets)})

# Eliminar archivo
@bp.delete("/files/<int:file_id>")
@roles_required("admin", "doctor", "manager")
def delete_file(file_id: int):
    asset = db.session.get(FileAsset, file_id)
    if not asset:
        return error("Archivo no encontrado", 404)
    db.session.delete(asset)
    db.session.commit()
    return ok({"deleted": True, "id": file_id})
