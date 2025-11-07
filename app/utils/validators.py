from email_validator import validate_email, EmailNotValidError
import phonenumbers

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False

def is_valid_phone(number: str, region: str = "MX") -> bool:
    try:
        p = phonenumbers.parse(number, region)
        return phonenumbers.is_valid_number(p)
    except Exception:
        return False
