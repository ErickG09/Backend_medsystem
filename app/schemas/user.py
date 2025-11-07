from marshmallow import Schema, fields, validate, validates, ValidationError
from ..models.user import UserRole
from ..utils.validators import is_valid_email

class UserBaseSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    date_of_birth = fields.Date(allow_none=True)
    photo_url = fields.Url(allow_none=True)

    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    role = fields.Str(required=True, validate=validate.OneOf([r.value for r in UserRole]))
    is_active = fields.Bool(dump_only=True)
    age = fields.Int(dump_only=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates("email")
    def _email(self, value, **kwargs):
        if not is_valid_email(value):
            raise ValidationError("Email inválido")

class UserCreateSchema(UserBaseSchema):
    password = fields.Str(required=True, load_only=True)

class UserUpdateSchema(Schema):
    first_name = fields.Str(validate=validate.Length(min=1, max=100))
    last_name = fields.Str(validate=validate.Length(min=1, max=150))
    date_of_birth = fields.Date(allow_none=True)
    photo_url = fields.Url(allow_none=True)
    email = fields.Email()
    username = fields.Str(validate=validate.Length(min=3, max=50))
    role = fields.Str(validate=validate.OneOf([r.value for r in UserRole]))
    is_active = fields.Bool()

class UserPublicSchema(UserBaseSchema):
    """Para respuestas al front (sin password)."""
    pass

class LoginSchema(Schema):
    username = fields.Str(required=False)
    email = fields.Email(required=False)
    password = fields.Str(required=True, load_only=True)
