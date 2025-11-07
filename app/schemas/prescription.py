from marshmallow import Schema, fields, validate

class PrescriptionCreateSchema(Schema):
    # O seleccionas paciente...
    patient_id = fields.Int(required=False)
    # ...o creas uno mínimo “rápido” (opcional). Ver notas en ruta.
    new_patient = fields.Dict(required=False)

    consultation_id = fields.Int(allow_none=True)
    professional_id = fields.Int(allow_none=True)

    issued_at = fields.DateTime(required=False)  # si no envían, se pone “ahora CDMX”

    # Signos vitales
    temp_c = fields.Float(allow_none=True)
    bp_sys = fields.Int(allow_none=True)
    bp_dia = fields.Int(allow_none=True)
    heart_rate = fields.Int(allow_none=True)
    resp_rate = fields.Int(allow_none=True)
    bmi = fields.Float(allow_none=True)
    spo2 = fields.Int(allow_none=True)

    # Contenido
    diagnosis = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    prescription_text = fields.Str(allow_none=True, validate=validate.Length(max=4000))
    care_instructions = fields.Str(allow_none=True, validate=validate.Length(max=4000))
    products = fields.Str(allow_none=True, validate=validate.Length(max=2000))

class PrescriptionUpdateSchema(Schema):
    issued_at = fields.DateTime()
    temp_c = fields.Float(allow_none=True)
    bp_sys = fields.Int(allow_none=True)
    bp_dia = fields.Int(allow_none=True)
    heart_rate = fields.Int(allow_none=True)
    resp_rate = fields.Int(allow_none=True)
    bmi = fields.Float(allow_none=True)
    spo2 = fields.Int(allow_none=True)

    diagnosis = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    prescription_text = fields.Str(allow_none=True, validate=validate.Length(max=4000))
    care_instructions = fields.Str(allow_none=True, validate=validate.Length(max=4000))
    products = fields.Str(allow_none=True, validate=validate.Length(max=2000))

class PrescriptionPublicSchema(Schema):
    id = fields.Int()
    patient_id = fields.Int()
    consultation_id = fields.Int(allow_none=True)
    professional_id = fields.Int(allow_none=True)
    issued_at = fields.DateTime()

    temp_c = fields.Float(allow_none=True)
    bp_sys = fields.Int(allow_none=True)
    bp_dia = fields.Int(allow_none=True)
    heart_rate = fields.Int(allow_none=True)
    resp_rate = fields.Int(allow_none=True)
    bmi = fields.Float(allow_none=True)
    spo2 = fields.Int(allow_none=True)

    diagnosis = fields.Str(allow_none=True)
    prescription_text = fields.Str(allow_none=True)
    care_instructions = fields.Str(allow_none=True)
    products = fields.Str(allow_none=True)

    created_at = fields.DateTime()
    updated_at = fields.DateTime()
