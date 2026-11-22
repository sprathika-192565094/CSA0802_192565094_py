"""B1 Alternative concept: the same cleaning with pandas (read_csv, to_numeric, dropna-style masks, vectorised conversion)
compared with the csv-module + loops version, at 1,000, 100,000 and 1,000,000 rows (time and peak memory).
Every measurement runs in its own process so that the peak memory (maximum resident set size) is not mixed up."""
import json
import os
import resource
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
# (the parent process stays tiny: ru_maxrss of a child inherits the parent's peak, so heavy imports are done lazily in the children)

TMP = "/tmp/aq_clean_bench"


def clean_pandas(path):
    import aqlib
    import pandas as pd
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    known = {n.lower(): n for n, _ in aqlib.STATIONS}
    key = df["station"].str.split().str.join(" ")
    df["station"] = key.str.lower().map(known).fillna(key.str.title())
    d = pd.to_datetime(df["date"].str.strip(), format="%Y-%m-%d", errors="coerce")
    d = d.fillna(pd.to_datetime(df["date"].str.strip(), format="%d/%m/%Y", errors="coerce"))
    df["date"] = d.dt.strftime("%Y-%m-%d")
    df["hour"] = pd.to_numeric(df["hour"].str.strip(), errors="coerce")
    df = df[df["date"].notna() & df["hour"].between(0, 23)]
    df = df.drop_duplicates(subset=["station", "date", "hour"], keep="first")
    for col in ("pm25", "pm10", "no", "temperature"):
        df[col] = pd.to_numeric(df[col].str.strip(), errors="coerce")           # blank, NA, ERR -> NaN
    f = df["station"].isin(aqlib.FAHRENHEIT)
    df.loc[f, "temperature"] = (df.loc[f, "temperature"] - 32) * 5 / 9
    for col, (lo, hi) in aqlib.LIMITS.items():
        df[col] = df[col].where(df[col].between(lo, hi))                      # impossible values -> NaN
    df = df.sort_values(["station", "date", "hour"])
    cols = ["pm25", "pm10", "no", "temperature"]
    df[cols] = df.groupby("station")[cols].ffill(limit=aqlib.FILL_LIMIT)
    return df


def clean_python(path):
    import csv
    import aqlib
    with open(path, newline="") as f:
        return aqlib.clean_rows(csv.DictReader(f))


def child(method, path):
    t = time.perf_counter()
    out = clean_pandas(path) if method == "pandas" else clean_python(path)
    elapsed = time.perf_counter() - t
    rows = len(out)
    print(json.dumps(dict(method=method, seconds=elapsed, rows=rows, peak_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)))


def make_file(n, path):
    import aqlib
    from datetime import date
    days = max(1, -(-n // (12 * 24)))
    truth = aqlib.generate_clean_truth(aqlib.STATIONS, date(2026, 1, 1), days, seed=5)[:n]
    raw = aqlib.make_raw(truth, seed=6)
    open(path, "w", newline="").write(aqlib.raw_to_csv_text(raw))
    return len(raw)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--run":
        child(sys.argv[2], sys.argv[3])
        sys.exit()
    if len(sys.argv) == 4 and sys.argv[1] == "--make":
        print(make_file(int(sys.argv[2]), sys.argv[3]))
        sys.exit()
    if len(sys.argv) == 3 and sys.argv[1] == "--agree":
        py, pdf = clean_python(sys.argv[2]), clean_pandas(sys.argv[2])
        mism = 0
        for r, (_, q) in zip(py, pdf.iterrows()):
            if (r[0], r[1], r[2]) != (q["station"], q["date"], int(q["hour"])):
                mism += 1
                continue
            for a, b in zip(r[3:], (q["pm25"], q["pm10"], q["no"], q["temperature"])):
                if (a is None) != (b != b) or (a is not None and abs(a - b) > 0.11):
                    mism += 1
                    break
        print(json.dumps(dict(py=len(py), pandas=len(pdf), mismatches=mism)))
        sys.exit()
    os.makedirs(TMP, exist_ok=True)
    print("=== Do the two versions agree? (1,000 rows, every value compared) ===")
    p1 = f"{TMP}/rows_1000.csv"
    n_in = int(subprocess.run([sys.executable, __file__, "--make", "1000", p1], capture_output=True, text=True).stdout.strip())
    ag = json.loads(subprocess.run([sys.executable, __file__, "--agree", p1], capture_output=True, text=True).stdout.strip().splitlines()[-1])
    same_rows, mism = ag["py"] == ag["pandas"], ag["mismatches"]
    print(f"rows in {n_in:,}; rows out python {ag['py']:,}, pandas {ag['pandas']:,}; same row count: {same_rows}; rows that differ: {mism}")
    results = []
    print("\n=== Time and peak memory (each run in a separate process; file read included) ===")
    print(f"{'rows':>10} | {'python time':>12} {'peak MB':>8} | {'pandas time':>12} {'peak MB':>8} | speed-up")
    for n in (1_000, 100_000, 1_000_000):
        path = f"{TMP}/rows_{n}.csv"
        if not os.path.exists(path):
            subprocess.run([sys.executable, __file__, "--make", str(n), path], capture_output=True, text=True, timeout=250)
        row = {"n": n, "file_mb": os.path.getsize(path) / 1e6}
        for method in ("python", "pandas"):
            best = None
            for _ in range(3 if n < 1_000_000 else 1):
                o = subprocess.run([sys.executable, __file__, "--run", method, path], capture_output=True, text=True, timeout=280)
                d = json.loads(o.stdout.strip().splitlines()[-1])
                if best is None or d["seconds"] < best["seconds"]:
                    best = d
            row[method] = best
        results.append(row)
        print(f"{n:>10,} | {row['python']['seconds']:>10.3f} s {row['python']['peak_mb']:>8.0f} | {row['pandas']['seconds']:>10.3f} s {row['pandas']['peak_mb']:>8.0f} | {row['python']['seconds'] / row['pandas']['seconds']:>6.1f}x")
    json.dump(dict(agree=dict(same_rows=same_rows, mismatches=mism), rows=results), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_pandas.json"), "w"), indent=1)
