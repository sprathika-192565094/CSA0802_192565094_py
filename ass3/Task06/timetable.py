"""Q6 - Nested data: railway timetable (dictionary -> {name, list of (station, arrival, departure) tuples, set of days})."""
import json
import random
import time
import tracemalloc

res = {}
ALL_DAYS = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

timetable = {
    "12621": {"name": "Tamil Nadu Express",
              "stops": [("Chennai Central", None, "22:00"), ("Vijayawada", "01:50", "02:00"), ("Nagpur", "10:20", "10:30"), ("New Delhi", "06:40", None)],
              "days": ALL_DAYS - set()},
    "12163": {"name": "Chennai Express",
              "stops": [("Dadar", None, "21:05"), ("Pune", "00:05", "00:15"), ("Chennai Central", "21:40", None)],
              "days": {"Mon", "Wed", "Fri"}},
    "12433": {"name": "Rajdhani Express",
              "stops": [("Chennai Central", None, "06:10"), ("Vijayawada", "10:40", "10:50"), ("Nagpur", "18:25", "18:35"), ("New Delhi", "08:15", None)],
              "days": {"Tue", "Thu", "Sat"}},
    "12007": {"name": "Shatabdi Express",
              "stops": [("Chennai Central", None, "06:00"), ("Katpadi", "07:35", "07:37"), ("Bengaluru", "11:00", None)],
              "days": {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat"}},
    "22637": {"name": "West Coast Express",
              "stops": [("Chennai Central", None, "13:55"), ("Katpadi", "15:25", "15:27"), ("Bengaluru", "19:10", "19:20"), ("Mangaluru", "08:15", None)],
              "days": {"Sun", "Fri"}},
}


# ------------------------------------------------------------ queries
def dep_time(train, station):
    """Departure time of `train` from `station` (arrival time at the terminus), or None if it does not stop there."""
    for st, arr, dep in train["stops"]:                     # a loop over the list of tuples with unpacking
        if st == station:
            return dep if dep is not None else arr
    return None


def trains_at(tt, station, day):
    """All train numbers that stop at `station` and run on `day` (full scan of the timetable)."""
    return [no for no, t in tt.items() if day in t["days"] and dep_time(t, station) is not None]


def sorted_by_departure(tt, station, day):
    return sorted(trains_at(tt, station, day), key=lambda no: dep_time(tt[no], station))


def print_timetable(tt):
    for no in sorted(tt):
        t = tt[no]
        print(f"{no}  {t['name']:20} runs: {' '.join(d for d in DAY_ORDER if d in t['days'])}")
        for st, arr, dep in t["stops"]:
            print(f"      {st:18} arr {arr or '--':>5}   dep {dep or '--':>5}")


# ------------------------------------------------------------ index: station -> list of (departure, train number), sorted
def build_index(tt):
    index = {}
    for no, t in tt.items():
        for st, arr, dep in t["stops"]:
            index.setdefault(st, []).append((dep if dep is not None else arr, no))
    for lst in index.values():
        lst.sort()
    return index


def query_indexed(tt, index, station, day):
    return [no for dep, no in index.get(station, []) if day in tt[no]["days"]]       # already sorted by departure


# ------------------------------------------------------------ alternative design: flat list of tuples
def flatten(tt):
    return [(no, st, arr, dep, t["days"]) for no, t in tt.items() for st, arr, dep in t["stops"]]


def query_flat(flat, station, day):
    rows = [(dep if dep is not None else arr, no) for no, st, arr, dep, days in flat if st == station and day in days]
    return [no for dep, no in sorted(rows)]


# ------------------------------------------------------------ generator
def make_timetable(n_trains, n_stations=300, seed=2):
    rnd = random.Random(seed)
    stations = [f"Station{i:03d}" for i in range(n_stations)]
    tt = {}
    for k in range(n_trains):
        stops = []
        t = rnd.randrange(0, 600)
        for st in rnd.sample(stations, rnd.randint(6, 14)):
            arr = None if not stops else f"{t // 60:02d}:{t % 60:02d}"
            t += rnd.randint(1, 4)
            dep = f"{t // 60:02d}:{t % 60:02d}"
            stops.append((st, arr, dep))
            t += rnd.randint(15, 60)
        stops[-1] = (stops[-1][0], stops[-1][1], None)
        tt[f"{10000 + k}"] = {"name": f"Train {k}", "stops": stops, "days": set(rnd.sample(DAY_ORDER, rnd.randint(2, 7)))}
    return tt, stations


if __name__ == "__main__":
    print("=== The timetable (5 trains) ===")
    print_timetable(timetable)

    print("\n=== Reaching the departure time of the third station of a train ===")
    print('timetable["12621"]["stops"][2][2] ->', timetable["12621"]["stops"][2][2], "(train 12621, third stop Nagpur, element 2 of the tuple = departure)")
    print('timetable["12621"]["name"]        ->', timetable["12621"]["name"])
    print('"Fri" in timetable["12163"]["days"] ->', "Fri" in timetable["12163"]["days"])

    print("\n=== Queries ===")
    for station, day in (("Chennai Central", "Tue"), ("Chennai Central", "Fri"), ("Katpadi", "Sun"), ("Vijayawada", "Mon"), ("Atlantis", "Mon"), ("Pune", "Tue")):
        res_ = sorted_by_departure(timetable, station, day)
        shown = [f"{no} ({dep_time(timetable[no], station)})" for no in res_]
        print(f"{station:16} on {day}: {shown or 'no trains'}")
    print("Train 12163 (Mon/Wed/Fri) stops at Pune but does not run on Tue -> not listed for Pune/Tue: ",
          "12163" not in trains_at(timetable, "Pune", "Tue"))
    idx = build_index(timetable)
    ok = all(query_indexed(timetable, idx, s, d) == sorted_by_departure(timetable, s, d)
             for s in list(idx) + ["Atlantis"] for d in DAY_ORDER)
    print("indexed query equals the full-scan query for every station and day:", ok)
    flat = flatten(timetable)
    print("flat-list query equals the full-scan query:",
          all(query_flat(flat, s, d) == sorted_by_departure(timetable, s, d) for s in list(idx) + ["Atlantis"] for d in DAY_ORDER))

    print("\n=== Experiment: 100, 1,000 and 10,000 trains (200 random station/day queries each) ===")
    print(f"{'trains':>7} {'stops':>8} | {'full scan':>12} {'flat list':>12} {'with index':>12} | {'index build':>11} {'index memory':>13} {'timetable memory':>17}")
    rows = []
    for n in (100, 1_000, 10_000):
        tt, stations = make_timetable(n)
        flat = flatten(tt)
        total_stops = len(flat)
        rnd = random.Random(9)
        queries = [(rnd.choice(stations + ["Atlantis"]), rnd.choice(DAY_ORDER)) for _ in range(200)]
        t = time.perf_counter(); idx = build_index(tt); t_build = time.perf_counter() - t
        # correctness on the queries
        assert all(query_indexed(tt, idx, s, d) == sorted_by_departure(tt, s, d) == query_flat(flat, s, d) for s, d in queries[:20])
        reps = 20 if n < 10_000 else 3
        def timeit_q(fn, qs):
            best = 1e9
            for _ in range(3):
                t0 = time.perf_counter()
                for s, d in qs:
                    fn(s, d)
                best = min(best, time.perf_counter() - t0)
            return best / len(qs)
        qs_scan = queries[:reps if n == 10_000 else 40]
        t_scan = timeit_q(lambda s, d: sorted_by_departure(tt, s, d), qs_scan)
        t_flat = timeit_q(lambda s, d: query_flat(flat, s, d), qs_scan)
        t_idx = timeit_q(lambda s, d: query_indexed(tt, idx, s, d), queries)
        tracemalloc.start(); build_index(tt); mem_idx = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
        tracemalloc.start(); make_timetable(n); mem_tt = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
        rows.append(dict(trains=n, stops=total_stops, scan=t_scan, flat=t_flat, index=t_idx, build=t_build, mem_index=mem_idx, mem_tt=mem_tt))
        print(f"{n:>7,} {total_stops:>8,} | {t_scan * 1e6:>9.1f} us {t_flat * 1e6:>9.1f} us {t_idx * 1e6:>9.2f} us | {t_build * 1e3:>8.2f} ms {mem_idx / 1e3:>10.1f} KB {mem_tt / 1e3:>14.1f} KB")
    res["rows"] = rows
    print("speed-up of the index over the full scan:", [f"{r['scan'] / r['index']:.0f}x" for r in rows])
    json.dump(res, open("results.json", "w"), indent=1)
