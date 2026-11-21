"""Q4 - Building long text: += or join()?   Monthly SMS bill statement."""
import io
import json
import time

# ------------------------------------------------------------------ the program given in the question
items = [f"Item{i}:Rs{i % 50}" for i in range(200_000)]


def build_plus(parts):
    text = ""
    for p in parts:
        text += p + ";"
    return text


def build_join(parts):
    # TODO 1 (completed): build the same text using a single str.join() call
    return ";".join(parts) + ";"


def build_fstring(parts):
    """Method 3: one f-string per line, lines collected and joined once."""
    return "".join(f"{p};" for p in parts)


def build_stringio(parts):
    """Alternative concept: write line by line into an in-memory text buffer."""
    buf = io.StringIO()
    for p in parts:
        buf.write(p)
        buf.write(";")
    return buf.getvalue()


def build_file(parts, path="statement_out.txt"):
    """Alternative concept: write line by line directly to a file (nothing large is kept in memory)."""
    with open(path, "w") as f:
        for p in parts:
            f.write(p + ";")
    with open(path) as f:
        return f.read()


class Statement:
    """Demonstrates that the CPython '+=' shortcut only works for plain local variables."""
    def __init__(self):
        self.text = ""


def build_plus_attribute(parts):
    s = Statement()
    for p in parts:
        s.text += p + ";"             # target is an attribute: the in-place optimisation cannot apply
    return s.text


def timed(fn, parts):
    start = time.perf_counter()
    out = fn(parts)
    return time.perf_counter() - start, out


if __name__ == "__main__":
    # ---- the exact program from the question
    start = time.perf_counter()
    a = build_plus(items)
    t_plus = time.perf_counter() - start
    start = time.perf_counter()
    b = build_join(items)
    t_join = time.perf_counter() - start
    print("same text:", a == b, "| length:", len(b))
    print(f"+= time: {t_plus:.4f} s   join time: {t_join:.4f} s")

    # ---- full experiment
    methods = {
        "+= loop": build_plus,
        "list + join": build_join,
        "f-string + join": build_fstring,
        "StringIO": build_stringio,
        "file write": build_file,
        "+= on attribute": build_plus_attribute,
    }
    sizes = [1_000, 10_000, 200_000]
    RUNS = 3
    results = {}
    print("\nRaw timings in seconds (3 runs each) and average")
    for n in sizes:
        parts = items[:n]
        reference = build_join(parts)
        for name, fn in methods.items():
            if name == "+= on attribute" and n > 50_000:
                continue                                  # quadratic copying: skipped at 200,000
            runs = []
            for _ in range(RUNS):
                t, out = timed(fn, parts)
                assert out == reference
                runs.append(t)
            avg = sum(runs) / RUNS
            results[f"{name}|{n}"] = dict(runs=runs, avg=avg)
            print(f"n={n:>7,}  {name:16} " + "  ".join(f"{r:.5f}" for r in runs) + f"   avg={avg:.5f}")
    json.dump(dict(results=results, program_t_plus=t_plus, program_t_join=t_join, length=len(b)),
              open("results.json", "w"), indent=1)
