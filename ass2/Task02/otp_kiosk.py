"""Q2 - Loops that count attempts: OTP verification at a bank kiosk.
Inputs are scripted (lists) so the program is repeatable and can be executed without typing."""
import json

OTP = "482913"
ANSWER = "chennai"          # security-question answer (changed condition)


def make_reader(inputs):
    it = iter(inputs)
    return lambda prompt="": next(it, "")


# ------------------------------------------------ 1. while version
def verify_while(read):
    attempts = 0
    while attempts < 3:
        code = read("Enter OTP: ").strip()
        if code == "":
            continue                      # blank entry: NOT counted, ask again
        attempts += 1                     # counter updated AFTER a real entry
        if code == OTP:
            return f"ACCESS GRANTED on attempt {attempts}"
    return "ACCOUNT LOCKED for 30 minutes"


# ------------------------------------------------ 2. for-range(3) version with loop-else
def verify_for(read):
    for attempt in range(1, 4):
        code = ""
        while code == "":                 # blank entries do not consume an attempt
            code = read("Enter OTP: ").strip()
        if code == OTP:
            return f"ACCESS GRANTED on attempt {attempt}"
    else:                                 # runs only when the loop finished WITHOUT break/return
        return "ACCOUNT LOCKED for 30 minutes"


# ------------------------------------------------ 3. demonstration of break / continue / pass / else
def demo_control_statements(read):
    log = []
    for attempt in range(1, 4):
        code = read("Enter OTP: ").strip()
        if code == "":
            log.append(f"slot {attempt}: blank -> continue (skip the rest of this iteration)")
            continue
        if not code.isdigit():
            pass                          # placeholder: later we may log non-numeric input
        if code == OTP:
            log.append(f"slot {attempt}: correct -> break")
            break
        log.append(f"slot {attempt}: wrong")
    else:
        log.append("loop-else executed: no break happened -> lock account")
    return log


# ------------------------------------------------ changed condition: +2 attempts after security question
def verify_extended(read, answer_given):
    attempts, allowed, bonus_used = 0, 3, False
    while attempts < allowed:
        code = read("Enter OTP: ").strip()
        if code == "":
            continue
        attempts += 1
        if code == OTP:
            return f"ACCESS GRANTED on attempt {attempts} (allowed so far: {allowed})"
        if attempts == allowed and not bonus_used:     # three failures: offer the security question
            bonus_used = True
            if answer_given.strip().lower() == ANSWER:
                allowed += 2
    return f"ACCOUNT LOCKED for 30 minutes after {attempts} attempts"


# ------------------------------------------------ alternative concept: recursion
def verify_recursive(read, attempt=1):
    if attempt > 3:
        return "ACCOUNT LOCKED for 30 minutes"
    code = read("Enter OTP: ").strip()
    if code == "":
        return verify_recursive(read, attempt)         # blank: same attempt number
    if code == OTP:
        return f"ACCESS GRANTED on attempt {attempt}"
    return verify_recursive(read, attempt + 1)


if __name__ == "__main__":
    scenarios = {
        "correct on 1st try": ["482913"],
        "correct on 3rd try": ["111111", "222222", "482913"],
        "blank entries ignored, correct on 2nd real try": ["", "111111", "", "", "482913"],
        "three wrong -> lock": ["1", "2", "3"],
        "three wrong, then correct 4th (must still lock)": ["1", "2", "3", "482913"],
    }
    res = {}
    for name, inputs in scenarios.items():
        w = verify_while(make_reader(inputs))
        f = verify_for(make_reader(inputs))
        r = verify_recursive(make_reader(inputs))
        print(f"{name}\n    while    : {w}\n    for/else : {f}\n    recursive: {r}")
        assert w == f == r
        res[name] = w
    print("\nDemo of break / continue / pass / loop-else")
    for case in (["", "111111", "482913"], ["1", "2", "3"]):
        print("  inputs:", case)
        for line in demo_control_statements(make_reader(case)):
            print("    ", line)

    print("\nChanged condition (two extra attempts after a correct security answer)")
    ext = {
        "3 wrong, correct security answer, 4th attempt correct": (["1", "2", "3", "482913"], "Chennai"),
        "3 wrong, correct security answer, 5 wrong in total": (["1", "2", "3", "4", "5"], "chennai"),
        "3 wrong, WRONG security answer, 4th attempt ignored": (["1", "2", "3", "482913"], "madurai"),
    }
    for name, (inputs, ans) in ext.items():
        print(f"  {name}: {verify_extended(make_reader(inputs), ans)}")
    json.dump(res, open("results.json", "w"), indent=1)
