"""B3 - Daily mean PM2.5 per station: plain Python loops (csv module), pandas groupby, SQL GROUP BY."""
import cProfile
import csv
import io
import json
import os
import pstats
import sqlite3
import statistics
import sys
import time
import tracemalloc

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = "/tmp/aq_b3"
os.makedirs(TMP, exist_ok=True)
res = {}


def make_csv(n_stations, path, days=365, seed=3, blank_rate=0.02):
    """station,date,hour,pm25 - about 8,760 hourly readings per station; 2 % of the readings are blank (missing)."""
    rng = np.random.default_rng(seed)
    n = n_stations * days * 24
    st = np.repeat(np.array([f"S{i:03d}" for i in range(n_stations)]), days * 24)
    d = np.tile(np.repeat(pd.date_range("2026-01-01", periods=days).strftime("%Y-%m-%d").to_numpy(), 24), n_stations)
    h = np.tile(np.arange(24), n_stations * days)
    base = np.repeat(rng.uniform(30, 90, n_stations), days * 24)
    pm = np.round(base + 25 * np.exp(-((h - 8) ** 2) / 8) + rng.normal(0, 8, n), 1).clip(2)
    s = pd.Series(pm.astype(str))
    s[rng.random(n) < blank_rate] = ""
    pd.DataFrame({"station": st, "date": d, "hour": h, "pm25": s}).to_csv(path, index=False)
    return n


# ---------------------------------------------------------------- the three methods
def read_rows(path):
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            yield r


def daily_loops(path):
    groups = {}
    for r in read_rows(path):
        if r["pm25"] == "":
            continue
        groups.setdefault((r["station"], r["date"]), []).append(float(r["pm25"]))
    return {k: statistics.mean(v) for k, v in groups.items()}


def daily_running(path):
    """Alternative concept: one pass with a running sum and a count per (station, day); no list of readings is kept."""
    acc = {}
    for r in read_rows(path):
        if r["pm25"] == "":
            continue
        a = acc.setdefault((r["station"], r["date"]), [0.0, 0])
        a[0] += float(r["pm25"])
        a[1] += 1
    return {k: s / c for k, (s, c) in acc.items()}


def daily_pandas(path):
    df = pd.read_csv(path)
    return df.groupby(["station", "date"])["pm25"].mean().to_dict()


def load_sql(path, con):
    con.execute("CREATE TABLE aq (station TEXT, day TEXT, hour INTEGER, pm25 REAL)")
    with open(path, newline="") as f:
        rd = csv.reader(f)
        next(rd)
        con.executemany("INSERT INTO aq VALUES (?, ?, ?, ?)", ((a, b, int(c), float(d) if d != "" else None) for a, b, c, d in rd))
    con.commit()


SQL = "SELECT station, day, AVG(pm25) FROM aq GROUP BY station, day"


def daily_sql(path):
    con = sqlite3.connect(":memory:")
    load_sql(path, con)
    out = {(s, d): m for s, d, m in con.execute(SQL)}
    con.close()
    return out


def agree(a, b, tol=1e-6):
    if a.keys() != b.keys():
        return False
    return all(abs(a[k] - b[k]) <= tol for k in a if not (a[k] != a[k] and b[k] != b[k]))


def best(fn, *a, repeat=3):
    r = []
    for _ in range(repeat):
        t = time.perf_counter(); out = fn(*a); r.append(time.perf_counter() - t)
    return min(r), out


if __name__ == "__main__":
    print("=== B3.1 Correctness on small data (2 stations, 3 days, hourly, some blanks) ===")
    small = f"{TMP}/small.csv"
    make_csv(2, small, days=3, seed=9, blank_rate=0.10)
    a, b, c, d = daily_loops(small), daily_pandas(small), daily_sql(small), daily_running(small)
    print(f"groups (station, day): loops {len(a)}, pandas {len(b)}, SQL {len(c)}, running-sum {len(d)}")
    for k in sorted(a):
        print(f"   {k[0]} {k[1]}  loops {a[k]:.4f}  pandas {b[k]:.4f}  SQL {c[k]:.4f}  running {d[k]:.4f}")
    ok_small = agree(a, b) and agree(a, c) and agree(a, d)
    print("all methods agree (tolerance 1e-6):", ok_small)
    res["small"] = dict(groups=len(a), agree=ok_small)

    print("\n=== B3.2 Increase the data size (1, 12 and 120 stations x 365 days x 24 hours) ===")
    print(f"{'stations':>8} {'rows':>10} {'file MB':>8} | {'loops':>9} {'running':>9} {'pandas':>9} | {'SQL load':>9} {'SQL query':>10} {'SQL total':>10} | agree")
    rows = []
    for n_st in (1, 12, 120):
        path = f"{TMP}/s{n_st}.csv"
        n = make_csv(n_st, path)
        rep = 3 if n_st < 120 else 1
        t_l, ra = best(daily_loops, path, repeat=rep)
        t_r, rr = best(daily_running, path, repeat=rep)
        t_p, rp = best(daily_pandas, path, repeat=rep)
        con = sqlite3.connect(":memory:")
        t0 = time.perf_counter(); load_sql(path, con); t_load = time.perf_counter() - t0
        t_q, _ = best(lambda: con.execute(SQL).fetchall(), repeat=rep)
        rs = {(s, dd): m for s, dd, m in con.execute(SQL)}
        con.close()
        ok = agree(ra, rp) and agree(ra, rs) and agree(ra, rr)
        row = dict(stations=n_st, rows=n, file_mb=os.path.getsize(path) / 1e6, loops=t_l, running=t_r, pandas=t_p, sql_load=t_load, sql_query=t_q, agree=ok, groups=len(ra))
        rows.append(row)
        print(f"{n_st:>8} {n:>10,} {row['file_mb']:>8.1f} | {t_l:>8.3f}s {t_r:>8.3f}s {t_p:>8.3f}s | {t_load:>8.3f}s {t_q:>9.3f}s {t_load + t_q:>9.3f}s | {ok}")
    res["sizes"] = rows

    print("\n=== B3.3 Profile the plain-Python version (12 stations, 105,120 rows) with cProfile ===")
    path = f"{TMP}/s12.csv"
    pr = cProfile.Profile()
    pr.enable(); daily_loops(path); pr.disable()
    buf = io.StringIO()
    ps = pstats.Stats(pr, stream=buf).sort_stats("tottime")
    ps.print_stats(8)
    text = buf.getvalue()
    print("\n".join(l for l in text.splitlines() if l.strip())[:2600])
    top = sorted(((v[2], f"{k[2]} ({os.path.basename(k[0])}:{k[1]})", v[0]) for k, v in ps.stats.items()), reverse=True)[:6]
    cum = sorted(((v[3], f"{k[2]}", v[0]) for k, v in ps.stats.items() if k[2] in ("mean", "daily_loops", "read_rows", "__next__", "_sum", "<dictcomp>")), reverse=True)
    res["profile_top"] = [(round(t, 4), n, c) for t, n, c in top]
    print("\nfunctions with the highest own time (tottime):", [(round(t, 3), n) for t, n, c in top[:4]])
    print("cumulative time of the main parts:", [(round(t, 3), n, c) for t, n, c in cum])

    print("\n=== Memory of the two Python designs (12 stations; tracemalloc peak) ===")
    mem = {}
    for name, fn in (("store all readings, then statistics.mean", daily_loops), ("running sum and count (one pass)", daily_running)):
        tracemalloc.start(); out = fn(path); mem[name] = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
        print(f"  {name:42} peak {mem[name] / 1e6:7.2f} MB   result entries: {len(out):,}")
    res["mem"] = mem
    t_l12 = rows[1]["loops"]; t_r12 = rows[1]["running"]
    print(f"  time at 12 stations: store-then-mean {t_l12:.3f} s, running sum {t_r12:.3f} s")
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
