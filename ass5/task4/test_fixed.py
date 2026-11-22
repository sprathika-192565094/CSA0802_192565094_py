"""Task 4.3 - evidence that the repaired program works."""
import os, builtins
os.chdir(os.path.dirname(os.path.abspath(__file__)))
for f in ("returns.log", "errors.log"):
    if os.path.exists(f):
        os.remove(f)
import library_fixed as lf

days = ["input_days/day1.txt", "input_days/day2.txt", "input_days/day_missing.txt",
        "input_days/day4_bad_encoding.txt", "input_days/day3.txt"]
for d in days:
    print(f"process({d!r}) ->", lf.process(d))
print("\n=== returns.log ===")
print(open("returns.log").read())
print("=== errors.log ===")
print(open("errors.log").read())

handles = []
real_open = builtins.open
def tracking_open(*a, **k):
    h = real_open(*a, **k); handles.append(h); return h
builtins.open = tracking_open
try:
    lf.save_returns(["Book A", None, "Book C"], "test_fail.log")
except TypeError as e:
    print("write() failed ->", type(e).__name__)
builtins.open = real_open
print("handle closed after failure? ->", [h.closed for h in handles])
os.remove("test_fail.log")
