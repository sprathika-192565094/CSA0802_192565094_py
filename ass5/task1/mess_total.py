"""Task 1.2 - repaired mess-bill totaller."""
import sys
from decimal import Decimal, InvalidOperation


def process_mess_file(filename):
    """Read one mess-bill file line by line.

    Returns (report_lines, total, rejected) where rejected is a list of
    (line_number, text, reason).  Raises FileNotFoundError / OSError to the caller.
    """
    report_lines = []
    rejected = []
    total = Decimal("0")
    with open(filename, encoding="utf-8") as f:          # closed automatically
        for line_no, line in enumerate(f, 1):             # one line in memory at a time
            line = line.strip()
            if not line:                                  # ignore blank / last empty line
                continue
            parts = line.split(",")
            try:
                if len(parts) != 3:
                    raise ValueError(f"expected 3 fields, found {len(parts)}")
                amount = Decimal(parts[2].strip())        # exact paise, e.g. 1250.50
                if not amount.is_finite() or amount < 0:
                    raise ValueError("amount not a valid non-negative number")
            except (ValueError, InvalidOperation) as err:  # specific exceptions only
                reason = "amount is not a number" if isinstance(err, InvalidOperation) else str(err)
                rejected.append((line_no, line, reason))
                continue
            total += amount
            report_lines.append(f"{parts[0].strip()} {parts[1].strip()} {amount}")
    return report_lines, total, rejected


def main(filename):
    try:
        lines, total, rejected = process_mess_file(filename)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return 1
    print("\n".join(lines))                                # one join, not repeated +
    print("Total", total)
    print(f"Rejected lines: {len(rejected)}")
    for n, text, why in rejected:
        print(f"  line {n}: {why}: {text!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "mess_oct.txt"))
