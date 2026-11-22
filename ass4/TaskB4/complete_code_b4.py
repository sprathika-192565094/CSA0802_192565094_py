"""B4 - Complete the Code (TODO 1): lexicon based sentiment scorer with negation."""
POSITIVE = {"good", "clean", "fast", "helpful", "improved"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
NEGATORS = {"not", "never", "no"}


def score(text):
    """+1 per positive word, -1 per negative word; a preceding negator flips it."""
    words = text.lower().replace(".", " ").replace(",", " ").split()
    total = 0
    # TODO 1 (completed): for each word find its value (+1, -1 or 0); if the previous word is a negator flip the sign; add it to total
    for i, w in enumerate(words):
        value = 1 if w in POSITIVE else -1 if w in NEGATIVE else 0
        if value != 0 and i > 0 and words[i - 1] in NEGATORS:
            value = -value
        total += value
    return total


def label(text):
    s = score(text)
    return "positive" if s > 0 else "negative" if s < 0 else "neutral"


for c in ["Roads are clean and the bus was fast.",
          "Smoke from the factory, air is bad.",
          "The staff were not helpful.",
          "Not bad, service improved."]:
    print(f"{label(c):8} | {c}")

print("\n--- Find a complaint that the scorer labels wrongly and explain why ---")
wrong = "The staff were never really helpful."
print(f"{label(wrong):8} | {wrong}   (a human reads this as negative)")
print("Reason: the negator 'never' is not DIRECTLY before 'helpful' (the word 'really' is between them), so the rule 'previous word is a negator' does not fire and 'helpful' counts as +1.")
wrong2 = "Terrible stench near the dump."
print(f"{label(wrong2):8} | {wrong2}   (a human reads this as negative)")
print("Reason: 'terrible' and 'stench' are not in the word list, so the total stays 0 -> neutral.")
