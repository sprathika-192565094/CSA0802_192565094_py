"""Part A support experiments (no design is accepted without evidence):
   1. A2 alternative: drop / forward fill / median fill - effect on daily means, time and space
   2. A2.2: min-max and z-score on PM2.5 with and without a spike
   3. A4 alternative: cost of print / logging / disabled logging / assert (thousands of calls) and how each is switched off"""
import io
import json
import logging
import os
import statistics
import subprocess
import sys
import time
import tracemalloc
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import random
import aqlib

HERE = os.path.dirname(os.path.abspath(__file__))
res = {}

# ---------------------------------------------------------------- 1. missing values
print("=== 1. Missing PM2.5 values: drop, forward fill (limit 3 h) or median fill - effect on the daily mean ===")
truth = aqlib.generate_clean_truth(aqlib.STATIONS, date(2026, 10, 1), 31, seed=1)
series = {}
for t in truth:
    series.setdefault(t["station"], []).append((t["day"], t["hour"], t["pm25"]))


def daily_means(values_by_station):
    out = {}
    for st, rows in values_by_station.items():
        by = {}
        for d, h, v in rows:
            if v is not None:
                by.setdefault(d, []).append(v)
        for d, v in by.items():
            out[(st, d)] = sum(v) / len(v)
    return out


true_mean = daily_means(series)


def damage(rate_random, peak_rate, seed):
    r = random.Random(seed)
    out = {}
    for st, rows in series.items():
        out[st] = [(d, h, None if r.random() < (peak_rate if h in (7, 8, 9, 18, 19, 20) else rate_random) else v) for d, h, v in rows]
    return out


def drop(rows):
    return rows                                    # missing values are simply not averaged


def ffill(rows, limit=3):
    out, last, gap = [], None, 0
    for d, h, v in rows:
        if v is None:
            gap += 1
            out.append((d, h, last if (last is not None and gap <= limit) else None))
        else:
            last, gap = v, 0
            out.append((d, h, v))
    return out


def median_fill(rows):
    m = statistics.median([v for _, _, v in rows if v is not None])
    return [(d, h, m if v is None else v) for d, h, v in rows]


print(f"{'scenario':42} {'method':12} {'mean abs error':>15} {'bias':>8} {'(ug/m3 per station-day)':>24}")
rows1 = []
for name, rr, pr in (("10 % missing completely at random", 0.10, 0.10), ("peak hours (7-9, 18-20) 40 % missing, others 5 %", 0.05, 0.40)):
    dmg = damage(rr, pr, seed=4)
    for meth, fn in (("drop", drop), ("forward fill", lambda r: ffill(r)), ("median fill", median_fill)):
        est = daily_means({st: fn(rows) for st, rows in dmg.items()})
        keys = [k for k in true_mean if k in est]
        errs = [est[k] - true_mean[k] for k in keys]
        mae, bias = statistics.fmean(abs(e) for e in errs), statistics.fmean(errs)
        rows1.append(dict(scenario=name, method=meth, mae=mae, bias=bias, days=len(keys)))
        print(f"{name:42} {meth:12} {mae:>15.2f} {bias:>+8.2f}")
res["missing"] = rows1

print("\nTime and extra space of the three methods on one long series (best of 3; tracemalloc peak of the result):")
print(f"{'values':>10} | {'drop (O(n))':>12} {'ffill (O(n))':>13} {'median (O(n log n))':>20} | peak MB: {'drop':>6} {'ffill':>6} {'median':>7}")
rows1b = []
for n in (10_000, 100_000, 1_000_000):
    r = random.Random(1)
    data = [(0, 0, None if r.random() < 0.1 else round(r.uniform(5, 150), 1)) for _ in range(n)]
    out = {}
    for name, fn in (("drop", lambda d: [v for _, _, v in d if v is not None]), ("ffill", ffill), ("median", median_fill)):
        best = 1e9
        for _ in range(3):
            t = time.perf_counter(); fn(data); best = min(best, time.perf_counter() - t)
        tracemalloc.start(); fn(data); peak = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
        out[name] = (best, peak)
    rows1b.append(dict(n=n, **{k: dict(t=v[0], mb=v[1] / 1e6) for k, v in out.items()}))
    print(f"{n:>10,} | {out['drop'][0]:>11.4f}s {out['ffill'][0]:>12.4f}s {out['median'][0]:>19.4f}s | {'':>9}{out['drop'][1] / 1e6:>6.1f} {out['ffill'][1] / 1e6:>6.1f} {out['median'][1] / 1e6:>7.1f}")
res["missing_cost"] = rows1b

# ---------------------------------------------------------------- 2. normalisation
print("\n=== 2. Normalisation of PM2.5 (8 readings of one station) ===")
vals = [42.0, 55.0, 61.0, 48.0, 70.0, 66.0, 52.0, 58.0]
spike = vals + [450.0]
for label, v in (("without spike", vals), ("with one valid-but-extreme reading 450", spike)):
    print(f"{label}:\n   values   {v}\n   min-max  {aqlib.min_max(v)}\n   z-score  {aqlib.z_scores(v)}")
print("constant series (division by zero guard): min-max", aqlib.min_max([50.0, 50.0, 50.0]), "z-score", aqlib.z_scores([50.0, 50.0, 50.0]))
res["norm"] = dict(minmax=aqlib.min_max(vals), z=aqlib.z_scores(vals), minmax_spike=aqlib.min_max(spike), z_spike=aqlib.z_scores(spike))

# ---------------------------------------------------------------- 3. print / logging / assert
print("\n=== 3. Cost of thousands of print, logging and assert calls (microseconds per call; output sent to a null device) ===")
devnull = open(os.devnull, "w")
log_off = logging.getLogger("aq_off"); log_off.setLevel(logging.WARNING); log_off.addHandler(logging.StreamHandler(devnull)); log_off.propagate = False
log_on = logging.getLogger("aq_on"); log_on.setLevel(logging.DEBUG); log_on.addHandler(logging.StreamHandler(devnull)); log_on.propagate = False
DEBUG = False


def bench(fn, n):
    best = 1e9
    for _ in range(3):
        t = time.perf_counter(); fn(n); best = min(best, time.perf_counter() - t)
    return best / n * 1e6


def f_print(n):
    for i in range(n):
        print("row", i, "pm25 =", 48.5, file=devnull)


def f_log_on(n):
    for i in range(n):
        log_on.debug("row %d pm25 = %s", i, 48.5)


def f_log_off(n):
    for i in range(n):
        log_off.debug("row %d pm25 = %s", i, 48.5)


def f_guard(n):
    for i in range(n):
        if DEBUG:
            print("row", i, "pm25 =", 48.5)


def f_assert(n):
    for i in range(n):
        assert 0 <= 48.5 <= 999, "pm25 out of range"


def f_none(n):
    for i in range(n):
        pass


print(f"{'calls':>8} | {'empty loop':>10} {'print':>8} {'logging ON':>11} {'logging OFF':>12} {'if DEBUG: print':>16} {'assert':>8}")
rows3 = []
for n in (1_000, 10_000, 100_000):
    r = dict(n=n, none=bench(f_none, n), print=bench(f_print, n), log_on=bench(f_log_on, n), log_off=bench(f_log_off, n), guard=bench(f_guard, n), assert_=bench(f_assert, n))
    rows3.append(r)
    print(f"{n:>8,} | {r['none']:>10.3f} {r['print']:>8.3f} {r['log_on']:>11.3f} {r['log_off']:>12.3f} {r['guard']:>16.3f} {r['assert_']:>8.3f}")
code = "import time\nt=time.perf_counter()\nfor i in range(1_000_000):\n    assert 0 <= 48.5 <= 999\nprint(round((time.perf_counter()-t)*1000,1))"
t_norm = float(subprocess.run([sys.executable, "-c", code], capture_output=True, text=True).stdout)
t_O = float(subprocess.run([sys.executable, "-O", "-c", code], capture_output=True, text=True).stdout)
print(f"\n1,000,000 assert statements: normal run {t_norm:.0f} ms, run with python -O {t_O:.0f} ms (assert statements are removed completely)")
res["debug_cost"] = dict(rows=rows3, assert_normal_ms=t_norm, assert_O_ms=t_O)
json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
