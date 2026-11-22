"""B2 - Engineer adversarial data: bad files, SQL injection, sentiment traps, executemany vs execute."""
import csv
import io
import json
import os
import sqlite3
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import sentiment

res = {}
GOOD = "station,date,hour,pm25,pm10,no,temperature\nAdyar,2026-10-01,00,48,90,20,30.1\nGuindy,2026-10-01,00,95,170,40,29.9\n"
REQUIRED = ["station", "date", "hour", "pm25"]


# ---------------------------------------------------------------- 1. files
def naive_loader(data: bytes):
    """What a first version does: trust the file."""
    rows = list(csv.DictReader(io.StringIO(data.decode("utf-8"))))
    return [(r["station"], r["date"], float(r["pm25"]), float(r["pm10"])) for r in rows]


def robust_loader(data: bytes):
    """Returns (rows, messages). Never crashes; refuses a file it cannot trust and says why."""
    msgs = []
    if not data.strip():
        return [], ["REJECTED: file is empty"]
    # encoding: BOM first, then UTF-8, then Windows-1252 (which never fails)
    for enc in ("utf-8-sig", "utf-16"):
        if enc == "utf-16" and not data.startswith((b"\xff\xfe", b"\xfe\xff")):
            continue
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            text = None
    else:
        text = None
    if text is None:
        text = data.decode("cp1252", errors="replace")
        msgs.append("WARNING: decoded as Windows-1252")
    first = text.splitlines()[0]
    try:
        dialect = csv.Sniffer().sniff(first, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    if dialect.delimiter != ",":
        msgs.append(f"WARNING: delimiter {dialect.delimiter!r} detected")
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    header = [h.strip().lower() for h in (reader.fieldnames or [])]
    missing = [c for c in REQUIRED if c not in header]
    if missing:
        return [], msgs + [f"REJECTED: required column(s) missing: {missing}; found {header}"]
    reader.fieldnames = header
    rows = []
    for r in reader:
        rows.append(r)
    return rows, msgs + [f"OK: {len(rows)} data rows"]


files = {
    "good file": GOOD.encode(),
    "missing column (pm25 absent)": b"station,date,hour,pm10,no,temperature\nAdyar,2026-10-01,00,90,20,30.1\n",
    "wrong delimiter (;)": GOOD.replace(",", ";").encode(),
    "UTF-16 with BOM (Windows export)": GOOD.encode("utf-16"),
    "Windows-1252 text (station 'Kodungaiy\u00fcr')": GOOD.replace("Adyar", "Kodungaiy\u00fcr").encode("cp1252"),
    "empty file": b"",
    "header only": GOOD.splitlines()[0].encode() + b"\n",
}
print("=== 1. Adversarial files: first version (trusts the file) against the hardened loader ===")
out1 = {}
for name, data in files.items():
    try:
        r = naive_loader(data)
        naive = f"returned {len(r)} rows" + (" (silently nothing!)" if not r else "")
    except Exception as e:                                           # noqa
        naive = f"CRASH {type(e).__name__}: {str(e)[:70]}"
    rows, msgs = robust_loader(data)
    out1[name] = dict(naive=naive, robust=msgs)
    print(f"- {name}\n     first version : {naive}\n     hardened      : {' | '.join(msgs)}")
res["files"] = out1

# ---------------------------------------------------------------- 2. SQL injection
print("\n=== 2. A station name containing a quote ===")
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE aq (station TEXT, day TEXT, pm25 REAL)")
con.executemany("INSERT INTO aq VALUES (?, ?, ?)", [("Adyar", "2026-10-01", 48.0), ("Adyar", "2026-10-04", 60.0), ("Guindy", "2026-10-01", 95.0),
                                                   ("Guindy", "2026-10-03", 121.0), ("Women's Road", "2026-10-01", 70.0)])


def by_concat(name):
    return con.execute("SELECT AVG(pm25) FROM aq WHERE station = '" + name + "'").fetchone()[0]


def by_placeholder(name):
    return con.execute("SELECT AVG(pm25) FROM aq WHERE station = ?", (name,)).fetchone()[0]


inj = {}
for label_, name in (("normal name", "Adyar"), ("name with a quote", "Women's Road"), ("injection  Adyar' OR '1'='1", "Adyar' OR '1'='1"),
                     ("stacked statement  x'; DROP TABLE aq; --", "x'; DROP TABLE aq; --")):
    try:
        a = "average " + str(by_concat(name))
    except Exception as e:                                           # noqa
        a = f"{type(e).__name__}: {e}"
    try:
        b = "average " + str(by_placeholder(name))
    except Exception as e:                                           # noqa
        b = f"{type(e).__name__}: {e}"
    inj[label_] = dict(concat=a, placeholder=b)
    print(f"{label_}\n     built with +  : {a}\n     with ? marker : {b}")
print("table still exists after the stacked-statement attempt:", con.execute("SELECT COUNT(*) FROM aq").fetchone()[0], "rows")
print("true average of ALL rows (what the injection leaked):", round(con.execute("SELECT AVG(pm25) FROM aq").fetchone()[0], 2))
res["injection"] = inj

# ---------------------------------------------------------------- 3. sentiment traps
print("\n=== 3. Sentiment scorer: sarcasm, double negatives, mixed opinions and other traps ===")
cases = [
    ("Oh sure, the officers were so helpful, they ignored me for an hour.", "negative", "sarcasm"),
    ("I would not say the roads are not clean.", "positive", "double negative"),
    ("The roads are clean but the air is bad.", "mixed", "mixed opinion"),
    ("The staff were never really helpful.", "negative", "negator not directly before the word"),
    ("The service isn't helpful.", "negative", "contraction n't"),
    ("Terrible stench near the dump.", "negative", "words outside the word list"),
    ("Smoke!", "negative", "punctuation attached to the word"),
    ("Not bad, service improved.", "positive", "negation works (from the question)"),
    ("Roads are CLEAN and the bus was FAST.", "positive", "upper case works"),
    ("No smoke today.", "positive", "negation works"),
]
fails = 0
rows3 = []
for text, human, kind in cases:
    s = sentiment.score(text)
    got = sentiment.label(text)
    ok = got == human
    fails += not ok
    rows3.append(dict(text=text, human=human, scorer=got, score=s, kind=kind, ok=ok))
    print(f"{'OK  ' if ok else 'FAIL'} | scorer {got:8} (score {s:+d}) | my reading {human:8} | {kind}\n       {text}")
print(f"scorer wrong on {fails} of {len(cases)} adversarial sentences")
res["sentiment"] = rows3

# ---------------------------------------------------------------- 4. executemany vs execute in a loop
print("\n=== 4. executemany() compared with execute() in a loop (seconds, best of 3) ===")
data_all = [("Adyar", f"2026-10-{d:02d}", float(d)) for d in range(1, 29)]


def make(n):
    return [("Station%d" % (i % 50), "2026-10-01", i * 0.5) for i in range(n)]


def run(method, rows, path):
    if path != ":memory:" and os.path.exists(path):
        os.remove(path)
    c = sqlite3.connect(path)
    c.execute("CREATE TABLE aq (station TEXT, day TEXT, pm25 REAL)")
    t = time.perf_counter()
    if method == "executemany":
        c.executemany("INSERT INTO aq VALUES (?, ?, ?)", rows)
        c.commit()
    elif method == "execute loop, one commit":
        for r in rows:
            c.execute("INSERT INTO aq VALUES (?, ?, ?)", r)
        c.commit()
    else:
        for r in rows:
            c.execute("INSERT INTO aq VALUES (?, ?, ?)", r)
            c.commit()
    elapsed = time.perf_counter() - t
    n = c.execute("SELECT COUNT(*) FROM aq").fetchone()[0]
    c.close()
    assert n == len(rows)
    return elapsed


print(f"{'rows':>8} | {'executemany':>12} {'execute loop':>13} {'loop / many':>12} | on disk: {'executemany':>12} {'loop, commit each row':>22}")
rows4 = []
for n in (1_000, 10_000, 100_000):
    d = make(n)
    mem_a = min(run("executemany", d, ":memory:") for _ in range(3))
    mem_b = min(run("execute loop, one commit", d, ":memory:") for _ in range(3))
    disk_a = min(run("executemany", d, "/tmp/aq_b2.db") for _ in range(2))
    disk_c = min(run("commit each", make(min(n, 1000)), "/tmp/aq_b2.db") for _ in range(1)) if n == 1_000 else None
    rows4.append(dict(n=n, many=mem_a, loop=mem_b, disk_many=disk_a, disk_commit_each=disk_c))
    print(f"{n:>8,} | {mem_a:>12.4f} {mem_b:>13.4f} {mem_b / mem_a:>11.2f}x | {'':>9}{disk_a:>12.4f} {('%.3f (1,000 rows)' % disk_c) if disk_c else 'not run':>22}")
res["insert"] = rows4
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"), "w"), indent=1)
