"""Organisation (b): one reusable module."""
import os


def read_records(folder):
    """Read every daily file once. Returns (records, bad_lines)."""
    records = {}      # {regno: {date: 'P' or 'A'}}
    bad_lines = []    # [(file_name, line_no, text)]
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".csv"):
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) != 3 or parts[2] not in ("P", "A"):
                    bad_lines.append((name, n, line))
                    continue
                regno, date, status = parts
                records.setdefault(regno, {})[date] = status
    return records, bad_lines


def percentage(records):
    """Attendance percentage per student (recorded days only)."""
    result = {}
    for regno, days in records.items():
        present = sum(1 for s in days.values() if s == "P")
        result[regno] = round(100 * present / len(days), 2)
    return result


def below_threshold(pcts, limit=75):
    """Register numbers strictly below the limit."""
    return sorted(r for r, p in pcts.items() if p < limit)


def three_day_absent(records, run=3):
    """Students absent on `run` consecutive recorded days (new requirement)."""
    flagged = []
    for regno, days in records.items():
        streak = 0
        for date in sorted(days):
            streak = streak + 1 if days[date] == "A" else 0
            if streak >= run:
                flagged.append(regno)
                break
    return sorted(flagged)


def write_summary(path, pcts):
    with open(path, "w", encoding="utf-8") as f:
        f.write("regno,percentage\n")
        for regno in sorted(pcts):
            f.write(f"{regno},{pcts[regno]}\n")


def write_list(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(item + "\n")


def write_errors(path, bad_lines):
    with open(path, "w", encoding="utf-8") as f:
        for name, n, text in bad_lines:
            f.write(f"{name}:{n}: damaged line: {text}\n")
