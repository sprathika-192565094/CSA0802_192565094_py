"""Q4 - Sets: elective registration clash detection."""
import json
import random
import sys
import time

res = {}


def section(t):
    print("\n=== " + t + " ===")


# ---------------------------------------------------------------- program given in the question
section("Program from the question (TODO 1 completed with set OPERATORS only)")
ai_elective = {"192311001", "192311004", "192311007", "192311009"}
iot_elective = {"192311002", "192311004", "192311009", "192311010"}
all_students = {f"1923110{i:02d}" for i in range(1, 11)}
# TODO 1 (completed): students in both electives, in exactly one, and in neither
both = ai_elective & iot_elective
exactly_one = ai_elective ^ iot_elective
neither = all_students - (ai_elective | iot_elective)
print("clash :", sorted(both))
print("exactly one:", sorted(exactly_one))
print("neither :", sorted(neither))

section("Rewrite of TODO 1 using set METHODS")
both_m = ai_elective.intersection(iot_elective)
exactly_one_m = ai_elective.symmetric_difference(iot_elective)
neither_m = all_students.difference(ai_elective.union(iot_elective))
print("clash :", sorted(both_m))
print("exactly one:", sorted(exactly_one_m))
print("neither :", sorted(neither_m))
print("operators and methods give the same results:", both == both_m and exactly_one == exactly_one_m and neither == neither_m)

section("Other reports (sorted) and duplicate registrations")
print("registered for at least one (union)  :", sorted(ai_elective | iot_elective))
print("AI only (difference)                 :", sorted(ai_elective - iot_elective))
print("IoT only (difference)                :", sorted(iot_elective - ai_elective))
raw_form_entries = ["192311001", "192311004", "192311001", "192311007", "192311004", "192311009"]   # duplicates from repeated submissions
print("raw entries :", raw_form_entries, "->", len(raw_form_entries), "entries")
clean = set(raw_form_entries)
print("as a set    :", sorted(clean), "->", len(clean), "students (duplicates removed automatically)")
print("subset / superset checks:", both <= ai_elective, ai_elective >= both, "| disjoint(AI only, IoT only):",
      (ai_elective - iot_elective).isdisjoint(iot_elective - ai_elective))

section("Check by hand (small case)")
print("AI = {1,4,7,9}, IoT = {2,4,9,10}, all = {1..10}")
print("  both = {4, 9}: the numbers that appear in both lists")
print("  exactly one = {1, 7} from AI plus {2, 10} from IoT = {1, 2, 7, 10}")
print("  neither = all - {1,2,4,7,9,10} = {3, 5, 6, 8}")
print("  program agrees with the hand result:",
      sorted(both) == ["192311004", "192311009"] and sorted(exactly_one) == [f"1923110{i:02d}" for i in (1, 2, 7, 10)]
      and sorted(neither) == [f"1923110{i:02d}" for i in (3, 5, 6, 8)])

section("Edge cases: empty electives and identical electives")
E = set()
print("both empty        : both", E & E, "| exactly one", E ^ E, "| neither", len(all_students - (E | E)), "of 10 students")
print("one empty         : both", ai_elective & E, "| exactly one", sorted(ai_elective ^ E) == sorted(ai_elective), "(all of AI)")
print("identical electives: both", sorted(ai_elective & ai_elective) == sorted(ai_elective), "| exactly one", ai_elective ^ ai_elective, "(empty set)")

section("Why sets cannot contain lists but can contain tuples")
try:
    {["192311001"]}
except TypeError as e:
    print("{['192311001']} -> TypeError:", e)
print("{('192311001', 'AI')} ->", {("192311001", "AI")}, "(a tuple of hashable items is hashable)")
try:
    {("192311001", ["AI"])}
except TypeError as e:
    print("a tuple that CONTAINS a list is also rejected -> TypeError:", e)
print("frozenset is hashable and can be an element:", {frozenset({"a", "b"})})
s = {"a"}
s.add("a"); s.add("a")
print("adding an existing element does nothing:", s, "(an element is stored once because equal elements have equal hashes)")

# ---------------------------------------------------------------- experiments
def best(fn, *a, repeat=5):
    r = []
    for _ in range(repeat):
        t = time.perf_counter(); fn(*a); r.append(time.perf_counter() - t)
    return min(r)


section("x in list and x in set (register numbers; best of 5; 1,000 look-ups each, worst case: x not present)")
print(f"{'size':>10} | {'list (s)':>10} {'set (s)':>10} | ratio | list bytes   set bytes")
rows = []
for n in (10_000, 100_000, 1_000_000):
    nums = [f"{19231100000 + i}" for i in range(n)]
    L, S = nums, set(nums)
    probes = ["x" + str(i) for i in range(1000)]                       # absent: list must scan every element
    reps = 1 if n == 1_000_000 else 3
    t_l = best(lambda: [p in L for p in probes[:100 if n >= 100_000 else 1000]], repeat=reps)
    t_l = t_l * (1000 / (100 if n >= 100_000 else 1000))               # scaled to 1,000 look-ups
    t_s = best(lambda: [p in S for p in probes])
    rows.append(dict(n=n, list=t_l, set=t_s, list_bytes=sys.getsizeof(L), set_bytes=sys.getsizeof(S)))
    print(f"{n:>10,} | {t_l:>10.5f} {t_s:>10.6f} | {t_l / t_s:>6.0f}x | {sys.getsizeof(L):>10,} {sys.getsizeof(S):>11,}")
res["membership"] = rows
print("(the list time grows 10x when n grows 10x -> O(n); the set time stays the same -> O(1) on average)")

section("Finding the common students: nested loops, sort + walk, and the & operator")


def common_nested(a, b):
    out = []
    for x in a:
        for y in b:
            if x == y:
                out.append(x)
                break
    return out


def common_sorted(a, b):
    a, b = sorted(a), sorted(b)
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i]); i += 1; j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out


def common_set(a, b):
    return sorted(set(a) & set(b))


print(f"{'n = m':>9} {'common':>7} | {'nested loops':>13} {'sort + walk':>12} {'set &':>10} | comparisons nested (n*m)")
crow = []
rnd = random.Random(5)
for n in (1_000, 3_000, 6_000, 200_000):
    pool = [f"{19231100000 + i}" for i in range(2 * n)]
    a, b = rnd.sample(pool, n), rnd.sample(pool, n)
    ref = common_set(a, b)
    assert sorted(common_sorted(a, b)) == ref
    t_n = None
    if n <= 6_000:
        assert sorted(common_nested(a, b)) == ref
        t_n = best(common_nested, a, b, repeat=1)
    t_w, t_s = best(common_sorted, a, b, repeat=3), best(common_set, a, b, repeat=3)
    crow.append(dict(n=n, common=len(ref), nested=t_n, sorted=t_w, set=t_s))
    print(f"{n:>9,} {len(ref):>7,} | {('%.4f' % t_n) if t_n is not None else 'not run':>13} {t_w:>12.4f} {t_s:>10.4f} | {n * n:,}")
res["common"] = crow
json.dump(res, open("results.json", "w"), indent=1)
