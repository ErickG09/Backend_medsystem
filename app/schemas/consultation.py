from marshmallow import Schema, fields, validate
from ..utils.time import to_cdmx

class ConsultationCreateSchema(Schema):
    patient_id = fields.Int(required=True)
    professional_id = fields.Int(allow_none=True)  # doctor/enfermera
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    datetime = fields.DateTime(required=True)  # ISO 8601 (front manda en local CDMX o UTC)
    notes = fields.Str(allow_none=True, validate=validate.Length(max=4000))
    products = fields.Str(allow_none=True, validate=validate.Length(max=2000))

class ConsultationUpdateSchema(Schema):
    professional_id = fields.Int(allow_none=True)
    title = fields.Str(validate=validate.Length(min=1, max=200))
    datetime = fields.DateTime()
    notes = fields.Str(allow_none=True, validate=validate.Length(max=4000))
    products = fields.Str(allow_none=True, validate=validate.Length(max=2000))

class ConsultationPublicSchema(Schema):
    id = fields.Int()
    patient_id = fields.Int()
    professional_id = fields.Int(allow_none=True)
    title = fields.Str()
    datetime = fields.DateTime()
    notes = fields.Str(allow_none=True)
    products = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    # bandera calculada en /history
    is_last = fields.Boolean(dump_only=True)
