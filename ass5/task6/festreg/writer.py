"""All output files are written here."""
import os


def _safe(name):
    return "".join(c if c.isalnum() else "_" for c in name).strip("_").lower()


def write_master(path, students):
    with open(path, "w", encoding="utf-8") as f:
        f.write("regno,name,department,email,events\n")
        for regno in sorted(students):
            s = students[regno]
            f.write(f"{regno},{s['name']},{s['dept']},{s['email']},{';'.join(s['events'])}\n")


def write_event_files(folder, event_map):
    os.makedirs(folder, exist_ok=True)
    for event in sorted(event_map):
        with open(os.path.join(folder, _safe(event) + ".txt"), "w", encoding="utf-8") as f:
            f.write(f"Participants - {event} ({len(event_map[event])})\n")
            for regno, name in sorted(event_map[event]):
                f.write(f"{regno},{name}\n")


def write_summary(path, stats, event_map, dept_count):
    with open(path, "w", encoding="utf-8") as f:
        f.write("FEST REGISTRATION SUMMARY\n=========================\n")
        for key in ("files_read", "files_missing", "lines_read", "accepted", "duplicates", "invalid"):
            f.write(f"{key.replace('_', ' ').capitalize():22}: {stats[key]}\n")
        f.write("\nParticipants per event\n")
        for e in sorted(event_map):
            f.write(f"  {e:20}: {len(event_map[e])}\n")
        f.write("\nRegistrations per department\n")
        for d in sorted(dept_count):
            f.write(f"  {d:20}: {dept_count[d]}\n")


def write_error_log(path, errors):
    with open(path, "w", encoding="utf-8") as f:
        for source, line_no, kind, message in errors:
            where = source if line_no is None else f"{source}:{line_no}"
            f.write(f"{where} | {kind} | {message}\n")
