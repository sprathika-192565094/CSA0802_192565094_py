"""B1 - Complete the Code (TODO 1 and TODO 2) + extra check for readings above 999."""
import csv
import io

RAW = """station,date,pm25
Adyar,2026-10-01,48
Adyar,2026-10-02,NA
Adyar,2026-10-03,
Guindy,2026-10-01,95
Guindy,2026-10-02,-5
Guindy,2026-10-03,121
"""


def load_clean(text):
    """Returns (station, date, pm25) tuples for valid, non-negative readings only."""
    rows = []
    # TODO 1 (completed): read with csv.DictReader; skip rows whose pm25 is empty, 'NA' or negative; convert to float
    for row in csv.DictReader(io.StringIO(text)):
        raw = row["pm25"].strip()
        if raw == "" or raw.upper() == "NA":
            continue
        value = float(raw)
        if value < 0 or value > 999:            # extra check required by the question: skip readings above 999
            continue
        rows.append((row["station"], row["date"], value))
    return rows


def min_max(values):
    # TODO 2 (completed): scale to 0-1 with (v - min) / (max - min), rounded to 3 decimals
    lo, hi = min(values), max(values)
    return [round((v - lo) / (hi - lo), 3) for v in values]


clean = load_clean(RAW)
print(clean)
print(min_max([pm for _, _, pm in clean]))

print("\n--- extra test: a row above 999 must be skipped ---")
RAW2 = RAW + "Adyar,2026-10-04,1500\nGuindy,2026-10-04,999\n"
clean2 = load_clean(RAW2)
print(clean2)
print("1500 skipped:", all(v != 1500 for _, _, v in clean2), "| 999 kept (boundary):", ("Guindy", "2026-10-04", 999.0) in clean2)
print("expected output of the question reproduced:", clean == [("Adyar", "2026-10-01", 48.0), ("Guindy", "2026-10-01", 95.0), ("Guindy", "2026-10-03", 121.0)]
      and min_max([pm for _, _, pm in clean]) == [0.0, 0.644, 1.0])
