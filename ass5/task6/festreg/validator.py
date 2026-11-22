"""Validation of one registration line using string methods only."""
from .exceptions import InvalidRecord


def valid_email(email):
    """Basic e-mail check with string methods (no regular expressions)."""
    if " " in email or email.count("@") != 1:
        return False
    local, domain = email.split("@")
    if not local or not domain:
        return False
    if "." not in domain or domain.startswith(".") or domain.endswith(".") or ".." in domain:
        return False
    return True


def validate_line(line):
    """Return (regno, name, dept, email, events) or raise InvalidRecord."""
    fields = [p.strip() for p in line.strip().split(",")]
    if len(fields) != 5:
        raise InvalidRecord(f"expected 5 fields, found {len(fields)}")
    regno, name, dept, email, event_text = fields
    if not (regno.isdigit() and len(regno) == 9):
        raise InvalidRecord(f"invalid register number {regno!r}")
    if not name or not name.replace(" ", "").replace(".", "").isalpha():
        raise InvalidRecord(f"invalid name {name!r}")
    if not dept:
        raise InvalidRecord("empty department")
    email = email.lower()
    if not valid_email(email):
        raise InvalidRecord(f"invalid e-mail {email!r}")
    events = [e.strip().title() for e in event_text.split(";") if e.strip()]
    if not events:
        raise InvalidRecord("no events chosen")
    return regno, name.title(), dept.upper(), email, events
