from milkrate import payout, rate_per_litre, ten_day_payment

print("Rate:", rate_per_litre(4.2, 8.7))
print("Payment:", payout(8.5, 4.2, 8.7))
entries = [(100, 4.2, 8.7), (150, 3.5, 8.5), (260, 3.6, 8.6)]
print("Ten-day total (milk, bonus, final):", ten_day_payment(entries, seasonal=True))
