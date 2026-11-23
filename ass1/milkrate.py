"""Ksheera Village Milk Co-operative payment calculator."""
from decimal import Decimal, ROUND_HALF_UP
from time import perf_counter

D = Decimal
CENT = D("0.01")
STEP = D("0.1")
ORIGINAL = {"base": D("30.00"), "fat_step": D("0.40"), "snf_step": D("0.30")}
SEASONAL = {"base": D("32.00"), "fat_step": D("0.45"), "snf_step": D("0.30")}

def money(value):
    return D(value).quantize(CENT, rounding=ROUND_HALF_UP)

def validate_entry(farmer_id, litres, fat, snf, shift):
    farmer_id = str(farmer_id).strip()
    litres, fat, snf = D(str(litres)), D(str(fat)), D(str(snf))
    shift = str(shift).strip().lower()
    if not farmer_id:
        raise ValueError("Farmer ID cannot be empty")
    if litres <= 0:
        raise ValueError("Milk quantity must be positive")
    if not D("2.0") <= fat <= D("7.0"):
        raise ValueError("Fat must be between 2.0 and 7.0")
    if shift not in ("morning", "evening"):
        raise ValueError("Shift must be Morning or Evening")
    # Assignment does not specify permitted SNF bounds; do not invent them.
    return farmer_id, litres, fat, snf, shift.title()

def steps(value, standard):
    # Assumption: round fractional 0.1 percentage-point steps half-up.
    return int(((value - standard) / STEP).quantize(D("1"), rounding=ROUND_HALF_UP))

def rate_per_litre(fat, snf, seasonal=False):
    fat, snf = D(str(fat)), D(str(snf))
    card = SEASONAL if seasonal else ORIGINAL
    rate = (card["base"] + steps(fat, D("3.5")) * card["fat_step"]
            + steps(snf, D("8.5")) * card["snf_step"])
    return money(rate)

def payout(litres, fat, snf, seasonal=False):
    litres, fat, snf = D(str(litres)), D(str(fat)), D(str(snf))
    if litres <= 0:
        raise ValueError("Milk quantity must be positive")
    if not D("2.0") <= fat <= D("7.0"):
        raise ValueError("Fat must be between 2.0 and 7.0")
    return money(litres * rate_per_litre(fat, snf, seasonal))

def volume_bonus(total_litres):
    total_litres = D(str(total_litres))
    return money(total_litres * D("0.50")) if total_litres > D("500") else D("0.00")

def ten_day_payment(entries, seasonal=False):
    # entries: iterable of (litres, fat, snf); each payment is rounded to paise.
    total_litres = sum((D(str(e[0])) for e in entries), D("0"))
    milk_total = sum((payout(*e, seasonal=seasonal) for e in entries), D("0.00"))
    bonus = volume_bonus(total_litres)
    return money(milk_total), bonus, money(milk_total + bonus)

def read_entry():
    farmer = input("Farmer ID: ").strip()
    litres = input("Litres: ").strip()
    fat = input("Fat %: ").strip()
    snf = input("SNF %: ").strip()
    shift = input("Shift (Morning/Evening): ").strip()
    try:
        return validate_entry(farmer, litres, fat, snf, shift)
    except Exception as exc:
        print("Invalid input:", exc)
        return None

def run_tests():
    assert rate_per_litre("3.5", "8.5") == D("30.00")
    assert rate_per_litre("4.2", "8.7") == D("33.40")
    assert rate_per_litre("3.1", "8.3") == D("27.80")
    assert payout(10, 3.5, 8.5) == D("300.00")
    assert payout(10, 7.0, 8.5) == D("440.00")
    assert payout(10, 2.0, 8.5) == D("240.00")
    assert rate_per_litre(3.5, 8.5, True) == D("32.00")
    assert rate_per_litre(4.2, 8.7, True) == D("35.75")
    assert volume_bonus(500) == D("0.00")
    assert volume_bonus(501) == D("250.50")
    for args in [(0, 3.5, 8.5), (-1, 3.5, 8.5), (10, 7.1, 8.5)]:
        try:
            payout(*args)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Expected ValueError for {args}")
    print("All calculator tests passed.")

def benchmark():
    print("\\nBenchmark (times vary by computer)")
    for n in (300, 6000, 150000):
        start = perf_counter()
        ftotal = 0.0
        for _ in range(n):
            ftotal += 33.40
        ft = perf_counter() - start
        start = perf_counter()
        dtotal = D("0.00")
        amount = D("33.40")
        for _ in range(n):
            dtotal += amount
        dt = perf_counter() - start
        print(f"n={n}: float={ftotal:.8f} ({ft:.6f}s); Decimal={dtotal} ({dt:.6f}s)")

if __name__ == "__main__":
    run_tests()
    sample = [(10, 3.5, 8.5), (8.5, 4.2, 8.7), (12, 3.1, 8.3)]
    print("\\nSample payments:")
    total = D("0.00")
    for i, (litres, fat, snf) in enumerate(sample, 1):
        amount = payout(litres, fat, snf)
        total += amount
        print(f"Entry {i}: rate ₹{rate_per_litre(fat, snf)}; payment ₹{amount}")
    print("Sample total: ₹", total)
    print("\\nSeasonal demonstration:")
    print("Seasonal rate for 4.2% fat, 8.7% SNF: ₹", rate_per_litre(4.2, 8.7, True))
    print("Bonus at 501 L: ₹", volume_bonus(501))
    benchmark()
