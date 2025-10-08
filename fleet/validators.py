import re
from django.core.exceptions import ValidationError

NAME_RE = re.compile(r'^[A-Za-z0-9_-]+$')
CODE_RE = re.compile(r'^[A-Z0-9_]+$')

def validate_medication_name(value: str):
    if not NAME_RE.fullmatch(value or ''):
        raise ValidationError("Name must contain only letters, numbers, '-', '_'")

def validate_medication_code(value: str):
    if not CODE_RE.fullmatch(value or ''):
        raise ValidationError("Code must contain only UPPERCASE letters, numbers, '_'")
