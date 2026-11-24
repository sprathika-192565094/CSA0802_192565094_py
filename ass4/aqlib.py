"""Shared library for Assignment 4 - city air-quality monitoring network.
Generation of messy station data, cleaning rules, normalisation and SQLite helpers."""
import csv
import io
import math
import random
import sqlite3
import statistics
from datetime import date, datetime, timedelta

STATIONS = [("Adyar", "South"), ("Guindy", "South"), ("Velachery", "South"), ("T. Nagar", "Central"),
            ("Anna Nagar", "West"), ("Perambur", "North"), ("Manali", "North"), ("Royapuram", "North"),
            ("Alandur", "South"), ("Kodungaiyur", "North"), ("Besant Nagar", "South"), ("Mylapore", "Central")]
FAHRENHEIT = {"Manali", "Perambur"}                       # two stations report temperature in Fahrenheit
DAY_FIRST_STATIONS = {"Guindy"}                           # one station writes dates as dd/mm/yyyy
HEADER = ["station", "date", "hour", "pm25", "pm10", "no", "temperature"]
LIMITS = {"pm25": (0, 999), "pm10": (0, 1999), "no": (0, 999), "temperature": (-10, 60)}   # valid ranges (temperature in deg C)
FILL_LIMIT = 3                                            # forward fill at most 3 consecutive hours
MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-"}


# =============================================================== generation of messy raw data
def generate_clean_truth(stations, start, days, seed=1):
    """True values (no problems): list of dicts. PM2.5 follows traffic peaks (8h and 19h) and is higher when it is cooler."""
    rnd = random.Random(seed)
    base = {name: 35 + 12 * (i % 5) + rnd.uniform(-5, 5) for i, (name, _) in enumerate(stations)}
    rows = []
    for d in range(days):
        day = start + timedelta(days=d)
        weather = rnd.lognormvariate(0, 0.25)                     # a bad-air day multiplies the whole day
        for name, _ in stations:
            for h in range(24):
                temp = 29 + 5 * math.sin((h - 9) / 24 * 2 * math.pi) + rnd.gauss(0, 0.8)
                peak = 20 * math.exp(-((h - 8) ** 2) / 8) + 24 * math.exp(-((h - 19) ** 2) / 8)
                pm25 = max(2.0, (base[name] + peak) * weather - 1.8 * (temp - 29) + rnd.gauss(0, 4))
                pm10 = pm25 * 1.8 + rnd.gauss(0, 6)
                no = max(1.0, 10 + 0.35 * pm25 + rnd.gauss(0, 3))
                rows.append(dict(station=name, day=day, hour=h, pm25=round(pm25, 1), pm10=round(pm10, 1), no=round(no, 1), temperature=round(temp, 1)))
    return rows


def make_raw(truth, seed=2, messy=True):
    """Turn true values into the strings that stations really send (with every problem of A1.1)."""
    rnd = random.Random(seed)
    out = []
    for t in truth:
        name = t["station"]
        if messy and rnd.random() < 0.05:
            name = rnd.choice([name.upper(), name.lower(), " " + name + " "])          # inconsistent station names
        d = t["day"].strftime("%d/%m/%Y") if (t["station"] in DAY_FIRST_STATIONS) else t["day"].isoformat()
        hour = str(t["hour"]) if (messy and rnd.random() < 0.3) else f"{t['hour']:02d}"
        temp = t["temperature"] * 9 / 5 + 32 if t["station"] in FAHRENHEIT else t["temperature"]
        vals = dict(pm25=t["pm25"], pm10=t["pm10"], no=t["no"], temperature=round(temp, 1))
        row = dict(station=name, date=d, hour=hour, **{k: str(v) for k, v in vals.items()})
        if messy:
            for k in ("pm25", "pm10", "no", "temperature"):
                r = rnd.random()
                p = 1.0 if k == "pm25" else 0.4                # PM2.5 is the most important column and has the most faults
                if r < 0.030 * p:
                    row[k] = ""                                  # blank
                elif r < 0.050 * p:
                    row[k] = "NA"                                # NA marker
                elif r < 0.060 * p and k != "temperature":
                    row[k] = str(-round(rnd.uniform(1, 30), 1))  # negative sensor fault
                elif r < 0.065 * p and k != "temperature":
                    row[k] = str(rnd.choice([9999, 5000, 12345])) # impossibly large
                elif r < 0.068 * p and k != "temperature":
                    row[k] = "ERR"                               # text instead of a number
        out.append(row)
        if messy and rnd.random() < 0.01:
            out.append(dict(row))                                # exact duplicate row
    return out


def raw_to_csv_text(raw, with_header=True):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    if with_header:
        w.writerow(HEADER)
    for r in raw:
        w.writerow([r[h] for h in HEADER])
    return buf.getvalue()


# =============================================================== cleaning rules (design A2.1)
def canonical_name(raw, known):
    """' adyar ' -> 'Adyar' (match ignoring case and surrounding blanks against the list of known stations)."""
    return known.get(" ".join(raw.split()).lower(), " ".join(raw.split()).title())


def parse_date(text, day_first):
    """ISO yyyy-mm-dd, or dd/mm/yyyy and dd-mm-yyyy (day first, as used in India). Returns ISO text or None."""
    text = text.strip()
    for fmt in (("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y") if not day_first else ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d")):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def parse_number(text):
    """Returns (value or None, reason) where reason is '', 'missing' or 'not a number'."""
    t = (text or "").strip()
    if t.lower() in MISSING_TOKENS:
        return None, "missing"
    try:
        v = float(t)
    except ValueError:
        return None, "not a number"
    if math.isnan(v) or math.isinf(v):
        return None, "not a number"
    return v, ""


def clean_rows(raw, limit=FILL_LIMIT, stats=None):
    """Rules: (1) fix station name, date and hour; (2) missing / NA / text -> missing; (3) Fahrenheit -> Celsius;
    (4) values outside the valid range -> missing; (5) drop exact duplicates of (station, date, hour), keep the first;
    (6) forward fill up to `limit` consecutive hours inside one station, longer gaps stay missing (and are not averaged).
    Returns a list of (station, date, hour, pm25, pm10, no, temp_c) sorted by station, date, hour."""
    st = stats if stats is not None else {}
    for k in ("rows_in", "missing", "not_numeric", "negative", "too_large", "duplicates", "fahrenheit", "dates_reformatted",
              "names_fixed", "filled", "still_missing", "rows_out", "bad_date_or_hour"):
        st.setdefault(k, 0)
    known = {n.lower(): n for n, _ in STATIONS}
    seen = {}
    for r in raw:
        st["rows_in"] += 1
        name = canonical_name(r["station"], known)
        if name != r["station"]:
            st["names_fixed"] += 1
        d = parse_date(r["date"], name in DAY_FIRST_STATIONS)
        try:
            hour = int(r["hour"].strip())
        except ValueError:
            hour = -1
        if d is None or not 0 <= hour <= 23:
            st["bad_date_or_hour"] += 1
            continue
        if d != r["date"].strip():
            st["dates_reformatted"] += 1
        key = (name, d, hour)
        if key in seen:
            st["duplicates"] += 1
            continue
        vals = []
        for col in ("pm25", "pm10", "no", "temperature"):
            v, why = parse_number(r[col])
            if why == "missing":
                st["missing"] += 1
            elif why == "not a number":
                st["not_numeric"] += 1
            if v is not None and col == "temperature" and name in FAHRENHEIT:
                v = (v - 32) * 5 / 9
                st["fahrenheit"] += 1
            if v is not None:
                lo, hi = LIMITS[col]
                if v < lo:
                    st["negative"] += 1
                    v = None
                elif v > hi:
                    st["too_large"] += 1
                    v = None
            vals.append(v)
        seen[key] = vals
    rows = sorted(seen.items())
    out, last, gap = [], {}, {}
    for (name, d, hour), vals in rows:
        vals = list(vals)
        for i in range(4):
            gk = (name, i)
            if vals[i] is None:
                gap[gk] = gap.get(gk, 0) + 1
                if gk in last and gap[gk] <= limit:
                    vals[i] = last[gk]
                    st["filled"] += 1
                else:
                    st["still_missing"] += 1
            else:
                last[gk] = vals[i]
                gap[gk] = 0
        out.append((name, d, hour) + tuple(None if v is None else round(v, 1) for v in vals))
    st["rows_out"] = len(out)
    return out


# =============================================================== normalisation (design A2.2)
def min_max(values):
    """(v - min) / (max - min) rounded to 3 decimals; all values equal -> zeros (avoids division by zero)."""
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [round((v - lo) / (hi - lo), 3) for v in values]


def z_scores(values):
    """(v - mean) / population standard deviation, rounded to 3 decimals; zero spread -> zeros."""
    m, s = statistics.fmean(values), statistics.pstdev(values)
    if s == 0:
        return [0.0 for _ in values]
    return [round((v - m) / s, 3) for v in values]


# =============================================================== SQLite design (design A1.2)
SCHEMA = """
CREATE TABLE IF NOT EXISTS stations (
    station_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    zone       TEXT,
    temp_unit  TEXT NOT NULL DEFAULT 'C' CHECK (temp_unit IN ('C', 'F'))     -- unit used by the station in its raw files
);
CREATE TABLE IF NOT EXISTS readings (
    station_id INTEGER NOT NULL REFERENCES stations(station_id),
    day        TEXT    NOT NULL,                                              -- ISO yyyy-mm-dd
    hour       INTEGER NOT NULL CHECK (hour BETWEEN 0 AND 23),
    pm25       REAL CHECK (pm25 IS NULL OR pm25 BETWEEN 0 AND 999),
    pm10       REAL,
    no         REAL,
    temp_c     REAL,                                                          -- always Celsius after cleaning
    PRIMARY KEY (station_id, day, hour)
) WITHOUT ROWID;
"""


def create_db(path=":memory:"):
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    con.executemany("INSERT OR IGNORE INTO stations (name, zone, temp_unit) VALUES (?, ?, ?)",
                    [(n, z, "F" if n in FAHRENHEIT else "C") for n, z in STATIONS])
    con.commit()
    return con


def load_readings(con, clean):
    ids = dict(con.execute("SELECT name, station_id FROM stations"))
    con.executemany("INSERT OR REPLACE INTO readings VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [(ids[r[0]],) + r[1:] for r in clean])
    con.commit()
