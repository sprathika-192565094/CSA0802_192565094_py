"""Q7 - Design a contact-merging program from first principles.

Input : contacts from several sources, each {"name": str, "phones": [str], "emails": [str], "source": str}
Output: merged contacts, each person once, with all names, normalised numbers and e-mails (sets).
"""
import json
import random
import time
import tracemalloc

res = {}
TITLES = {"dr", "mr", "mrs", "ms", "shri", "smt", "prof", "sri"}
PUNCT = ".,;:-_()'\""


# =============================================================== normalisation
def norm_number(raw):
    """Keep only digits; numbers with 10 or more digits are compared by their LAST 10 digits
    (removes +91, 0091, 0 trunk prefix, spaces, dashes). Shorter numbers are kept as they are."""
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) < 5:                      # nothing usable
        return ""
    return digits[-10:] if len(digits) >= 10 else digits


def norm_name(raw):
    """'Dr. Ravi' -> 'ravi', ' Ravi  KUMAR ' -> 'ravi kumar'."""
    cleaned = "".join(" " if ch in PUNCT else ch for ch in raw.lower())
    return " ".join(w for w in cleaned.split() if w not in TITLES)


def norm_email(raw):
    return raw.strip().lower()


# =============================================================== merge with a dictionary keyed by the normalised number
class DisjointSet:
    """Union-find over contact indices: needed because one contact can connect two groups (transitive merging)."""

    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def merge_contacts(contacts):
    """Returns (merged contacts, review list).  O(total numbers) dictionary operations on average."""
    n = len(contacts)
    ds = DisjointSet(n)
    owner = {}                                              # normalised number -> first contact index having it
    clean = []
    for i, c in enumerate(contacts):
        nums = {x for x in (norm_number(p) for p in c.get("phones", [])) if x}
        mails = {norm_email(e) for e in c.get("emails", []) if e.strip()}
        name = norm_name(c.get("name", "") or "")
        clean.append((nums, mails, name))
        for num in nums:
            if num in owner:
                ds.union(i, owner[num])
            else:
                owner[num] = i
    # contacts with NO number are attached through an e-mail address shared with another contact
    mail_owner = {}
    for i, (nums, mails, name) in enumerate(clean):
        for m in mails:
            mail_owner.setdefault(m, i)
    for i, (nums, mails, name) in enumerate(clean):
        if not nums:
            for m in mails:
                if mail_owner[m] != i:
                    ds.union(i, mail_owner[m])
                    break
    groups = {}
    for i in range(n):
        g = groups.setdefault(ds.find(i), {"names": set(), "numbers": set(), "emails": set(), "members": []})
        nums, mails, name = clean[i]
        g["numbers"] |= nums
        g["emails"] |= mails
        if name:
            g["names"].add(name)
        g["members"].append(i)
    merged, review = [], []
    for root in sorted(groups):
        g = groups[root]
        g["display"] = max(g["names"], key=lambda s: (len(s.split()), len(s)), default="(no name)")
        # same number but names that share no word at all -> different people may have been merged: flag for a human
        words = [set(nm.split()) for nm in g["names"]]
        if len(words) > 1 and not set.intersection(*words):
            review.append(g["display"])
        merged.append(g)
    return merged, review


# =============================================================== alternative: compare every pair
def merge_pairwise(contacts):
    n = len(contacts)
    sets = [{x for x in (norm_number(p) for p in c.get("phones", [])) if x} for c in contacts]
    ds = DisjointSet(n)
    comparisons = 0
    for i in range(n):
        for j in range(i + 1, n):
            comparisons += 1
            if sets[i] & sets[j]:
                ds.union(i, j)
    return len({ds.find(i) for i in range(n)}), comparisons


def show(g):
    return f"{g['display']!r:16} names={sorted(g['names'])} numbers={sorted(g['numbers'])} emails={sorted(g['emails'])} from contacts {[m + 1 for m in g['members']]}"


# =============================================================== synthetic data with known truth
def make_contacts(n, seed=4):
    rnd = random.Random(seed)
    n_people = max(1, n // 3)
    pool = rnd.sample(range(6_000_000_000, 9_999_999_999), n_people * 2)
    first = ["Ravi", "Anita", "Mohan", "Lakshmi", "Kumar", "Priya", "Suresh", "Divya", "Arun", "Meena"]
    last = ["Kumar", "Sharma", "Raj", "Iyer", "Nair", "Reddy", "Das", "Pillai", "Rao", "Menon"]
    people = [dict(primary=pool[2 * i], secondary=pool[2 * i + 1], name=(rnd.choice(first), rnd.choice(last))) for i in range(n_people)]

    def fmt(num):
        s = str(num)
        return rnd.choice([s, "+91 " + s[:5] + " " + s[5:], "0" + s, "+91-" + s, "(0" + s[:3] + ") " + s[3:], "0091" + s])
    contacts, truth = [], []
    i = 0
    while len(contacts) < n:
        p = i % n_people if i < n_people else rnd.randrange(n_people)     # every person appears at least once
        i += 1
        pe = people[p]
        phones = [fmt(pe["primary"])] + ([fmt(pe["secondary"])] if rnd.random() < 0.3 else [])
        name = rnd.choice([pe["name"][0], f"{pe['name'][0]} {pe['name'][1]}", f"Dr. {pe['name'][0]}", f"{pe['name'][0].lower()} {pe['name'][1].lower()}"])
        contacts.append(dict(name=name, phones=phones, emails=[f"p{p}@mail.com"] if rnd.random() < 0.4 else [], source=rnd.choice(["phone1", "phone2", "sim"])))
        truth.append(p)
    return contacts, truth


def best(fn, *a, repeat=3):
    r = []
    for _ in range(repeat):
        t = time.perf_counter(); out = fn(*a); r.append(time.perf_counter() - t)
    return min(r), out


if __name__ == "__main__":
    print("=== Normalisation tests ===")
    for raw in ("+91 98400 12345", "9840012345", "098400-12345", "0091 98400 12345", "(044) 2345 6789", "12", ""):
        print(f"  number {raw!r:22} -> {norm_number(raw)!r}")
    for raw in ("Dr. Ravi", "ravi kumar", "  RAVI   Kumar ", "Mrs. Anita S.", ""):
        print(f"  name   {raw!r:22} -> {norm_name(raw)!r}")

    print("\n=== Test with duplicates, missing fields and different formats (small list, merged by hand first) ===")
    small = [
        dict(name="Dr. Ravi", phones=["+91 98400 12345"], emails=[], source="phone1"),                       # 1
        dict(name="ravi kumar", phones=["9840012345", "044-2345 6789"], emails=["ravi@x.com"], source="phone2"),  # 2
        dict(name="Ravi Kumar", phones=[], emails=["RAVI@x.com"], source="sim"),                              # 3 (no number)
        dict(name="Anita", phones=["+91 90000 11111"], emails=["anita@y.com"], source="phone1"),             # 4
        dict(name="anita s", phones=["090000 11111"], emails=[], source="sim"),                               # 5
        dict(name="Mohan", phones=["98765 43210"], emails=[], source="phone1"),                               # 6
        dict(name="Mohan", phones=["91234 56789"], emails=[], source="phone2"),                               # 7 (different person, same name)
        dict(name="", phones=["+91-98765-43210"], emails=[], source="sim"),                                   # 8 (no name)
        dict(name="Lakshmi", phones=[], emails=[], source="sim"),                                             # 9 (nothing to match on)
        dict(name="Dr. Ravi", phones=["+91 98400 12345"], emails=["ravi.k@work.com"], source="sim"),         # 10
    ]
    print("HAND RESULT (expected): 5 people -> {1,2,3,10} Ravi, {4,5} Anita, {6,8} Mohan, {7} Mohan, {9} Lakshmi")
    merged, review = merge_contacts(small)
    print(f"PROGRAM RESULT: {len(merged)} people")
    for g in merged:
        print("  ", show(g))
    expected = [[0, 1, 2, 9], [3, 4], [5, 7], [6], [8]]
    ok_small = [g["members"] for g in merged] == expected
    print("program equals the hand result:", ok_small)
    print("groups flagged for review (same number, no common word in the names):", review)
    all_in = {n for c in small for n in (norm_number(p) for p in c["phones"]) if n}
    all_out = set().union(*(g["numbers"] for g in merged))
    mails_in = {norm_email(e) for c in small for e in c["emails"]}
    mails_out = set().union(*(g["emails"] for g in merged))
    print("no number lost:", all_in == all_out, "| no e-mail lost:", mails_in == mails_out)
    again, _ = merge_contacts([dict(name=g["display"], phones=sorted(g["numbers"]), emails=sorted(g["emails"])) for g in merged])
    print("merging the result again changes nothing (idempotent):", len(again) == len(merged))
    res.update(small_ok=ok_small, small_people=len(merged))

    print("\n=== Transitive merge: a contact with two numbers links two groups ===")
    trio = [dict(name="A", phones=["9000000001"]), dict(name="B", phones=["9000000002"]), dict(name="A B", phones=["9000000001", "9000000002"])]
    print("3 contacts ->", len(merge_contacts(trio)[0]), "person (a dictionary keyed only by the first number would give 2)")

    print("\n=== Different people, same name, shared number (limitation) ===")
    clash = [dict(name="Ravi", phones=["044 2345 6789"]), dict(name="Sundar", phones=["044 2345 6789"])]
    m, rv = merge_contacts(clash)
    print("two people sharing an office landline ->", len(m), "merged contact(s); flagged for review:", rv)

    print("\n=== Measurements (best of 3) with verification against the known truth ===")
    print(f"{'contacts':>9} {'people':>7} | {'dictionary design':>18} {'merged':>7} {'correct':>8} | {'memory (tracemalloc)':>22}")
    rows = []
    for n in (1_000, 100_000):
        contacts, truth = make_contacts(n)
        t, (merged, review) = best(merge_contacts, contacts)
        # truth check: every merged group contains exactly one true person and every true person is in exactly one group
        correct = all(len({truth[m] for m in g["members"]}) == 1 for g in merged) and len(merged) == len(set(truth))
        tracemalloc.start(); merge_contacts(contacts); mem = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
        rows.append(dict(n=n, people=len(set(truth)), time=t, merged=len(merged), correct=correct, mem=mem))
        print(f"{n:>9,} {len(set(truth)):>7,} | {t:>16.4f} s {len(merged):>7,} {str(correct):>8} | {mem / 1e6:>19.1f} MB")
    res["rows"] = rows

    print("\n=== Alternative concept: compare every pair of contacts ===")
    print(f"{'contacts':>9} | {'pairs n(n-1)/2':>15} {'pairwise time':>14} {'dictionary time':>16} | same number of people")
    prow = []
    for n in (1_000, 2_000, 4_000):
        contacts, _ = make_contacts(n)
        tp, (cnt, comps) = best(merge_pairwise, contacts, repeat=1)
        td, (mg, _) = best(merge_contacts, contacts)
        prow.append(dict(n=n, pairs=comps, pairwise=tp, dictionary=td, same=cnt == len(mg)))
        print(f"{n:>9,} | {comps:>15,} {tp:>13.3f}s {td:>15.4f}s | {cnt == len(mg)}")
    scale = (100_000 / 4_000) ** 2
    est = prow[-1]["pairwise"] * scale
    dict_100k = rows[1]["time"]
    print(f"Extrapolation to 100,000 contacts (time grows with n^2: x{scale:.0f} from n = 4,000): about {est:,.0f} s = {est / 60:.1f} minutes "
          f"for {100_000 * 99_999 // 2:,} pairs; the dictionary design needed {dict_100k:.2f} s (about {est / dict_100k:,.0f} times faster).")
    res["pairs"] = prow
    res["extrapolated_100k_s"] = est
    json.dump(res, open("results.json", "w"), indent=1)
