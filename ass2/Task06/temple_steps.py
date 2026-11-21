"""Q6 - Recursion and its limits: counting ways to climb temple steps (1 or 2 steps at a time)."""
import json
import math
import subprocess
import sys
import time
from functools import lru_cache

sys.set_int_max_str_digits(100_000)     # allow printing the digit count of very large integers
calls = 0


def ways_naive(n):
    """Ways to climb n temple steps taking 1 or 2 steps at a time."""
    global calls
    calls += 1
    if n <= 1:
        return 1
    return ways_naive(n - 1) + ways_naive(n - 2)


@lru_cache(maxsize=None)
def ways_memo(n):
    # TODO 1 (completed): same base case and recursive case as ways_naive, calling ways_memo
    global calls
    calls += 1
    if n <= 1:
        return 1
    return ways_memo(n - 1) + ways_memo(n - 2)


def ways_loop(n):
    """Loop that keeps only the last two values: O(n) time, O(1) auxiliary space."""
    prev, cur = 1, 1                    # ways(0), ways(1)
    for _ in range(2, n + 1):
        prev, cur = cur, prev + cur
    return cur


def call_tree(n, depth=0, lines=None):
    """Text call tree of the plain recursive version."""
    if lines is None:
        lines = []
    lines.append("    " * depth + f"ways({n})")
    if n > 1:
        call_tree(n - 1, depth + 1, lines)
        call_tree(n - 2, depth + 1, lines)
    return lines


def run(fn, n, memo=False):
    global calls
    if memo:
        fn.cache_clear()
    calls = 0
    t = time.perf_counter()
    value = fn(n)
    return value, calls, time.perf_counter() - t


if __name__ == "__main__":
    out = {}
    print("=== Output required by the question ===")
    v, c, _ = run(ways_naive, 25)
    print("naive:", v, "calls =", c)
    v, c, _ = run(ways_memo, 25, memo=True)
    print("memo :", v, "calls =", c)

    print("\n=== Base case and recursive case ===")
    print("base case: ways(0) = ways(1) = 1   |   recursive case: ways(n) = ways(n-1) + ways(n-2)")

    print("\n=== Correctness check n = 1..6 (manual values from listing the step sequences) ===")
    manual = {1: 1, 2: 2, 3: 3, 4: 5, 5: 8, 6: 13}
    ok = True
    for n, m in manual.items():
        a, b, c3 = ways_naive(n), ways_memo(n), ways_loop(n)
        ok &= (a == b == c3 == m)
        print(f"n={n}: manual={m:2}  naive={a:2}  memo={b:2}  loop={c3:2}")
    print("All agree with the manual values:", ok)

    print("\n=== Call tree for n = 5 ===")
    tree = call_tree(5)
    print("\n".join(tree))
    print("number of calls in the tree:", len(tree))
    out["tree_calls_n5"] = len(tree)

    print("\n=== Growth investigation ===")
    print("Prediction: naive calls = 2*ways(n) - 1 (every call is either a leaf or has two children); memo calls = n + 1.")
    print(f"{'n':>3} {'ways(n)':>10} {'predicted naive':>16} {'naive calls':>12} {'naive time(s)':>14} {'predicted memo':>15} {'memo calls':>11} {'memo time(s)':>13}")
    growth = []
    for n in (10, 20, 25, 30):
        v1, c1, t1 = run(ways_naive, n)
        v2, c2, t2 = run(ways_memo, n, memo=True)
        pred_naive, pred_memo = 2 * v1 - 1, n + 1
        assert v1 == v2 and c1 == pred_naive and c2 == pred_memo
        growth.append(dict(n=n, ways=v1, naive_calls=c1, naive_time=t1, memo_calls=c2, memo_time=t2))
        print(f"{n:>3} {v1:>10} {pred_naive:>16} {c1:>12} {t1:>14.5f} {pred_memo:>15} {c2:>11} {t2:>13.6f}")
    out["growth"] = growth
    ratio = growth[-1]["naive_calls"] / growth[-2]["naive_calls"]
    print(f"Calls ratio n=30 vs n=25: {ratio:.2f} (golden ratio^5 = {((1+5**0.5)/2)**5:.2f})  -> exponential growth")

    print("\n=== Deployment decision: n = 1,000 ===")
    print("sys.getrecursionlimit() =", sys.getrecursionlimit())
    ways_memo.cache_clear()
    try:
        ways_memo(1000)
        print("memo(1000) worked with the default limit")
        out["memo_1000_default"] = "ok"
    except RecursionError as e:
        print("ways_memo(1000) -> RecursionError:", e)
        out["memo_1000_default"] = "RecursionError: " + str(e)

    sys.setrecursionlimit(5000)
    ways_memo.cache_clear()
    calls = 0
    t = time.perf_counter()
    big_memo = ways_memo(1000)
    t_memo = time.perf_counter() - t
    memo_calls = calls
    t = time.perf_counter()
    big_loop = ways_loop(1000)
    t_loop = time.perf_counter() - t
    print(f"after sys.setrecursionlimit(5000): memo(1000) OK, calls={memo_calls}, time={t_memo*1000:.3f} ms")
    print(f"loop(1000): time={t_loop*1000:.3f} ms; digits in the answer = {len(str(big_loop))}; memo == loop: {big_memo == big_loop}")
    out.update(memo_1000_calls=memo_calls, memo_1000_ms=t_memo * 1000, loop_1000_ms=t_loop * 1000,
               digits_1000=len(str(big_loop)), memo_eq_loop=big_memo == big_loop)

    # naive for n = 1000 can not be run: extrapolate from measured speed
    rate = growth[-1]["naive_calls"] / growth[-1]["naive_time"]           # calls per second
    log10_calls = math.log10(2) + (1000 + 1) * math.log10((1 + 5 ** 0.5) / 2) - math.log10(5 ** 0.5)
    log10_seconds = log10_calls - math.log10(rate)
    print(f"naive(1000): about 10^{log10_calls:.0f} calls; at {rate:,.0f} calls/s that is about 10^{log10_seconds:.0f} seconds "
          f"(the universe is ~4.3e17 seconds old) -> NOT executed")
    out.update(naive_1000_log10_calls=log10_calls, naive_1000_log10_seconds=log10_seconds, calls_per_second=rate)

    print("\nHow far can the recursion limit be pushed? (separate process, memoised version, n = 1,000,000, limit 10**7)")
    code = ("import sys\nfrom functools import lru_cache\nsys.setrecursionlimit(10**7)\n"
            "@lru_cache(maxsize=None)\ndef w(n):\n    return 1 if n<=1 else w(n-1)+w(n-2)\nw(1_000_000)\nprint('finished')")
    try:
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
        tail = (r.stderr.strip().splitlines() or [""])[-1]
        print("return code:", r.returncode, "|", r.stdout.strip() or tail)
        out["crash_test"] = dict(returncode=r.returncode, message=r.stdout.strip() or tail)
    except subprocess.TimeoutExpired:
        print("timed out after 120 s")
        out["crash_test"] = dict(returncode=None, message="timeout")

    print("\nLoop version for larger inputs:")
    for n in (10_000, 100_000):
        t = time.perf_counter()
        d = len(str(ways_loop(n)))
        print(f"n={n:>7,}: digits={d}, time={time.perf_counter()-t:.3f} s")
    json.dump(out, open("results.json", "w"), indent=1, default=str)

    # graph of the growth
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ns = list(range(1, 31))
        naive = []
        for n in ns:
            naive.append(2 * ways_loop(n) - 1)
        plt.figure(figsize=(6.5, 4))
        plt.semilogy(ns, naive, "o-", label="plain recursion (calls)")
        plt.semilogy(ns, [n + 1 for n in ns], "s-", label="memoised (calls)")
        plt.xlabel("n (steps)"); plt.ylabel("function calls (log scale)")
        plt.title("Q6: calls grow exponentially without memoisation"); plt.grid(True, alpha=.3); plt.legend()
        plt.tight_layout(); plt.savefig("calls_growth.png", dpi=150)
        print("\nsaved calls_growth.png")
    except ImportError:
        print("matplotlib not installed - graph skipped")
