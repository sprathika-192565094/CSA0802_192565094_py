"""Q1 - Decisions with many boundaries: State Electricity Subsidy Eligibility.

Rules
  * units <= 100            -> FULL subsidy
  * 101 <= units <= 200     -> PARTIAL subsidy, only if the household has a ration card
  * units > 200             -> NO subsidy, unless a member is above 80 years -> SENIOR subsidy
"""
import json
import timeit


# ---------------------------------------------------------------- buggy version
def decide_buggy(units, ration_card, senior):
    """Separate if statements, written the way the 'developer' wrote it.
    The conditions overlap, so one household can receive several subsidies.
    Returns the LIST of subsidies granted."""
    result = []
    if units <= 100:
        result.append("FULL")
    if units <= 200 and ration_card:          # forgot the lower bound (101)
        result.append("PARTIAL")
    if units > 100 and senior:                # should be units > 200
        result.append("SENIOR")
    return result


# ---------------------------------------------------------------- correct version
def decide_elif(units, ration_card, senior):
    """if-elif-else: exactly one branch can run -> exactly one decision."""
    if units <= 100:
        return "FULL"
    elif 101 <= units <= 200:                 # chained comparison
        return "PARTIAL" if ration_card else "NONE"
    else:                                     # units > 200
        return "SENIOR" if senior else "NONE"


# ---------------------------------------------------------------- alternative 1: match-case
def decide_match(units, ration_card, senior):
    match (units, ration_card, senior):
        case (u, _, _) if u <= 100:
            return "FULL"
        case (u, True, _) if u <= 200:
            return "PARTIAL"
        case (u, False, _) if u <= 200:
            return "NONE"
        case (_, _, True):
            return "SENIOR"
        case _:
            return "NONE"


# ---------------------------------------------------------------- alternative 2: slab table
SLABS = [  # (upper limit, rule)
    (100, lambda rc, sr: "FULL"),
    (200, lambda rc, sr: "PARTIAL" if rc else "NONE"),
    (float("inf"), lambda rc, sr: "SENIOR" if sr else "NONE"),
]


def decide_table(units, ration_card, senior):
    for upper, rule in SLABS:                 # O(k) for k slabs
        if units <= upper:
            return rule(ration_card, senior)


# ---------------------------------------------------------------- test data
# (units, ration_card, senior_above_80, predicted decision made BEFORE running code)
HOUSEHOLDS = [
    (150, True,  True,  "PARTIAL"),   # senior member below 201 units must NOT add a second subsidy
    (100, False, False, "FULL"),      # boundary
    (100, True,  False, "FULL"),      # boundary, ration card must not add PARTIAL
    (101, True,  False, "PARTIAL"),   # boundary
    (101, False, False, "NONE"),      # boundary
    (200, True,  False, "PARTIAL"),   # boundary
    (201, False, True,  "SENIOR"),    # boundary
    (201, True,  False, "NONE"),      # boundary, ration card is irrelevant above 200
]

if __name__ == "__main__":
    print("units rc    senior | predicted | buggy (separate ifs)    | if-elif | match | table")
    print("-" * 92)
    mismatch_buggy = 0
    all_agree = True
    rows = []
    for u, rc, sr, pred in HOUSEHOLDS:
        b = decide_buggy(u, rc, sr)
        e = decide_elif(u, rc, sr)
        m = decide_match(u, rc, sr)
        t = decide_table(u, rc, sr)
        expected = [] if pred == "NONE" else [pred]       # NONE = no subsidy granted
        if b != expected:
            mismatch_buggy += 1
        all_agree &= (e == m == t == pred)
        rows.append(dict(units=u, ration=rc, senior=sr, predicted=pred, buggy=b, elif_=e, match=m, table=t))
        print(f"{u:5} {str(rc):5} {str(sr):6} | {pred:9} | {str(b):23} | {e:7} | {m:5} | {t}")
    print()
    print("Households where the separate-if version gave a WRONG result:", mismatch_buggy, "of", len(HOUSEHOLDS))
    print("if-elif-else, match-case and table all equal the predictions:", all_agree)

    # exhaustive check over all combinations 0..300 units
    bad = sum(1 for u in range(0, 301) for rc in (False, True) for sr in (False, True)
              if not (decide_elif(u, rc, sr) == decide_match(u, rc, sr) == decide_table(u, rc, sr)))
    dbl = sum(1 for u in range(0, 301) for rc in (False, True) for sr in (False, True)
              if len(decide_buggy(u, rc, sr)) > 1)
    print("Exhaustive check (301 x 2 x 2 = 1204 cases): disagreements between the 3 correct versions =", bad)
    print("Exhaustive check: cases where the buggy version grants MORE THAN ONE subsidy =", dbl)

    # timing per decision
    N = 200_000
    args = (150, True, False)
    timings = {}
    for name, fn in [("if-elif-else", decide_elif), ("match-case", decide_match), ("slab table", decide_table)]:
        t = min(timeit.repeat(lambda: fn(*args), number=N, repeat=3)) / N * 1e9
        timings[name] = round(t, 1)
    print("\nTime per decision (ns, units=150, best of 3 x 200000 calls):", timings)
    json.dump(dict(rows=rows, buggy_wrong=mismatch_buggy, buggy_double_exhaustive=dbl, timings_ns=timings),
              open("results.json", "w"), indent=1)
