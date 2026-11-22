"""Q5 - List comprehension: cleaning cold-storage temperature readings."""
import json
import random
import sys
import time
import tracemalloc

res = {}
LOW, HIGH = -50, 50              # valid sensor range (deg C)
SAFE_LOW, SAFE_HIGH = 2, 8       # safe vaccine range (deg C)


def make_readings(n, bad_fraction=0.05, seed=11):
    """Mostly 2-8 C with some excursions and ~5 % sensor errors (+-99 or 999)."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        r = rnd.random()
        if r < bad_fraction:
            out.append(rnd.choice([99.0, -99.0, 999.0, -60.5, 55.2]))
        elif r < bad_fraction + 0.10:
            out.append(round(rnd.uniform(-5, 14), 1))         # temperature excursion
        else:
            out.append(round(rnd.uniform(2, 8), 1))
    return out


def c_to_f(c):
    return c * 9 / 5 + 32


# ------------------------------------------------------------ version 1: for loop with append
def clean_loop(readings):
    celsius, fahrenheit, alarms = [], [], []
    for minute, c in enumerate(readings, start=1):            # minute 1 = first reading
        if LOW <= c <= HIGH:                                  # sensor errors are skipped
            celsius.append(c)
            fahrenheit.append(c_to_f(c))
            if not (SAFE_LOW <= c <= SAFE_HIGH):
                alarms.append(minute)
    return celsius, fahrenheit, alarms


# ------------------------------------------------------------ version 2: list comprehensions
def clean_comp(readings):
    celsius = [c for c in readings if LOW <= c <= HIGH]
    fahrenheit = [c * 9 / 5 + 32 for c in celsius]                # reuse the cleaned list (no second range test)
    alarms = [m for m, c in enumerate(readings, start=1) if LOW <= c <= HIGH and not (SAFE_LOW <= c <= SAFE_HIGH)]
    return celsius, fahrenheit, alarms


# ------------------------------------------------------------ version 3: map() and filter() with lambda
def clean_mapfilter(readings):
    celsius = list(filter(lambda c: LOW <= c <= HIGH, readings))
    fahrenheit = list(map(lambda c: c * 9 / 5 + 32, celsius))
    alarms = list(map(lambda mc: mc[0],
                      filter(lambda mc: LOW <= mc[1] <= HIGH and not (SAFE_LOW <= mc[1] <= SAFE_HIGH),
                             enumerate(readings, start=1))))
    return celsius, fahrenheit, alarms


def best(fn, *a, repeat=3):
    r = []
    for _ in range(repeat):
        t = time.perf_counter(); fn(*a); r.append(time.perf_counter() - t)
    return min(r)


if __name__ == "__main__":
    print("=== Small example ===")
    demo = [4.0, 5.5, 99.0, 9.1, -60.5, 1.5, 7.9, 2.0]
    for name, fn in (("for loop + append", clean_loop), ("list comprehensions", clean_comp), ("map/filter + lambda", clean_mapfilter)):
        c, f, a = fn(demo)
        print(f"{name:20} valid C={c}\n{'':20} F={[round(x, 1) for x in f]}\n{'':20} alarm minutes={a}")
    print("Hand check: readings 99.0 and -60.5 are errors; valid = [4.0, 5.5, 9.1, 1.5, 7.9, 2.0]; outside 2-8 C: 9.1 (minute 4), 1.5 (minute 6) -> alarms [4, 6]")
    print("Boundaries 2.0 and 8.0 are inside the safe range; 50 and -50 are valid readings:",
          clean_comp([2.0, 8.0, 50, -50, 50.1, -50.1])[2])

    print("\n=== General form of a list comprehension with a condition ===")
    print("[expression  for item in iterable  if condition]   ->  the same as:\n"
          "  result = []\n  for item in iterable:\n      if condition:\n          result.append(expression)")

    print("\n=== Dictionary and set comprehensions for this problem ===")
    valid_by_minute = {m: c for m, c in enumerate(demo, start=1) if LOW <= c <= HIGH}
    distinct_whole_degrees = {round(c) for c in demo if LOW <= c <= HIGH}
    print("dictionary comprehension {minute: celsius for valid readings} :", valid_by_minute)
    print("set comprehension {rounded temperature for valid readings}    :", sorted(distinct_whole_degrees))

    print("\n=== Verify that the three versions give identical results ===")
    cases = {"mixed (10,000)": make_readings(10_000), "all valid": [4.5] * 1000 + [0.0, 10.0, -50, 50],
             "all invalid": [100.0, -75.5, 999.0] * 100, "empty": []}
    ok = True
    for name, data in cases.items():
        a, b, c = clean_loop(data), clean_comp(data), clean_mapfilter(data)
        same = a == b == c
        ok &= same
        print(f"{name:16}: valid={len(a[0]):>5} alarms={len(a[2]):>5} identical={same}")
    print("all three versions identical on every test:", ok)
    res["identical"] = ok

    print("\n=== Time of the three versions (seconds, best of 3) ===")
    print(f"{'readings':>10} | {'for + append':>12} {'comprehension':>14} {'map/filter':>11} | loop/comp  mapfilter/comp")
    rows = []
    for n in (10_000, 100_000, 1_000_000):
        data = make_readings(n)
        t1, t2, t3 = best(clean_loop, data), best(clean_comp, data), best(clean_mapfilter, data)
        rows.append(dict(n=n, loop=t1, comp=t2, mapfilter=t3))
        print(f"{n:>10,} | {t1:>12.4f} {t2:>14.4f} {t3:>11.4f} | {t1 / t2:>9.2f} {t3 / t2:>13.2f}")
    res["times"] = rows

    print("\n=== Memory: list comprehension against generator expression (1,000,000 readings) ===")
    data = make_readings(1_000_000)
    lst = [c for c in data if LOW <= c <= HIGH]
    gen = (c for c in data if LOW <= c <= HIGH)
    print(f"sys.getsizeof(list comprehension result)   = {sys.getsizeof(lst):>10,} bytes (holds {len(lst):,} references)")
    print(f"sys.getsizeof(generator expression object) = {sys.getsizeof(gen):>10,} bytes (holds nothing yet, computes on demand)")
    tracemalloc.start(); s1 = sum([c for c in data if LOW <= c <= HIGH]); p1 = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
    tracemalloc.start(); s2 = sum(c for c in data if LOW <= c <= HIGH); p2 = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
    t_l = best(lambda: sum([c for c in data if LOW <= c <= HIGH]))
    t_g = best(lambda: sum(c for c in data if LOW <= c <= HIGH))
    print(f"sum([ ... ]) : peak extra memory {p1 / 1e6:8.3f} MB, time {t_l:.4f} s, result {s1:.1f}")
    print(f"sum( ... )   : peak extra memory {p2 / 1e6:8.3f} MB, time {t_g:.4f} s, result {s2:.1f}")
    g2 = (c for c in data[:5])
    first_pass = sum(g2)
    print("same sum:", abs(s1 - s2) < 1e-6, f"| a generator can be used once: first sum {first_pass:.1f}, second sum over the same generator = {sum(g2)}")
    res["mem"] = dict(list_bytes=sys.getsizeof(lst), gen_bytes=sys.getsizeof(gen), peak_list=p1, peak_gen=p2, t_list=t_l, t_gen=t_g)
    json.dump(res, open("results.json", "w"), indent=1)
