"""Q3 - Dictionaries: farmer helpline (Kisan call centre) complaint analysis."""
import json
import random
import string
import time
from collections import Counter

res = {}
TABLE = str.maketrans("", "", string.punctuation)


def words_of(text):
    """lower-case, remove punctuation, split on white space."""
    return text.lower().translate(TABLE).split()


# ---------------------------------------------------------------- program given in the question
calls = [
    "seeds not received seeds delayed",
    "fertiliser price high",
    "seeds price high subsidy not received",
]
STOP = {"not", "high"}
STOP_BIG = STOP | {"the", "is", "for", "my", "has", "been"}      # stop words used for the generated data


def frequencies(texts, stop):
    # TODO 1 (completed): dictionary word -> count for every word that is not in stop, using dict.get()
    counts = {}
    for text in texts:
        for w in words_of(text):
            if w not in stop:
                counts[w] = counts.get(w, 0) + 1
    return counts


def top(counts, k):
    # TODO 2 (completed): k most frequent (word, count) pairs, highest count first, alphabetical for ties
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


# ---------------------------------------------------------------- variants
def frequencies_setdefault(texts, stop):
    counts = {}
    for text in texts:
        for w in words_of(text):
            if w not in stop:
                counts.setdefault(w, 0)          # make sure the key exists ...
                counts[w] += 1                   # ... then add one
    return counts


def frequencies_counter(texts, stop):
    return Counter(w for text in texts for w in words_of(text) if w not in stop)


def frequencies_listcount(texts, stop):
    """Alternative concept: list.count() for every distinct word -> O(n * d)."""
    words = [w for text in texts for w in words_of(text) if w not in stop]
    return {w: words.count(w) for w in set(words)}


def group_by(records, field):
    """dictionary of lists: field value -> list of complaint texts (setdefault creates the list on first use)."""
    groups = {}
    for rec in records:
        groups.setdefault(rec[field], []).append(rec["text"])
    return groups


# ---------------------------------------------------------------- data generator
def make_complaints(n, vocab=500, seed=7):
    rnd = random.Random(seed)
    base = ["seeds", "fertiliser", "price", "subsidy", "pump", "loan", "insurance", "water", "pest", "market",
            "received", "delayed", "rejected", "damaged", "supply", "credit", "rain", "tractor", "payment", "drought"]
    stop_pool = ["not", "high", "the", "is", "for", "my", "has", "been"]
    words = base + [f"item{i}" for i in range(vocab - len(base))]
    weights = [1 / (r + 1) for r in range(len(words))]            # a few words are very frequent, a long tail is rare
    districts = ["Madurai", "Salem", "Erode", "Theni", "Vellore", "Tiruppur", "Karur", "Nagapattinam", "Thanjavur", "Dindigul"]
    crops = ["paddy", "cotton", "sugarcane", "banana", "groundnut", "maize", "turmeric", "coconut"]
    out = []
    for _ in range(n):
        ws = rnd.choices(words, weights, k=5) + rnd.choices(stop_pool, k=2)
        rnd.shuffle(ws)
        out.append(dict(text=" ".join(ws).capitalize() + rnd.choice(["", ".", "!"]),
                        district=rnd.choice(districts), crop=rnd.choice(crops)))
    return out


def best(fn, *a, repeat=3):
    r = []
    for _ in range(repeat):
        t = time.perf_counter(); fn(*a); r.append(time.perf_counter() - t)
    return min(r)


if __name__ == "__main__":
    print("=== Program from the question ===")
    print(top(frequencies(calls, STOP), 3))
    print("all counts:", frequencies(calls, STOP))
    print("Why does 'price' come before 'received'? Both have count 2, so the sort key (-count, word) falls back to the word:"
          " 'price' < 'received' alphabetically ('p' comes before 'r').")
    print("same result with setdefault:", frequencies_setdefault(calls, STOP) == frequencies(calls, STOP),
          "| with Counter:", dict(frequencies_counter(calls, STOP)) == frequencies(calls, STOP),
          "| with list.count:", frequencies_listcount(calls, STOP) == frequencies(calls, STOP))

    print("\n=== Grouping (dictionary of lists) ===")
    sample = [dict(text="Seeds delayed", district="Madurai", crop="paddy"),
              dict(text="Pump damaged", district="Salem", crop="cotton"),
              dict(text="Loan rejected", district="Madurai", crop="cotton")]
    by_district, by_crop = group_by(sample, "district"), group_by(sample, "crop")
    print("complaints per district:", {k: len(v) for k, v in by_district.items()})
    print("by district:", by_district)
    print("by crop    :", by_crop)

    print("\n=== Tests: empty text, case and punctuation ===")
    print("empty list of complaints        ->", frequencies([], STOP))
    print("empty string                    ->", frequencies([""], STOP))
    print("only stop words                 ->", frequencies(["Not HIGH, not high!"], STOP))
    print("'Seeds, SEEDS! seeds.'          ->", frequencies(["Seeds, SEEDS! seeds."], STOP))
    print("top(k=0), top(k larger than d)  ->", top({"a": 1}, 0), top({"a": 1}, 5))
    print("ties sorted alphabetically      ->", top({"b": 2, "a": 2, "c": 2, "d": 3}, 4))

    print("\n=== Order of keys (Python 3.7+): insertion order is guaranteed ===")
    d = {}
    for k in ("seeds", "price", "loan"):
        d[k] = len(k)
    print("inserted seeds, price, loan ->", list(d))
    del d["price"]
    d["price"] = 5
    print("delete 'price' and insert it again -> it moves to the end:", list(d))
    print("two dicts with the same items in a different order are equal:", {"a": 1, "b": 2} == {"b": 2, "a": 1})

    print("\n=== key, value and item views ===")
    d = {"paddy": 3, "cotton": 5}
    kv, vv, iv = d.keys(), d.values(), d.items()
    print("before:", kv, vv, iv)
    d["maize"] = 1
    print("after d['maize'] = 1 (the SAME view objects now show it):", list(kv), list(vv), list(iv))
    print("keys view supports set operations:", kv & {"paddy", "wheat"}, "| len:", len(kv), "| 'maize' in kv:", "maize" in kv)
    try:
        for k in d:
            d[k + "x"] = 0
    except RuntimeError as e:
        print("changing the dictionary while iterating over it -> RuntimeError:", e)

    print("\n=== Experiment: n complaints (about 5 words + 2 stop words each), vocabulary d = 500 ===")
    print(f"{'complaints':>10} {'words n':>9} {'distinct d':>10} | {'dict get':>9} {'setdefault':>10} {'Counter':>9} {'list.count':>11} | list.count / dict")
    rows = []
    for n in (1_000, 10_000, 100_000):
        recs = make_complaints(n)
        texts = [r["text"] for r in recs]
        ref = frequencies(texts, STOP_BIG)
        assert frequencies_setdefault(texts, STOP_BIG) == ref and dict(frequencies_counter(texts, STOP_BIG)) == ref
        assert frequencies_listcount(texts, STOP_BIG) == ref
        t1, t2 = best(frequencies, texts, STOP_BIG), best(frequencies_setdefault, texts, STOP_BIG)
        t3, t4 = best(frequencies_counter, texts, STOP_BIG), best(frequencies_listcount, texts, STOP_BIG)
        nwords = sum(ref.values())
        rows.append(dict(complaints=n, words=nwords, distinct=len(ref), get=t1, setdefault=t2, counter=t3, listcount=t4))
        print(f"{n:>10,} {nwords:>9,} {len(ref):>10} | {t1:>9.4f} {t2:>10.4f} {t3:>9.4f} {t4:>11.4f} | {t4 / t1:>8.1f}x")
    res["rows"] = rows

    print("\n=== Counting step only (words already split into a list, so tokenising cost is excluded) ===")
    print(f"{'words n':>9} | {'dict loop get':>13} {'Counter(words)':>15} {'list.count':>11}")
    crows = []
    for n in (1_000, 10_000, 100_000):
        words = [w for r in make_complaints(n) for w in words_of(r["text"]) if w not in STOP_BIG]

        def loop(ws):
            c = {}
            for w in ws:
                c[w] = c.get(w, 0) + 1
            return c
        t1, t2 = best(loop, words), best(Counter, words)
        t3 = best(lambda ws: {w: ws.count(w) for w in set(ws)}, words, repeat=1 if n == 100_000 else 3)
        crows.append(dict(words=len(words), loop=t1, counter=t2, listcount=t3))
        print(f"{len(words):>9,} | {t1:>13.5f} {t2:>15.5f} {t3:>11.4f}")
    res["crows"] = crows

    print("\n=== Effect of d: 10,000 complaints with vocabulary 100, 500, 2000, 5000 ===")
    drows = []
    for v in (100, 500, 2000, 5000):
        texts = [r["text"] for r in make_complaints(10_000, vocab=v)]
        t1, t4 = best(frequencies, texts, STOP_BIG), best(frequencies_listcount, texts, STOP_BIG, repeat=1)
        d_ = len(frequencies(texts, STOP_BIG))
        drows.append(dict(vocab=v, distinct=d_, get=t1, listcount=t4))
        print(f"vocabulary {v:>5}: distinct words in data d = {d_:>5} | dict loop {t1:.4f} s | list.count {t4:.4f} s")
    res["drows"] = drows
    json.dump(res, open("results.json", "w"), indent=1)

    top5 = top(frequencies([r["text"] for r in make_complaints(100_000)], STOP_BIG), 5)
    print("\ntop 5 words in 100,000 generated complaints:", top5)
