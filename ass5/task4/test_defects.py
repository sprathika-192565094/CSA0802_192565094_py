"""Task 4.2 - evidence: run process() for three days and show each defect."""
import os, builtins
os.chdir(os.path.dirname(os.path.abspath(__file__)))
if os.path.exists("returns.log"):
    os.remove("returns.log")
import buggy_library as b

for day in ("input_days/day1.txt", "input_days/day2.txt", "input_days/day3.txt"):
    b.process(day)
print("=== returns.log after three days (original program) ===")
print(repr(open("returns.log").read()))
print("-> Defect 1: only day 3 survives ('w' mode truncates the file every call)")
print("-> Defect 2: books are glued together: no newline is written after each title")

print()
handles = []
real_open = builtins.open
def tracking_open(*a, **k):
    h = real_open(*a, **k); handles.append(h); return h
builtins.open = tracking_open
try:
    b.save_returns(["Book A", None, "Book C"])        # None makes write() fail
except TypeError as e:
    print("write() failed ->", type(e).__name__ + ":", e)
builtins.open = real_open
log_handles = [h for h in handles if h.name == "returns.log"]
print("returns.log handle closed after the failure? ->", log_handles[0].closed)
print("-> Defect 3: log.close() is never reached, so the file stays open (leak)")

print()
try:
    b.process("input_days/day4_bad_encoding.txt")
except UnicodeDecodeError as e:
    print("process() crashed with", type(e).__name__)
print("Files containing an error message:", [f for f in os.listdir('.') if f.endswith('.log') and f != 'returns.log'] or "none")
print("-> Defect 4: only FileNotFoundError is caught and it is merely printed; every other error stops the run with nothing saved")
print("-> Defect 5: split('\\n') leaves a trailing empty string and the input file is never closed either")
os.remove("returns.log")
