"""B4.2 - Check the database at the new scale: 112 stations x 96 readings a day (every 15 minutes).
Table without any index first; then CREATE INDEX on (station, day); time the four typical queries."""
import json
import os
import sqlite3
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = "/tmp/aq_scale.db"
DAYS, STATIONS, SLOTS = 120, 112, 96
res = {}


def build():
    if os.path.exists(PATH):
        os.remove(PATH)
    rng = np.random.default_rng(1)
    n = DAYS * STATIONS * SLOTS
    st = np.repeat([f"S{i:03d}" for i in range(STATIONS)], DAYS * SLOTS)
    days = np.tile(np.repeat([(np.datetime64("2026-01-01") + np.timedelta64(int(d), "D")).astype(str) for d in range(DAYS)], SLOTS), STATIONS)
    slot = np.tile(np.arange(SLOTS), STATIONS * DAYS)
    pm = np.round(30 + 0.4 * (np.repeat(rng.uniform(10, 80, STATIONS), DAYS * SLOTS)) + 20 * np.exp(-((slot - 32) ** 2) / 60) + rng.normal(0, 8, n), 1)
    con = sqlite3.connect(PATH)
    con.execute("CREATE TABLE aq (station TEXT, day TEXT, slot INTEGER, pm25 REAL)")
    t = time.perf_counter()
    con.executemany("INSERT INTO aq VALUES (?, ?, ?, ?)", zip(st.tolist(), days.tolist(), slot.tolist(), pm.tolist()))
    con.commit()
    return con, n, time.perf_counter() - t


QUERIES = {
    "A  average of one station in one month": ("SELECT AVG(pm25) FROM aq WHERE station = 'S050' AND day BETWEEN '2026-02-01' AND '2026-02-28'", True),
    "B  daily mean of one station in one month": ("SELECT day, AVG(pm25) FROM aq WHERE station = 'S050' AND day BETWEEN '2026-02-01' AND '2026-02-28' GROUP BY day", True),
    "C  three stations with the highest mean": ("SELECT station, AVG(pm25) AS m FROM aq GROUP BY station ORDER BY m DESC LIMIT 3", False),
    "D  three worst time slots of the day": ("SELECT slot, AVG(pm25) AS m FROM aq GROUP BY slot ORDER BY m DESC LIMIT 3", False),
}


def timeit(con, sql, rep=5):
    best = 1e9
    for _ in range(rep):
        t = time.perf_counter(); con.execute(sql).fetchall(); best = min(best, time.perf_counter() - t)
    return best


def size_mb(con):
    return con.execute("PRAGMA page_count").fetchone()[0] * con.execute("PRAGMA page_size").fetchone()[0] / 1e6


if __name__ == "__main__":
    con, n, t_ins = build()
    print(f"=== table aq: {n:,} rows = 112 stations x 96 readings x {DAYS} days; inserted with ONE executemany call in {t_ins:.2f} s; database {size_mb(con):.1f} MB ===")
    print(f"projection to one year (365 days): {n * 365 // DAYS:,} rows, about {size_mb(con) * 365 / DAYS:.0f} MB, insertion about {t_ins * 365 / DAYS:.0f} s")
    before = {k: timeit(con, q) for k, (q, _) in QUERIES.items()}
    plan_before = [r[3] for r in con.execute("EXPLAIN QUERY PLAN " + QUERIES["A  average of one station in one month"][0])]
    slowest = max(before, key=before.get)
    print("\nWITHOUT an index (best of 5, ms):")
    for k, v in before.items():
        print(f"   {k:44} {v * 1000:9.1f}" + ("   <- slowest" if k == slowest else ""))
    print("query plan of A:", plan_before)
    t = time.perf_counter(); con.execute("CREATE INDEX idx_station_day ON aq (station, day)"); con.commit(); t_idx = time.perf_counter() - t
    s_after = size_mb(con)
    after = {k: timeit(con, q) for k, (q, _) in QUERIES.items()}
    plan_after = [r[3] for r in con.execute("EXPLAIN QUERY PLAN " + QUERIES["A  average of one station in one month"][0])]
    print(f"\nCREATE INDEX idx_station_day ON aq (station, day): {t_idx:.2f} s; database grows to {s_after:.1f} MB")
    print("WITH the index (ms) and speed-up:")
    for k in before:
        print(f"   {k:44} {after[k] * 1000:9.2f}   {before[k] / after[k]:8.1f}x")
    print("query plan of A:", plan_after)
    # covering index for the queries that group by station
    t = time.perf_counter(); con.execute("CREATE INDEX idx_cover ON aq (station, day, pm25)"); con.commit(); t_cov = time.perf_counter() - t
    cov = {k: timeit(con, q) for k, (q, _) in QUERIES.items()}
    print(f"\nadding a COVERING index (station, day, pm25): build {t_cov:.2f} s, database {size_mb(con):.1f} MB")
    for k in before:
        print(f"   {k:44} {cov[k] * 1000:9.2f} ms   ({before[k] / cov[k]:.1f}x faster than no index)")
    # insert cost with the index in place (new daily load: 112 stations x 96 = 10,752 rows)
    rows = [(f"S{i % 112:03d}", "2026-05-01", i % 96, 40.0) for i in range(10_752)]
    t = time.perf_counter(); con.executemany("INSERT INTO aq VALUES (?, ?, ?, ?)", rows); con.commit(); t_day = time.perf_counter() - t
    print(f"\ncost of one daily load (10,752 rows) with both indexes in place: {t_day:.3f} s")
    res = dict(n=n, t_insert=t_ins, size_before=size_mb(con), before=before, after=after, cover=cov, slowest=slowest, t_index=t_idx, t_cover=t_cov,
               size_after_idx=s_after, plan_before=plan_before, plan_after=plan_after, t_daily_load=t_day)
    json.dump(res, open(os.path.join(HERE, "results_scale.json"), "w"), indent=1)
    con.close()
    os.remove(PATH)
