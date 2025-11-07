from marshmallow import Schema, fields, validate, validates, ValidationError
from ..models.file_asset import FileKind, PhotoPhase
import re

# Validaciones simples por extensión de URL (no descargamos el binario)
IMG_EXT = (".webp", ".jpg", ".jpeg", ".png")
PDF_EXT = (".pdf",)

def _guess_mime_from_url(url: str) -> str | None:
    u = url.lower()
    if u.endswith(PDF_EXT):
        return "application/pdf"
    if u.endswith(IMG_EXT):
        # preferimos webp
        return "image/webp" if u.endswith(".webp") else "image/jpeg"
    return None

class FileCreateSchema(Schema):
    kind = fields.Str(required=True, validate=validate.OneOf([k.value for k in FileKind]))
    url = fields.Url(required=True, error_messages={"invalid": "URL inválida"})
    title = fields.Str(allow_none=True, validate=validate.Length(max=255))
    note = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    size_bytes = fields.Int(allow_none=True)

    # Solo para fotos
    photo_phase = fields.Str(allow_none=True, validate=validate.OneOf([p.value for p in PhotoPhase]))
    photo_order = fields.Int(allow_none=True)

    @validates("url")
    def _v_url(self, value, **kwargs):
        mime = _guess_mime_from_url(value)
        if not mime:
            raise ValidationError("Extensión no soportada. Usa PDF o imagen (.webp/.jpg/.png)")

class FilePublicSchema(Schema):
    id = fields.Int(dump_only=True)
    patient_id = fields.Int()
    kind = fields.Str()
    photo_phase = fields.Str(allow_none=True)
    photo_order = fields.Int(allow_none=True)
    url = fields.Url()
    mime_type = fields.Str(allow_none=True)
    title = fields.Str(allow_none=True)
    note = fields.Str(allow_none=True)
    size_bytes = fields.Int(allow_none=True)
    created_at = fields.DateTime()
