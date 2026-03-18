"""Shared validation helpers for user fields."""
import re


def normalize_optional_aadhaar(value):
    """
    If value is empty/None, return None.
    Otherwise strip spaces/dashes; must be exactly 12 digits.
    Raises ValueError with message if non-empty but invalid.
    """
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
    else:
        s = str(value).strip()
        if not s:
            return None
    digits = re.sub(r'[\s-]', '', s)
    if not re.fullmatch(r'\d{12}', digits):
        raise ValueError('Aadhaar must be exactly 12 digits (spaces/dashes allowed).')
    return digits
