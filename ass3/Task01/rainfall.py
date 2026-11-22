"""Q1 - Lists and slicing: daily rainfall records of a village rain-gauge station."""
import json
import random
import time
import timeit
import tracemalloc
from collections import deque
from datetime import date, timedelta
from bisect import insort

W = 7                                   # window / week length


def make_readings(n, seed=1):
    """n daily readings in whole mm; about 40 % of the days are dry (0 mm)."""
    rnd = random.Random(seed)
    return [0 if rnd.random() < 0.4 else rnd.randint(1, 60) for _ in range(n)]


# ------------------------------------------------------------ weekly totals by slicing
def weekly_totals(readings):
    """Totals of consecutive 7-day blocks; the last block may be shorter."""
    return [sum(readings[i:i + W]) for i in range(0, len(readings), W)]


def extreme_weeks(readings):
    """(wettest, driest) among COMPLETE weeks, each as (week number starting at 1, total, first day number)."""
    full = [sum(readings[i:i + W]) for i in range(0, len(readings) - W + 1, W)]
    if not full:
        return None, None
    hi, lo = max(full), min(full)
    hi_i, lo_i = full.index(hi), full.index(lo)
    return (hi_i + 1, hi, hi_i * W + 1), (lo_i + 1, lo, lo_i * W + 1)


def max_min_positions(readings):
    if not readings:
        return None
    hi, lo = max(readings), min(readings)
    return dict(max=hi, max_first_day=readings.index(hi) + 1,
                max_days=[i + 1 for i, v in enumerate(readings) if v == hi],
                min=lo, min_first_day=readings.index(lo) + 1)


def dry_days(readings):
    return [i + 1 for i, v in enumerate(readings) if v == 0]          # day numbers 1..n


# ------------------------------------------------------------ moving averages
def ma_naive(readings, w=W):
    """Re-add all w values for every window: w-1 additions per window."""
    adds = 0
    out = []
    for i in range(len(readings) - w + 1):
        total = readings[i]
        for v in readings[i + 1:i + w]:
            total += v
            adds += 1
        out.append(total / w)
    return out, adds


def ma_running(readings, w=W):
    """Running sum: first window w-1 additions, then one addition and one subtraction per slide."""
    n = len(readings)
    if n < w:
        return [], 0
    ops = 0
    total = readings[0]
    for v in readings[1:w]:
        total += v
        ops += 1
    out = [total / w]
    for i in range(w, n):
        total += readings[i] - readings[i - w]
        ops += 2
        out.append(total / w)
    return out, ops


def ma_deque(readings, w=W):
    """collections.deque(maxlen=w) keeps only the current window; running sum is updated with the value that falls out."""
    win = deque(maxlen=w)
    total, out = 0, []
    for v in readings:
        if len(win) == w:
            total -= win[0]
        win.append(v)
        total += v
        if len(win) == w:
            out.append(total / w)
    return out


def ma_dict(by_date, start, n, w=W):
    """Readings stored in a dictionary keyed by date: w look-ups per window."""
    out = []
    for i in range(w - 1, n):
        total = 0
        for k in range(w):
            total += by_date[start + timedelta(days=i - k)]
        out.append(total / w)
    return out


def best(fn, *a, repeat=3):
    r = []
    for _ in range(repeat):
        t = time.perf_counter(); fn(*a); r.append(time.perf_counter() - t)
    return min(r)


if __name__ == "__main__":
    res = {}
    readings = make_readings(365)
    print("=== Basic results for 365 readings ===")
    wk = weekly_totals(readings)
    print(f"weeks: {len(wk)} (52 complete + 1 block of {365 - 52 * 7} day)  first 8 weekly totals: {wk[:8]}  last block: {wk[-1]}")
    wet, dry = extreme_weeks(readings)
    print(f"wettest complete week: week {wet[0]} (days {wet[2]}-{wet[2] + 6}) total {wet[1]} mm")
    print(f"driest complete week : week {dry[0]} (days {dry[2]}-{dry[2] + 6}) total {dry[1]} mm")
    mm = max_min_positions(readings)
    print(f"maximum {mm['max']} mm first on day {mm['max_first_day']} (all days: {mm['max_days']}); minimum {mm['min']} mm first on day {mm['min_first_day']}")
    ds = dry_days(readings)
    print(f"dry days: {len(ds)} of 365, first ten: {ds[:10]}")
    avg, adds_n = ma_naive(readings)
    avg2, ops_r = ma_running(readings)
    print(f"moving average windows: {len(avg)}; first three: {[round(x, 2) for x in avg[:3]]}")
    print("naive == running sum == deque:", all(abs(a - b) < 1e-9 for a, b in zip(avg, avg2)) and avg2 == ma_deque(readings) or
          all(abs(a - b) < 1e-9 for a, b in zip(avg, ma_deque(readings))))
    res.update(weeks=len(wk), wettest=wet, driest=dry, dry_days=len(ds), maxmin=mm)

    print("\n=== What do the slices return? ===")
    s1, s2, s3 = readings[7:14], readings[-7:], readings[::7]
    print("readings[7:14] -> days 8..14, length", len(s1), s1)
    print("readings[-7:]  -> the last 7 days (days 359..365), length", len(s2), s2)
    print("readings[::7]  -> every 7th reading starting at day 1 (days 1, 8, 15, ...), length", len(s3), s3[:6], "...")
    print("slices are NEW lists (copies of references):", s1 is not readings[7:14], "| readings unchanged:", len(readings))

    print("\n=== Derived number of additions (window w = 7, n readings) ===")
    print("naive  : (n - w + 1) windows x (w - 1) additions = 6(n - 6)   [7(n-6) if the sum starts from 0 -> O(7n)]")
    print("running: (w - 1) + 2(n - w) = 2n - 8 operations (one add + one subtract per slide) -> O(n)")
    print(f"{'n':>8} {'naive formula':>14} {'naive counted':>14} {'running formula':>16} {'running counted':>16}")
    counts = []
    for n in (365, 36_500, 365_000):
        r = make_readings(n)
        _, a1 = ma_naive(r)
        _, a2 = ma_running(r)
        f1, f2 = 6 * (n - 6), 2 * n - 8
        assert a1 == f1 and a2 == f2
        counts.append(dict(n=n, naive=a1, running=a2))
        print(f"{n:>8,} {f1:>14,} {a1:>14,} {f2:>16,} {a2:>16,}")
    res["counts"] = counts

    print("\n=== Timing (seconds, best of 3) ===")
    print(f"{'n':>8} {'naive':>10} {'running':>10} {'deque':>10} {'dict(date)':>11}  naive/running  ratio of derived counts")
    times = []
    for n in (365, 36_500, 365_000):
        r = make_readings(n)
        start = date(2026, 1, 1)
        by_date = {start + timedelta(days=i): v for i, v in enumerate(r)}
        t_n, t_r = best(ma_naive, r), best(ma_running, r)
        t_d, t_k = best(ma_deque, r), best(ma_dict, by_date, start, n)
        times.append(dict(n=n, naive=t_n, running=t_r, deque=t_d, dict=t_k))
        print(f"{n:>8,} {t_n:>10.5f} {t_r:>10.5f} {t_d:>10.5f} {t_k:>11.5f}  {t_n / t_r:>12.2f}  {6 * (n - 6) / (2 * n - 8):>8.2f}")
    res["times"] = times

    print("\n=== Memory (tracemalloc peak while building a result for n = 365,000) ===")
    r = make_readings(365_000)
    start = date(2026, 1, 1)
    mem = {}
    for name, fn in (("list slicing (naive)", lambda: ma_naive(r)), ("running sum", lambda: ma_running(r)),
                     ("deque(maxlen=7)", lambda: ma_deque(r))):
        tracemalloc.start(); fn(); mem[name] = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
    tracemalloc.start(); d = {start + timedelta(days=i): v for i, v in enumerate(r)}; mem["dictionary keyed by date (storage)"] = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
    for k, v in mem.items():
        print(f"  {k:36} {v / 1e6:8.2f} MB")
    res["mem"] = mem

    print("\n=== Edge cases ===")
    for label, data in (("empty list", []), ("3 readings", [5, 0, 2]), ("exactly 7", [1] * 7)):
        print(f"{label:11}: weekly={weekly_totals(data)} extreme={extreme_weeks(data)} maxmin={max_min_positions(data)} "
              f"dry={dry_days(data)} naive={ma_naive(data)[0]} running={ma_running(data)[0]} deque={ma_deque(data)}")

    print("\n=== Costs of list operations (n = 365,000 list, microseconds per operation, 200 repeats) ===")
    big = make_readings(365_000)
    def tm(stmt, setup_list):
        lst = list(setup_list)
        return timeit.timeit(lambda: stmt(lst), number=200) / 200 * 1e6
    ops = {
        "append(x)            O(1) amortised": tm(lambda l: (l.append(1), l.pop()), big),
        "pop()  (last)        O(1)": tm(lambda l: (l.append(1), l.pop()), big),
        "insert(0, x)         O(n)": tm(lambda l: (l.insert(0, 1), l.pop(0)), big),
        "insert(len//2, x)    O(n)": tm(lambda l: (l.insert(len(l) // 2, 1), l.pop(len(l) // 2)), big),
        "pop(0)               O(n)": tm(lambda l: (l.append(1), l.pop(0)), big),
        "sort() random data   O(n log n)": timeit.timeit(lambda: sorted(big), number=5) / 5 * 1e6,
        "sort() sorted data   O(n)": timeit.timeit(lambda: sorted(sorted(big)), number=5) / 5 * 1e6 - timeit.timeit(lambda: sorted(big), number=5) / 5 * 1e6,
    }
    for k, v in ops.items():
        print(f"  {k:36} {v:12.2f} us")
    res["ops_us"] = ops

    print("\n=== Design question: a reading arrives late and must be inserted at its date ===")
    r365 = make_readings(365)
    t_ins = timeit.timeit(lambda: (r365.insert(100, 12), r365.pop(100)), number=100000) / 100000 * 1e6
    print(f"insert in the middle of a 365-element list: {t_ins:.3f} microseconds -> about {365 // 2} references are shifted: negligible")
    print("with 365,000 elements a mid-list insert shifts ~182,000 references (see table above)")
    lst = [(1, 5), (2, 0), (4, 3)]
    insort(lst, (3, 9))
    print("bisect.insort keeps a (day, mm) list sorted:", lst)
    res["insert_365_us"] = t_ins
    json.dump(res, open("results.json", "w"), indent=1, default=str)
