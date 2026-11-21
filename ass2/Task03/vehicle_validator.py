"""Q3 - Vehicle registration number validator (no regular expressions in the main solution)."""
import json
import re
import timeit


def normalise(text):
    """'tn 09 ab 1234' -> 'TN09AB1234' (spaces and hyphens removed, upper case)."""
    # TODO 1 (completed)
    return text.replace(" ", "").replace("-", "").upper()


def is_valid(reg):
    """Valid form: 2 letters, 2 digits, 1 or 2 letters, 4 digits."""
    # TODO 2 (completed)
    n = len(reg)
    if n not in (9, 10):
        return False
    return (reg[:2].isalpha()            # state code
            and reg[2:4].isdigit()       # district
            and reg[4:-4].isalpha()      # series: 1 or 2 letters (length n - 8)
            and reg[-4:].isdigit())      # number


def format_receipt(reg):
    """Format a VALID normalised number as 'TN 09 AB 1234'."""
    return " ".join([reg[:2], reg[2:4], reg[4:-4], reg[-4:]])


def is_valid_regex(reg):
    return re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}", reg) is not None


if __name__ == "__main__":
    print("--- program given in the question ---")
    for raw in ["tn 09 ab 1234", "KA-01-M-0007", "TN9AB1234", "TN 22 1234 AB"]:
        reg = normalise(raw)
        print(f"{raw:15} -> {reg:11} {'valid' if is_valid(reg) else 'INVALID'}")

    print("\n--- six inputs of my choice (predictions written before running) ---")
    tests = [  # raw, predicted
        ("TN-09-AB-1234", True),
        ("Tn09Ab1234", True),
        ("kl 7 cc 4567", False),          # district has only one digit
        ("MH12A9999", True),              # one-letter series, 9 characters
        ("TN09AB123", False),             # only 3 final digits
        ("T109AB1234", False),            # digit '1' where a letter is required
    ]
    ok = True
    rows = []
    for raw, pred in tests:
        reg = normalise(raw)
        got = is_valid(reg)
        ok &= (got == pred) and (is_valid_regex(reg) == got)
        shown = format_receipt(reg) if got else "-"
        rows.append(dict(raw=raw, norm=reg, predicted=pred, observed=got, receipt=shown))
        print(f"{raw:15} -> {reg:11} predicted={str(pred):5} observed={str(got):5} receipt: {shown}")
    print("All predictions matched and regex agrees with slicing version:", ok)

    print("\n--- slicing explanation ---")
    for s in ("MH12A9999", "TN09AB1234"):
        print(f"s = {s!r} (len {len(s)}):  s[-4:] = {s[-4:]!r}   s[4:-4] = {s[4:-4]!r}")

    print("\n--- immutability ---")
    t = "tn09ab1234"
    u = t.upper()
    print("t.upper() ->", u, "| t is still", t, "| same object?", t is u)
    try:
        t[0] = "T"
    except TypeError as e:
        print("t[0] = 'T' ->", type(e).__name__ + ":", e)

    samples = ["TN09AB1234", "MH12A9999", "T109AB1234", "KA01M0007"] * 25
    N = 200
    t_slice = min(timeit.repeat(lambda: [is_valid(s) for s in samples], number=N, repeat=3)) / (N * len(samples)) * 1e9
    t_regex = min(timeit.repeat(lambda: [is_valid_regex(s) for s in samples], number=N, repeat=3)) / (N * len(samples)) * 1e9
    print(f"\nTime per validation: slicing {t_slice:.0f} ns, regex fullmatch {t_regex:.0f} ns")
    json.dump(dict(rows=rows, all_ok=ok, t_slice_ns=round(t_slice), t_regex_ns=round(t_regex)),
              open("results.json", "w"), indent=1)
