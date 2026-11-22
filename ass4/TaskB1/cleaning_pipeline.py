"""B1 - Implement and validate the cleaning pipeline; store in SQLite; query; visualise."""
import csv
import json
import os
import sqlite3
import statistics
import sys
import time
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import aqlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

res = {}
HERE = os.path.dirname(os.path.abspath(__file__))

SAMPLE = """station,date,hour,pm25,pm10,no,temperature
Adyar,2026-10-01,00,48,90,20,30.1
Adyar,2026-10-01,01,NA,85,19,29.8
Adyar,2026-10-01,02,,80,18,29.5
Adyar,2026-10-01,03,-5,78,17,29.1
Adyar,2026-10-01,04,9999,76,17,28.7
Adyar,2026-10-01,04,9999,76,17,28.7
Adyar,2026-10-01,05,52,96,21,28.4
 adyar ,2026-10-01,6,55,99,22,28.1
Manali,2026-10-01,00,60,110,25,86.0
Manali,2026-10-01,01,ERR,115,26,84.2
Guindy,01/10/2026,00,95,170,40,29.9
Guindy,01/10/2026,01,98,175,41,29.7
"""


def read_csv_file(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


print("=== B1.1 Validate the implementation on a small file that contains every problem of A1.1 ===")
open(os.path.join(HERE, "sample_messy.csv"), "w", newline="").write(SAMPLE)
raw = read_csv_file(os.path.join(HERE, "sample_messy.csv"))
print("BEFORE cleaning (12 rows as received):")
for r in raw:
    print("  ", [r[h] for h in aqlib.HEADER])
stats = {}
clean = aqlib.clean_rows(raw, stats=stats)
print("\nAFTER cleaning (station, date, hour, pm25, pm10, no, temp_c) - note: forward fill used for gaps of up to 3 hours:")
for r in clean:
    print("  ", r)
print("\nProblem found -> rule applied (counts from the program):")
for label, key in (("missing / NA / blank values", "missing"), ("text instead of a number (ERR)", "not_numeric"), ("negative values -> missing", "negative"),
                   ("impossibly large values -> missing", "too_large"), ("duplicate rows removed", "duplicates"), ("Fahrenheit temperatures converted", "fahrenheit"),
                   ("dates rewritten to ISO format", "dates_reformatted"), ("station names normalised", "names_fixed"), ("values forward-filled", "filled"),
                   ("values still missing", "still_missing")):
    print(f"   {label:38} {stats[key]}")
checks = {
    "duplicate removed (12 rows in, 11 out)": len(raw) == 12 and len(clean) == 11,
    "Manali 86.0 F = 30.0 C": [r for r in clean if r[0] == "Manali"][0][6] == 30.0,
    "Adyar hour 1 pm25 NA filled with 48.0": [r for r in clean if r[0] == "Adyar" and r[2] == 1][0][3] == 48.0,
    "Adyar hour 6 name fixed, hour 06": any(r[0] == "Adyar" and r[2] == 6 for r in clean),
    "Guindy date 01/10/2026 -> 2026-10-01": all(r[1] == "2026-10-01" for r in clean if r[0] == "Guindy"),
    "no value outside the valid range": all(r[3] is None or 0 <= r[3] <= 999 for r in clean),
}
for k, v in checks.items():
    print(f"   check: {k:46} {'PASS' if v else 'FAIL'}")
res["sample"] = dict(stats=stats, checks=checks)

print("\n=== Full month: 12 stations, 1-31 October 2026 ===")
truth = aqlib.generate_clean_truth(aqlib.STATIONS, date(2026, 10, 1), 31, seed=1)
rawm = aqlib.make_raw(truth, seed=2)
path_raw = os.path.join(HERE, "october_raw.csv")
open(path_raw, "w", newline="").write(aqlib.raw_to_csv_text(rawm))
rawm = read_csv_file(path_raw)
fs = {}
t = time.perf_counter()
cleaned = aqlib.clean_rows(rawm, stats=fs)
t_clean = time.perf_counter() - t
print(f"rows received {fs['rows_in']:,} -> rows stored {fs['rows_out']:,} (12 stations x 31 days x 24 hours = {12 * 31 * 24:,}); cleaning time {t_clean:.3f} s")
print("cleaning counts:", {k: v for k, v in fs.items() if k not in ("rows_in", "rows_out")})
# accuracy of the cleaning against the truth (values that were never damaged must stay identical)
true_map = {(t_["station"], t_["day"].isoformat(), t_["hour"]): t_ for t_ in truth}
same = diff = 0
err = []
for r in cleaned:
    tv = true_map[(r[0], r[1], r[2])]
    if r[3] is not None:
        err.append(abs(r[3] - tv["pm25"]))
        same += abs(r[3] - tv["pm25"]) < 0.051
        diff += abs(r[3] - tv["pm25"]) >= 0.051
print(f"PM2.5 values equal to the true value: {same:,} of {same + diff:,}; the rest are forward-filled values (mean absolute error of ALL stored values {statistics.fmean(err):.2f} ug/m3)")
res["month"] = dict(stats=fs, t_clean=t_clean, mae=statistics.fmean(err), equal=same, filled_or_changed=diff)

print("\n=== B1.3 Store in SQLite with executemany and answer the three questions of A1.3 ===")
db_path = os.path.join(HERE, "airquality.db")
if os.path.exists(db_path):
    os.remove(db_path)
con = aqlib.create_db(db_path)
t = time.perf_counter()
aqlib.load_readings(con, cleaned)
t_load = time.perf_counter() - t
print(f"loaded {con.execute('SELECT COUNT(*) FROM readings').fetchone()[0]:,} readings in {t_load:.3f} s with ONE executemany call")
Q1 = ("SELECT ROUND(AVG(r.pm25), 2) FROM readings r JOIN stations s ON s.station_id = r.station_id "
      "WHERE s.name = ? AND r.day BETWEEN '2026-10-01' AND '2026-10-31'")
Q2 = ("SELECT s.name, ROUND(AVG(r.pm25), 2) AS m FROM readings r JOIN stations s ON s.station_id = r.station_id "
      "GROUP BY s.name ORDER BY m DESC LIMIT 3")
Q3 = "SELECT hour, ROUND(AVG(pm25), 2) AS m FROM readings GROUP BY hour ORDER BY m DESC LIMIT 3"
a1 = con.execute(Q1, ("Adyar",)).fetchone()[0]
a2 = con.execute(Q2).fetchall()
a3 = con.execute(Q3).fetchall()
print("Q1 average PM2.5 of Adyar in October            :", a1)
print("Q2 three stations with the highest mean PM2.5   :", a2)
print("Q3 three hours with the worst air (mean PM2.5)  :", a3)
res["sql"] = dict(q1=a1, q2=a2, q3=a3, t_load=t_load)

# the same three questions from the cleaned CSV file (read + loop)
clean_csv = os.path.join(HERE, "october_clean.csv")
with open(clean_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["station", "date", "hour", "pm25", "pm10", "no", "temp_c"])
    w.writerows(cleaned)


def csv_answers():
    sums, cnt, hs, hc = {}, {}, {}, {}
    adyar_sum = adyar_n = 0
    with open(clean_csv, newline="") as f:
        for row in csv.DictReader(f):
            if row["pm25"] == "":
                continue
            v = float(row["pm25"])
            sums[row["station"]] = sums.get(row["station"], 0) + v
            cnt[row["station"]] = cnt.get(row["station"], 0) + 1
            h = int(row["hour"])
            hs[h] = hs.get(h, 0) + v
            hc[h] = hc.get(h, 0) + 1
            if row["station"] == "Adyar":
                adyar_sum += v
                adyar_n += 1
    top = sorted(((round(sums[s] / cnt[s], 2), s) for s in sums), reverse=True)[:3]
    worst = sorted(((round(hs[h] / hc[h], 2), h) for h in hs), reverse=True)[:3]
    return round(adyar_sum / adyar_n, 2), top, worst


def best(fn, n=5):
    r = []
    for _ in range(n):
        t0 = time.perf_counter(); out = fn(); r.append(time.perf_counter() - t0)
    return min(r), out


t_csv, (c1, c2, c3) = best(csv_answers)
t_q1, _ = best(lambda: con.execute(Q1, ("Adyar",)).fetchone())
t_q2, _ = best(lambda: con.execute(Q2).fetchall())
t_q3, _ = best(lambda: con.execute(Q3).fetchall())
print(f"\nCSV (read the whole file once for all three answers): {t_csv * 1000:.1f} ms -> Q1 {c1}, top stations {[(s, m) for m, s in c2]}, worst hours {[(h, m) for m, h in c3]}")
print(f"SQL: Q1 {t_q1 * 1000:.2f} ms, Q2 {t_q2 * 1000:.2f} ms, Q3 {t_q3 * 1000:.2f} ms (data already in the database)")
print("CSV and SQL give the same answers:", c1 == a1 and [(s, m) for m, s in c2] == a2 and [(h, m) for m, h in c3] == a3)
res["csv_vs_sql"] = dict(t_csv=t_csv, t_q1=t_q1, t_q2=t_q2, t_q3=t_q3, same=(c1 == a1))

print("\n=== B1.4 Charts (saved as PNG) ===")
# 1 line: daily mean PM2.5 of one station
daily = con.execute("SELECT r.day, AVG(r.pm25) FROM readings r JOIN stations s USING (station_id) WHERE s.name = 'Adyar' GROUP BY r.day ORDER BY r.day").fetchall()
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.plot([int(d[8:]) for d, _ in daily], [m for _, m in daily], marker="o")
ax.axhline(60, color="red", ls="--", lw=1, label="24-h standard 60 ug/m3")
ax.set_xlabel("Day of October 2026"); ax.set_ylabel("Daily mean PM2.5 (ug/m3)"); ax.set_title("Chart 1: Trend of PM2.5 at Adyar, October 2026"); ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "chart1_trend.png"), dpi=140); plt.close(fig)
dv = [m for _, m in daily]
peak = max(daily, key=lambda x: x[1]); low = min(daily, key=lambda x: x[1])
print(f"chart 1: highest daily mean {peak[1]:.1f} on {peak[0]}, lowest {low[1]:.1f} on {low[0]}, days above 60: {sum(v > 60 for v in dv)} of {len(dv)}")

# 2 box plot: comparison of stations
data, names = [], []
for n, in con.execute("SELECT name FROM stations ORDER BY name"):
    names.append(n)
    data.append([v for v, in con.execute("SELECT r.pm25 FROM readings r JOIN stations s USING (station_id) WHERE s.name = ? AND r.pm25 IS NOT NULL", (n,))])
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.boxplot(data, tick_labels=names, showfliers=True)
ax.set_xlabel("Station"); ax.set_ylabel("Hourly PM2.5 (ug/m3)"); ax.set_title("Chart 2: Comparison of the 12 stations (hourly PM2.5, October 2026)")
plt.setp(ax.get_xticklabels(), rotation=40, ha="right"); ax.grid(alpha=.3, axis="y")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "chart2_stations.png"), dpi=140); plt.close(fig)
med = sorted(((statistics.median(d), n) for d, n in zip(data, names)), reverse=True)
print(f"chart 2: highest median {med[0][1]} ({med[0][0]:.1f}), lowest median {med[-1][1]} ({med[-1][0]:.1f})")

# 3 scatter: temperature against PM2.5
pts = con.execute("SELECT temp_c, pm25 FROM readings WHERE temp_c IS NOT NULL AND pm25 IS NOT NULL").fetchall()
xs, ys = [p[0] for p in pts], [p[1] for p in pts]
r = statistics.correlation(xs, ys)
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.scatter(xs, ys, s=4, alpha=.25)
ax.set_xlabel("Temperature (deg C)"); ax.set_ylabel("PM2.5 (ug/m3)"); ax.set_title(f"Chart 3: Temperature against PM2.5 (r = {r:.2f}, n = {len(pts):,})"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "chart3_scatter.png"), dpi=140); plt.close(fig)
print(f"chart 3: correlation coefficient r = {r:.3f} over {len(pts):,} hourly points")

# 4 bar: mean PM2.5 by hour of the day
hours = con.execute("SELECT hour, AVG(pm25) FROM readings GROUP BY hour ORDER BY hour").fetchall()
fig, ax = plt.subplots(figsize=(8, 3.8))
top3 = {h for h, _ in sorted(hours, key=lambda x: -x[1])[:3]}
ax.bar([h for h, _ in hours], [m for _, m in hours], color=["#c0392b" if h in top3 else "#5b8def" for h, _ in hours])
ax.set_xlabel("Hour of the day"); ax.set_ylabel("Mean PM2.5 (ug/m3)"); ax.set_title("Chart 4: Hours with the worst air (red = worst three)"); ax.set_xticks(range(0, 24, 2)); ax.grid(alpha=.3, axis="y")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "chart4_hours.png"), dpi=140); plt.close(fig)
print("chart 4: worst three hours", sorted(top3), "best hour", min(hours, key=lambda x: x[1])[0], f"({min(hours, key=lambda x: x[1])[1]:.1f})")
print("\n=== A3.2 daily summary table per station (min, max, mean, number of valid readings) produced with ONE GROUP BY query ===")
con.execute("DROP TABLE IF EXISTS daily_summary")
con.execute("CREATE TABLE daily_summary AS SELECT station_id, day, MIN(pm25) AS min_pm25, MAX(pm25) AS max_pm25, ROUND(AVG(pm25), 2) AS mean_pm25, COUNT(pm25) AS n_valid FROM readings GROUP BY station_id, day")
con.commit()
srows = con.execute("SELECT s.name, d.day, d.min_pm25, d.max_pm25, d.mean_pm25, d.n_valid FROM daily_summary d JOIN stations s USING (station_id) ORDER BY s.name, d.day LIMIT 4").fetchall()
print(f"{'station':10} {'day':11} {'min':>6} {'max':>6} {'mean':>7} {'n_valid':>8}")
for r_ in srows:
    print(f"{r_[0]:10} {r_[1]:11} {r_[2]:>6} {r_[3]:>6} {r_[4]:>7} {r_[5]:>8}")
cnt = con.execute("SELECT COUNT(*), MAX(n_valid), MIN(n_valid) FROM daily_summary").fetchone()
print(f"rows in the summary table: {cnt[0]} (12 stations x 31 days = 372); n_valid between {cnt[2]} and {cnt[1]} (24 hourly readings per day at most)")
res["summary_table"] = dict(rows=cnt[0], first=srows)

res["charts"] = dict(peak=peak, low=low, days_above_60=sum(v > 60 for v in dv), ndays=len(dv), med_hi=med[0], med_lo=med[-1], r=r, npts=len(pts),
                     worst_hours=sorted(top3), best_hour=min(hours, key=lambda x: x[1]))
json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
con.close()
