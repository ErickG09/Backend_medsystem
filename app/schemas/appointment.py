from marshmallow import Schema, fields, validate
from ..models.appointment import AppointmentStatus, AppointmentType

class AppointmentCreateSchema(Schema):
    # O seleccionas paciente existente...
    patient_id = fields.Int(required=False)
    # ...o creas uno rápido
    new_patient = fields.Dict(required=False)

    professional_id = fields.Int(allow_none=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))

    # el front manda CDMX o UTC. Si viene sin tz, asumimos CDMX (lo convertimos en ruta)
    start_at = fields.DateTime(required=True)
    duration_min = fields.Int(required=True)  # ej. 30, 45, 60

    status = fields.Str(required=False, validate=validate.OneOf([s.value for s in AppointmentStatus]))
    appt_type = fields.Str(required=False, validate=validate.OneOf([t.value for t in AppointmentType]))

    treatment = fields.Str(allow_none=True, validate=validate.Length(max=300))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=4000))

class AppointmentUpdateSchema(Schema):
    professional_id = fields.Int(allow_none=True)
    title = fields.Str(validate=validate.Length(min=1, max=200))
    start_at = fields.DateTime()
    duration_min = fields.Int()
    status = fields.Str(validate=validate.OneOf([s.value for s in AppointmentStatus]))
    appt_type = fields.Str(validate=validate.OneOf([t.value for t in AppointmentType]))
    treatment = fields.Str(allow_none=True, validate=validate.Length(max=300))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=4000))

class AppointmentPublicSchema(Schema):
    id = fields.Int()
    patient_id = fields.Int()
    professional_id = fields.Int(allow_none=True)
    title = fields.Str()
    start_at = fields.DateTime()
    end_at = fields.DateTime()
    duration_min = fields.Int()
    status = fields.Str()
    appt_type = fields.Str()
    treatment = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
