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
