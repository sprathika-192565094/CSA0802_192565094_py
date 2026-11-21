"""Q7 - Day-4 Design Challenge: Diagnose, Redesign and Validate.
Selected program: the plain recursive ways_naive(n) from Q6 (temple steps).

The redesign is written by hand (a dictionary memo and a two-variable loop); it does not
import lru_cache or any other ready-made helper for the job."""
import json
import sys
import time
import tracemalloc
from collections import Counter

sys.set_int_max_str_digits(100_000)
calls = 0


# =============================================================== ORIGINAL
def ways_original(n):
    global calls
    calls += 1
    if n <= 1:
        return 1
    return ways_original(n - 1) + ways_original(n - 2)


# =============================================================== REDESIGN (intermediate): own dictionary memo
def ways_dict_memo(n, memo=None):
    global calls
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    calls += 1
    memo[n] = 1 if n <= 1 else ways_dict_memo(n - 1, memo) + ways_dict_memo(n - 2, memo)
    return memo[n]


# =============================================================== REDESIGN (final): bottom-up, only two values kept
def ways_redesigned(n):
    """Returns (answer, number_of_additions). ways(k) needs only ways(k-1) and ways(k-2),
    so each value is computed once, in increasing order of k, and older values are forgotten."""
    prev, cur, additions = 1, 1, 0
    for _ in range(2, n + 1):
        prev, cur = cur, prev + cur
        additions += 1
    return cur, additions


def ways_table(n):
    """Bottom-up with a full table (used only for the memory comparison)."""
    t = [1, 1] + [0] * max(0, n - 1)
    for k in range(2, n + 1):
        t[k] = t[k - 1] + t[k - 2]
    return t[n]


def best_time(fn, repeat, *args):
    """Average seconds per call over `repeat` calls, best of 3 batches."""
    best = float("inf")
    for _ in range(3):
        t = time.perf_counter()
        for _ in range(repeat):
            fn(*args)
        best = min(best, (time.perf_counter() - t) / repeat)
    return best


if __name__ == "__main__":
    res = {}
    # ------------------------------------------------------------ A. DIAGNOSE
    print("=== A. DIAGNOSE THE BOTTLENECK (n = 25) ===")
    counter = Counter()

    def instrumented(n):
        counter[n] += 1
        if n <= 1:
            return 1
        return instrumented(n - 1) + instrumented(n - 2)

    instrumented(25)
    total = sum(counter.values())
    print("total calls:", total, "| distinct arguments actually needed:", len(counter))
    print("how many times each argument is computed (k : times):")
    for k in (25, 24, 23, 20, 15, 10, 5, 3, 2, 1, 0):
        print(f"   ways({k:2}) computed {counter[k]:>7,} times")
    wasted = total - len(counter)
    print(f"calls that repeat an already-computed value: {wasted:,} of {total:,} = {wasted/total*100:.3f}%")
    print("Where the work is done: the leaves ways(1)/ways(0) account for",
          f"{counter[1] + counter[0]:,} of {total:,} calls ({(counter[1]+counter[0])/total*100:.1f}%).")
    res["diagnose"] = dict(total=total, distinct=len(counter), wasted_pct=wasted / total * 100,
                           counts={k: counter[k] for k in (25, 20, 15, 10, 5, 2, 1, 0)})

    # ------------------------------------------------------------ B/D. objective and prediction
    print("\n=== B. DESIGN OBJECTIVE ===")
    print("For n = 30 reduce the number of operations from 2,692,537 calls to at most n + 1 = 31 operations,")
    print("make the running time at least 1,000 times shorter, and make n = 1,000 computable with no RecursionError.")
    print("\n=== D. PREDICTION (written before measuring the redesign) ===")
    print("Operations: original grows like 1.618^n, redesign like n -> for n = 30 about 2.69e6 / 29 = 90,000 times fewer.")
    print("Time: at least 1,000 times faster for n = 30 (additions are cheaper than function calls); the gap widens with n.")

    # ------------------------------------------------------------ E. VALIDATE
    print("\n=== E. IMPLEMENT AND VALIDATE (same inputs for both) ===")
    print(f"{'n':>3} {'answer':>9} | {'orig calls':>11} {'orig time(s)':>13} | {'new adds':>9} {'new time(s)':>12} | {'ops reduction':>14} {'speed-up':>12}")
    rows = []
    for n in (10, 20, 25, 30, 35):
        calls = 0
        t = time.perf_counter()
        a = ways_original(n)
        t_o = time.perf_counter() - t
        c_o = calls
        b, adds = ways_redesigned(n)
        assert a == b == ways_table(n)
        calls = 0
        assert ways_dict_memo(n) == a
        t_n = best_time(ways_redesigned, 20000, n)
        rows.append(dict(n=n, answer=a, orig_calls=c_o, orig_time=t_o, new_adds=adds, new_time=t_n,
                         ops_reduction=c_o / adds, speedup=t_o / t_n, dict_memo_calls=calls))
        print(f"{n:>3} {a:>9} | {c_o:>11,} {t_o:>13.6f} | {adds:>9} {t_n:>12.8f} | {c_o/adds:>13,.0f}x {t_o/t_n:>11,.0f}x")
    res["rows"] = rows
    print("Edge cases n = 0, 1:", ways_redesigned(0)[0], ways_redesigned(1)[0], "(both must equal 1)")

    print("\nBeyond what the original can do:")
    big = {}
    for n in (1_000, 10_000, 100_000):
        t_n = best_time(ways_redesigned, 5, n)
        ans, adds = ways_redesigned(n)
        big[n] = dict(time=t_n, digits=len(str(ans)), adds=adds)
        print(f"  n={n:>7,}: {adds:>7,} additions, {t_n:.5f} s, answer has {len(str(ans)):,} digits")
    res["big"] = big

    print("\nMemory comparison at n = 20,000 (tracemalloc peak):")
    mem = {}
    for name, fn in (("redesign (two values)", lambda n: ways_redesigned(n)), ("table of all values", ways_table)):
        tracemalloc.start()
        fn(20_000)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        mem[name] = peak
        print(f"  {name:24} peak = {peak/1024:,.0f} KiB")
    res["mem"] = mem

    # recursion-depth side effect of the intermediate design
    try:
        calls = 0
        ways_dict_memo(1500)
        r = "worked"
    except RecursionError:
        r = "RecursionError (a dictionary memo is still recursive)"
    print("\nIntermediate design ways_dict_memo(1500) with the default limit:", r)
    res["dict_memo_1500"] = r

    # ------------------------------------------------------------ F. DEFEND
    last = rows[3]
    print("\n=== F. DEFEND THE FINAL DESIGN ===")
    print(f"Objective achieved for n = 30: operations {last['orig_calls']:,} -> {last['new_adds']} "
          f"({last['ops_reduction']:,.0f}x fewer); time {last['orig_time']:.4f} s -> {last['new_time']*1e6:.2f} microseconds "
          f"({last['speedup']:,.0f}x faster).")
    json.dump(res, open("results.json", "w"), indent=1, default=str)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ns = [r["n"] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].semilogy(ns, [r["orig_calls"] for r in rows], "o-", label="original (calls)")
    ax[0].semilogy(ns, [r["new_adds"] for r in rows], "s-", label="redesign (additions)")
    ax[0].set_xlabel("n"); ax[0].set_ylabel("operations (log scale)"); ax[0].set_title("Operation counts"); ax[0].legend(); ax[0].grid(alpha=.3)
    ax[1].semilogy(ns, [r["orig_time"] for r in rows], "o-", label="original")
    ax[1].semilogy(ns, [r["new_time"] for r in rows], "s-", label="redesign")
    ax[1].set_xlabel("n"); ax[1].set_ylabel("seconds (log scale)"); ax[1].set_title("Execution time"); ax[1].legend(); ax[1].grid(alpha=.3)
    plt.tight_layout(); plt.savefig("original_vs_redesign.png", dpi=150)
    print("saved original_vs_redesign.png")
