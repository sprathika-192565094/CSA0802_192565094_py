"""Task 3.4 - misuse experiment: `except Exception: pass` + a typing error in a variable name."""
from attendance_processor import parse_line, InvalidRecord

def summarise_good(lines):
    present = absent = 0
    errors = []
    for n, line in enumerate(lines, 1):
        try:
            _, _, s = parse_line(line)
            if s == "P":
                present += 1
            else:
                absent += 1
        except InvalidRecord as e:
            errors.append((n, str(e)))
    return present, absent, errors

def summarise_misused(lines):
    present = absent = 0
    errors = []
    for n, line in enumerate(lines, 1):
        try:
            _, _, s = parse_line(line)
            if s == "P":
                presnt += 1                  # <-- typing error in variable name
            else:
                absent += 1
        except Exception:
            pass                             # <-- hides InvalidRecord AND the NameError
    return present, absent, errors

data = ["192311001,2026-10-08,P", "192311002,2026-10-08,A", "192311003,2026-10-08", "192311004,2026-10-08,L"]
print("specific handlers  :", summarise_good(data))
print("except Exception  :", summarise_misused(data))
print()
def summarise_typo_specific(lines):
    """Same typing error, but only the specific exception is handled."""
    present = absent = 0
    for line in lines:
        try:
            _, _, s = parse_line(line)
            if s == "P":
                presnt += 1
            else:
                absent += 1
        except InvalidRecord:
            pass
    return present, absent

# With specific handlers the typing error is NOT hidden - it surfaces at once:
try:
    summarise_typo_specific(data)
except Exception as e:
    print("specific except   : crashed visibly ->", type(e).__name__ + ":", e)
