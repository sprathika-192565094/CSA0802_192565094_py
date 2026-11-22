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
