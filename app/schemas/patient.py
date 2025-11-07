from marshmallow import Schema, fields, validate, validates, ValidationError
from ..models.patient import Sex
from ..utils.validators import is_valid_email, is_valid_phone

# --- Create schema (con obligatorios por secciones) ---------------------------
class PatientCreateSchema(Schema):
    # Sección 1: identificación (OBLIGATORIOS)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    date_of_birth = fields.Date(required=True)
    sex = fields.Str(required=True, validate=validate.OneOf([s.value for s in Sex]))
    phone = fields.Str(required=True)
    email = fields.Email(required=True)

    photo_url = fields.Url(allow_none=True)
    address = fields.Str(allow_none=True, validate=validate.Length(max=500))

    # Sección 2: clínico (OBLIGATORIOS aquí)
    weight_kg = fields.Float(required=True)
    height_m = fields.Float(required=True)
    treatments_of_interest = fields.Str(required=True, validate=validate.Length(min=1, max=2000))

    past_history = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    allergies = fields.Str(allow_none=True, validate=validate.Length(max=2000))

    # Sección 3: consentimientos (OBLIGATORIOS)
    privacy_notice_accepted = fields.Bool(required=True)
    informed_consent_accepted = fields.Bool(required=True)

    # Contacto de emergencia (opcionales)
    emergency_full_name = fields.Str(allow_none=True, validate=validate.Length(max=200))
    emergency_phone = fields.Str(allow_none=True)
    emergency_relation = fields.Str(allow_none=True, validate=validate.Length(max=100))

    @validates("email")
    def _email(self, value, **kwargs):
        if not is_valid_email(value):
            raise ValidationError("Email inválido")

    @validates("phone")
    def _phone(self, value, **kwargs):
        if not is_valid_phone(value, region="MX"):
            raise ValidationError("Teléfono inválido")

    @validates("emergency_phone")
    def _em_phone(self, value, **kwargs):
        if value and not is_valid_phone(value, region="MX"):
            raise ValidationError("Teléfono de emergencia inválido")

    @validates("weight_kg")
    def _w(self, value, **kwargs):
        if value <= 0 or value > 500:
            raise ValidationError("Peso fuera de rango")

    @validates("height_m")
    def _h(self, value, **kwargs):
        if value <= 0 or value > 2.6:
            raise ValidationError("Estatura fuera de rango")

# --- Update schema (todo opcional, recalculamos IMC y edad si aplica) ---------
class PatientUpdateSchema(Schema):
    first_name = fields.Str(validate=validate.Length(min=1, max=100))
    last_name = fields.Str(validate=validate.Length(min=1, max=150))
    date_of_birth = fields.Date()
    sex = fields.Str(validate=validate.OneOf([s.value for s in Sex]))
    phone = fields.Str()
    email = fields.Email()

    photo_url = fields.Url(allow_none=True)
    address = fields.Str(allow_none=True, validate=validate.Length(max=500))

    weight_kg = fields.Float()
    height_m = fields.Float()
    treatments_of_interest = fields.Str(validate=validate.Length(min=1, max=2000))
    past_history = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    allergies = fields.Str(allow_none=True, validate=validate.Length(max=2000))

    privacy_notice_accepted = fields.Bool()
    informed_consent_accepted = fields.Bool()

    emergency_full_name = fields.Str(allow_none=True, validate=validate.Length(max=200))
    emergency_phone = fields.Str(allow_none=True)
    emergency_relation = fields.Str(allow_none=True, validate=validate.Length(max=100))

# --- Public schema (respuesta al front) ---------------------------------------
class PatientPublicSchema(Schema):
    id = fields.Int(dump_only=True)
    display_id = fields.Method("get_display_id", dump_only=True)

    first_name = fields.Str()
    last_name = fields.Str()
    date_of_birth = fields.Date()
    sex = fields.Str()
    phone = fields.Str()
    email = fields.Email()

    photo_url = fields.Url(allow_none=True)
    address = fields.Str(allow_none=True)

    weight_kg = fields.Float(allow_none=True)
    height_m = fields.Float(allow_none=True)
    bmi = fields.Float(allow_none=True)
    age_years = fields.Int(allow_none=True)

    past_history = fields.Str(allow_none=True)
    allergies = fields.Str(allow_none=True)
    treatments_of_interest = fields.Str(allow_none=True)

    privacy_notice_accepted = fields.Bool()
    informed_consent_accepted = fields.Bool()

    emergency_full_name = fields.Str(allow_none=True)
    emergency_phone = fields.Str(allow_none=True)
    emergency_relation = fields.Str(allow_none=True)

    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    def get_display_id(self, obj):
        return obj.display_id
