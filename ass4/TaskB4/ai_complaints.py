"""B4.1 - Sentiment scorer and summariser on 54 complaints (agreement with my own reading) + comparison with a trained model."""
import json
import os
import pickle
import random
import re
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import sentiment
from complaints_data import COMPLAINTS

res = {}
STOP = set("a an the is are was were be been it its this that these those of to in on at for from by with and or but not no i we you they he she "
           "my our your their me us please very so also as have has had will can could would should do does did there here near after before".split())


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def words_of(s):
    return [w for w in re.findall(r"[a-z0-9']+", s.lower()) if w not in STOP]


def summarise(text, k=1):
    """Extractive: score each sentence by the sum of the frequencies (inside the complaint) of its important words, keep the k best, original order."""
    sents = sentences(text)
    freq = Counter(w for s in sents for w in words_of(s))
    scores = [sum(freq[w] for w in words_of(s)) for s in sents]
    best = sorted(range(len(sents)), key=lambda i: (-scores[i], i))[:k]
    return [sents[i] for i in sorted(best)], sorted(best)


def first_k(text, k=1):
    s = sentences(text)
    return s[:k], list(range(min(k, len(s))))


print("=== B4.1 Sentiment scorer: agreement with my own reading of 54 complaints ===")
labels = ["negative", "neutral", "positive"]
conf = {(h, p): 0 for h in labels for p in labels}
wrong = []
for text, human, key in COMPLAINTS:
    got = sentiment.label(text)
    conf[(human, got)] += 1
    if got != human:
        wrong.append((text, human, got, sentiment.score(text)))
agree = len(COMPLAINTS) - len(wrong)
print(f"complaints: {len(COMPLAINTS)} (negative {sum(c[1] == 'negative' for c in COMPLAINTS)}, positive {sum(c[1] == 'positive' for c in COMPLAINTS)}, neutral {sum(c[1] == 'neutral' for c in COMPLAINTS)})")
print(f"labels in agreement with my reading: {agree} of {len(COMPLAINTS)} = {agree / len(COMPLAINTS) * 100:.1f} %")
print("\nconfusion table (rows = my reading, columns = scorer):")
print(f"{'':10}" + "".join(f"{p:>10}" for p in labels))
for h in labels:
    print(f"{h:10}" + "".join(f"{conf[(h, p)]:>10}" for p in labels))
print("\nrecall per class:", {h: f"{conf[(h, h)] / sum(conf[(h, p)] for p in labels) * 100:.0f} %" for h in labels})
print("\nComplaints labelled wrongly (first 8):")
for t, h, g, s in wrong[:8]:
    print(f"  mine {h:8} scorer {g:8} (score {s:+d}) | {t[:90]}")
res["sentiment"] = dict(n=len(COMPLAINTS), agree=agree, conf={f"{h}|{p}": v for (h, p), v in conf.items()}, wrong=[(t, h, g) for t, h, g, s in wrong])

print("\n=== Summariser: sentence with the most frequent important words, against the first sentence (k = 1) ===")
hit_freq = sum(summarise(t)[1][0] == key for t, _, key in COMPLAINTS)
hit_first = sum(first_k(t)[1][0] == key for t, _, key in COMPLAINTS)
not_first = [c for c in COMPLAINTS if c[2] != 0]
hit_freq_nf = sum(summarise(t)[1][0] == key for t, _, key in not_first)
print(f"key sentence = the sentence that states the main point (my reading); complaints where it is NOT the first sentence: {len(not_first)} of {len(COMPLAINTS)}")
print(f"frequency summariser picks my key sentence: {hit_freq} of {len(COMPLAINTS)} ({hit_freq / len(COMPLAINTS) * 100:.0f} %); first-sentence summariser: {hit_first} of {len(COMPLAINTS)} ({hit_first / len(COMPLAINTS) * 100:.0f} %)")
print(f"... on the {len(not_first)} complaints whose key sentence is not the first: frequency {hit_freq_nf}, first-sentence 0")
for t, h, key in COMPLAINTS[:3] + [c for c in COMPLAINTS if c[2] == 1][:2]:
    print(f"  complaint : {t}\n  frequency : {summarise(t)[0][0]}\n  first     : {first_k(t)[0][0]}\n  my key    : {sentences(t)[key]}")
res["summary"] = dict(freq_hits=hit_freq, first_hits=hit_first, n=len(COMPLAINTS), not_first=len(not_first), freq_hits_not_first=hit_freq_nf)

print("\n=== Time per complaint (microseconds) and for 50,000 complaints a month ===")
texts = [c[0] for c in COMPLAINTS]


def per_item(fn, reps=300):
    t = time.perf_counter()
    for _ in range(reps):
        for x in texts:
            fn(x)
    return (time.perf_counter() - t) / (reps * len(texts)) * 1e6


t_score, t_sum, t_first = per_item(sentiment.score), per_item(summarise), per_item(first_k)
print(f"lexicon scorer {t_score:.1f} us | frequency summariser {t_sum:.1f} us | first-sentence summariser {t_first:.1f} us")
print(f"50,000 complaints a month: scorer {t_score * 50_000 / 1e6:.2f} s, scorer + summariser {(t_score + t_sum) * 50_000 / 1e6:.2f} s")
res["time"] = dict(score_us=t_score, summarise_us=t_sum, first_us=t_first)

print("\n=== Alternative concept: a trained model (Naive Bayes, scikit-learn) ===")
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
rnd = random.Random(12)
POS = "good clean fast helpful improved great excellent nice happy quick polite useful satisfied easy fresh peaceful comfortable solved regular thanks".split()
NEG = "bad dirty slow rude smoke broken terrible awful stench dust fumes wrong useless angry unsafe delayed worst ignored stinks polluted".split()
NEU = "where when how what share report office hours register forecast contact available information explain date meeting".split()
TOP = "bus road air water app helpline staff officer park market metro garbage sensor station school hospital factory street".split()
FILL = "is was the near our this and very now today again".split()


def make_sentence(cls):
    pool = {"positive": POS, "negative": NEG, "neutral": NEU}[cls]
    ws = [rnd.choice(TOP) for _ in range(rnd.randint(1, 2))] + [rnd.choice(pool) for _ in range(rnd.randint(1, 2))] + [rnd.choice(FILL) for _ in range(2)]
    if rnd.random() < 0.15 and cls != "neutral":                                # noise: a word of the other class
        ws.append(rnd.choice(NEG if cls == "positive" else POS))
    rnd.shuffle(ws)
    return " ".join(ws) + "."


train = []
for _ in range(3000):
    cls = rnd.choice(["positive", "negative", "neutral"])
    train.append((" ".join(make_sentence(cls) for _ in range(rnd.randint(1, 3))), cls))
vec = CountVectorizer()
X = vec.fit_transform([t for t, _ in train])
nb = MultinomialNB().fit(X, [c for _, c in train])
pred = nb.predict(vec.transform(texts))
acc_nb = sum(p == c[1] for p, c in zip(pred, COMPLAINTS))
t0 = time.perf_counter()
for _ in range(20):
    for x in texts:
        nb.predict(vec.transform([x]))
t_nb_single = (time.perf_counter() - t0) / (20 * len(texts)) * 1e6
big = [train[i % len(train)][0] for i in range(50_000)]
t0 = time.perf_counter(); nb.predict(vec.transform(big)); t_nb_batch = time.perf_counter() - t0
size_model = len(pickle.dumps((vec, nb)))
size_lex = len(pickle.dumps((sentiment.POSITIVE, sentiment.NEGATIVE, sentiment.NEGATORS)))
print(f"trained on 3,000 synthetic labelled complaints (vocabulary {len(vec.vocabulary_)} words); tested on my 54 complaints")
print(f"agreement with my reading: Naive Bayes {acc_nb} of 54 ({acc_nb / 54 * 100:.1f} %), lexicon {agree} of 54 ({agree / 54 * 100:.1f} %)")
print(f"time per complaint: Naive Bayes one at a time {t_nb_single:.0f} us, in one batch of 50,000: {t_nb_batch / 50_000 * 1e6:.1f} us per complaint ({t_nb_batch:.2f} s total); lexicon {t_score:.1f} us")
print(f"memory of the model (pickled): {size_model / 1e3:.1f} KB; word lists: {size_lex / 1e3:.2f} KB")
print("note: the training data are synthetic (written by me from word lists), so this accuracy is optimistic; a real model needs thousands of real labelled complaints.")
res["nb"] = dict(acc=acc_nb, t_single_us=t_nb_single, t_batch_us=t_nb_batch / 50_000 * 1e6, model_kb=size_model / 1e3, lex_kb=size_lex / 1e3, vocab=len(vec.vocabulary_))
json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
