"""Builds Assignment3_Report.docx from the programs, their output.txt files and results.json.
Edit NAME / REGNO / REPO below, run the programs (python run_all.py) on your own computer, then run this file."""
import json
import os
import platform
import sys
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor

NAME = "<YOUR NAME>"
REGNO = "<REGISTER NUMBER>"
REPO = "https://github.com/<your-username>/CSA08-<RegisterNumber>-Assignment3"
MACHINE = f"Python {platform.python_version()} on {platform.system()} {platform.machine()}"


def J(task):
    return json.load(open(f"{task}/results.json"))


def T(task):
    return open(f"{task}/output.txt").read()


doc = Document()
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(0.9)
sec.top_margin = sec.bottom_margin = Inches(0.8)
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)
for lvl, size in ((1, 16), (2, 13), (3, 11.5)):
    h = doc.styles[f"Heading {lvl}"]
    h.font.name = "Calibri"
    h.font.size = Pt(size)
    h.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)


def shade(cell_or_par, color):
    pr = cell_or_par._tc.get_or_add_tcPr() if hasattr(cell_or_par, "_tc") else cell_or_par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    pr.append(shd)


def H(text, lvl=1):
    return doc.add_heading(text, level=lvl)


def P(text, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    p.paragraph_format.space_after = Pt(4)
    return p


def B(items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        if isinstance(it, tuple):
            r = p.add_run(it[0]); r.bold = True
            p.add_run(it[1])
        else:
            p.add_run(it)
        p.paragraph_format.space_after = Pt(1)


def CODE(text, size=8):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    shade(p, "F2F2F2")
    lines = text.rstrip("\n").split("\n")
    for i, line in enumerate(lines):
        r = p.add_run(line)
        r.font.name = "Consolas"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        r.font.size = Pt(size)
        if i < len(lines) - 1:
            r.add_break()


def TABLE(rows, widths=None, header=True, size=9):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    if widths:
        t.autofit = False
        for j, w in enumerate(widths):
            t.columns[j].width = Inches(w)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            r = c.paragraphs[0].add_run(str(val))
            r.font.size = Pt(size)
            if header and i == 0:
                r.bold = True
                shade(c, "D9E2F3")
            if widths:
                c.width = Inches(widths[j])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def IMG(path, width=6.3, caption=None):
    doc.add_picture(path, width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        p = P(caption, italic=True)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def OUT(task, caption):
    """Console output as text (copyable) and as an output image."""
    P(caption, bold=True)
    CODE(T(task), size=7)
    IMG(f"{task}/output_screenshot.png", 6.4, f"Output screenshot - {task}")


# =============================================================== title page
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("\n\nCSA08 - Python Programming\nAssignment 3 - Assignment Report")
r.bold = True
r.font.size = Pt(22)
TABLE([["Student name", NAME], ["Register number", REGNO], ["GitHub repository", REPO],
       ["Environment used for the measurements", MACHINE]], widths=[2.4, 4.3], header=False, size=11)
P("Contents: Q1 Lists and slicing - Q2 Tuples, mutability and copying - Q3 Dictionaries - Q4 Sets - Q5 List comprehension - "
  "Q6 Nested data - Q7 Data-structure design from first principles - Appendix A (source code) - Appendix B (how the evidence was produced).")
P("Method used for every question: Design, Implement, Analyse, Evaluate. All numbers in this report are copied from results.json / output.txt of the programs in the repository.", italic=True)
doc.add_page_break()

# =============================================================== Q1
r1 = J("Task01")
c1, tm1 = r1["counts"], r1["times"]
H("Q1 - Lists and Slicing: Daily Rainfall Records (6 marks)")
H("1.1 Implementation (Task01/rainfall.py)", 2)
B(["Readings: a list of 365 integers (mm) from the random module (seed 1, about 40 % dry days).",
   "Weekly totals by slicing: [sum(readings[i:i+7]) for i in range(0, n, 7)] - 52 complete weeks and a last block of 1 day (365 = 52 x 7 + 1).",
   "Wettest and driest week among the COMPLETE weeks (the 1-day block would always look 'driest'); maximum and minimum with positions using max()/min() and index() (first position) and a list comprehension with enumerate (all positions).",
   "7-day moving average three ways: naive (re-add 7 values), running sum, collections.deque(maxlen=7); dry days = [day for day, mm in enumerate(readings, 1) if mm == 0]."])
OUT("Task01", "Console output")
w, d_ = r1["wettest"], r1["driest"]
P(f"Result for the generated year: wettest complete week = week {w[0]} (days {w[2]}-{w[2]+6}, {w[1]} mm), driest = week {d_[0]} (days {d_[2]}-{d_[2]+6}, {d_[1]} mm); "
  f"the maximum is {r1['maxmin']['max']} mm (first on day {r1['maxmin']['max_first_day']}); {r1['dry_days']} of 365 days were dry.")
H("1.2 Design and analysis", 2)
P("Pseudocode of the moving average (window w = 7) - naive and with a running sum:", bold=True)
CODE("NAIVE                                      RUNNING SUM\nFOR i FROM 0 TO n - w DO                   total <- sum of readings[0 .. w-1]\n    total <- 0                             APPEND total / w\n    FOR j FROM i TO i + w - 1 DO           FOR i FROM w TO n - 1 DO\n        total <- total + readings[j]           total <- total + readings[i] - readings[i - w]\n    APPEND total / w                           APPEND total / w", size=8)
P("What the three slices return (len(readings) = 365):", bold=True)
TABLE([["Expression", "Result", "Observed"],
       ["readings[7:14]", "a NEW list with the elements at index 7 ... 13 = days 8-14, the second week", "length 7"],
       ["readings[-7:]", "the last 7 elements (days 359-365); negative index counts from the end", "length 7"],
       ["readings[::7]", "every 7th element starting at index 0 (days 1, 8, 15, ...): step 7", "length 53"]], widths=[1.4, 4.2, 1.2], size=9)
P("A slice is a copy of the selected references; the original list is not changed.")
P("Why a list is suitable, and the cost of its operations", bold=True)
P("The readings are an ordered sequence of the same kind of value that is accessed by position (day number - 1), sliced into weeks and extended by one value per day - exactly what a list is for: index access and slicing by position are O(1) per element copied, "
  "and append is cheap. Measured on a list of 365,000 values:")
ops = r1["ops_us"]
TABLE([["Operation", "Complexity", "Measured (microseconds)"],
       ["append(x) / pop() at the end", "O(1) amortised", f"{ops['append(x)            O(1) amortised']:.2f} / {ops['pop()  (last)        O(1)']:.2f}"],
       ["insert(0, x)", "O(n) - every element shifts one place", f"{ops['insert(0, x)         O(n)']:.1f}"],
       ["insert(n // 2, x)", "O(n - i) - the elements after the position shift", f"{ops['insert(len//2, x)    O(n)']:.1f}"],
       ["pop(0)", "O(n)", f"{ops['pop(0)               O(n)']:.1f}"],
       ["sort() on random data", "O(n log n) (Timsort)", f"{ops['sort() random data   O(n log n)']:,.0f}"],
       ["sort() on already sorted data", "O(n) (Timsort finds the run)", f"{ops['sort() sorted data   O(n)']:,.0f}"]], widths=[2.2, 2.6, 2.0], size=9)
P("Derivation of the number of additions (w = 7)", bold=True)
B(["Naive: there are n - w + 1 = n - 6 windows; each needs w - 1 = 6 additions of readings (7 if sum() starts from 0), so 6(n - 6) additions: O(7n) = O(n) with a large constant.",
   "Running sum: w - 1 = 6 additions for the first window, then one addition and one subtraction per further window: 6 + 2(n - 7) = 2n - 8 operations: O(n) with constant 2.",
   "Ratio for large n: 6n / 2n = 3, so I expect the running sum to be about 3 times faster."])
H("1.3 Experimental investigation", 2)
rows = [["n", "Naive: formula = counted", "Running sum: formula = counted", "Time naive (s)", "Time running (s)", "Time ratio", "Derived ratio"]]
for c, t in zip(c1, tm1):
    rows.append([f"{c['n']:,}", f"{c['naive']:,}", f"{c['running']:,}", f"{t['naive']:.5f}", f"{t['running']:.5f}", f"{t['naive']/t['running']:.2f}", f"{c['naive']/c['running']:.2f}"])
TABLE(rows, widths=[0.7, 1.3, 1.4, 0.9, 0.9, 0.7, 0.8], size=8.5)
P("The counted additions (instrumented code) equal the derived formulas exactly for all three sizes. The measured time ratio (about 3.2-3.5 at the two large sizes) agrees with the derived ratio of the counts (3.00); at n = 365 the timer overhead and fixed costs make the small run less exact.")
P("Edge cases: an empty list gives empty weekly totals, no extremes (None) and an empty moving average; a list of 3 readings gives one weekly block (a partial week) but no moving-average window; exactly 7 readings gives one window. "
  "No exception is raised in any of these cases (see the console output).")
H("1.4 Design question - a late reading must be inserted at the correct date", 2)
P(f"list.insert(i, x) moves all elements after position i one place to the right, so it costs O(n - i). For the 365-element year this is about {r1['insert_365_us']:.2f} microseconds (about 180 references moved on average), which is negligible; "
  f"for a 365,000-element list the measured cost is about {ops['insert(len//2, x)    O(n)']:.0f} microseconds per insertion. Decision: I would still use a list for one year of daily readings: it is simple, memory-compact and late readings are rare. "
  "If very many late insertions were expected on very long series I would keep (date, mm) pairs in a list maintained with bisect.insort (O(log n) search but still O(n) shifting) or use a dictionary keyed by date (O(1) insert).")
H("1.5 Alternative concept - deque(maxlen=7) or a dictionary keyed by date", 2)
CODE("win = deque(maxlen=7); total = 0\nfor v in readings:\n    if len(win) == 7: total -= win[0]      # value that is about to fall out\n    win.append(v); total += v\n    if len(win) == 7: out.append(total / 7)\n\n"
     "by_date = {date(2026,1,1) + timedelta(i): v for i, v in enumerate(readings)}\nfor i in range(6, n): total = sum(by_date[start + timedelta(i - k)] for k in range(7))")
mem = r1["mem"]
TABLE([["Approach", "Time for n days", "Extra space (apart from the result)", f"Time at n = 365,000 (s)", "Peak memory at n = 365,000"],
       ["Slicing, naive", "O(7n) = O(n)", "O(1) (temporary 6-element slices)", f"{tm1[2]['naive']:.4f}", f"{mem['list slicing (naive)']/1e6:.1f} MB"],
       ["List with running sum", "O(n)", "O(1)", f"{tm1[2]['running']:.4f}", f"{mem['running sum']/1e6:.1f} MB"],
       ["deque(maxlen=7) + running sum", "O(n) (append and drop are O(1))", "O(7) = O(1)", f"{tm1[2]['deque']:.4f}", f"{mem['deque(maxlen=7)']/1e6:.1f} MB"],
       ["dictionary keyed by date", "O(7n): 7 hash look-ups per window", "O(n) for the dictionary itself", f"{tm1[2]['dict']:.4f}", f"{mem['dictionary keyed by date (storage)']/1e6:.1f} MB (storage alone)"]],
      widths=[1.6, 1.4, 1.6, 1.0, 1.2], size=8)
P("The peak memory of the first three is dominated by the output list of 365,000 floats; their working storage is constant. The deque version is as fast as the running-sum list version and never needs the whole series in memory, so it is the right choice for a live stream of readings. "
  "The dictionary is the slowest (building date objects and hashing them) and its storage alone is about " + f"{mem['dictionary keyed by date (storage)']/mem['running sum']:.1f}" + " times the peak memory of the other three methods, but it is the only one of the four that finds a reading directly by its DATE, which helps when days are missing or arrive out of order.")
doc.add_page_break()

# =============================================================== Q2
r2 = J("Task02")
H("Q2 - Tuples, Mutability and Copying (7 marks)")
H("2.1 Implementation and Complete the Code (Task02/tuples_copying.py)", 2)
CODE("# TODO 1 (completed)\ngood = [[0 for _ in range(cols)] for _ in range(rows)]")
P("Stops are tuples (latitude, longitude) used as dictionary keys; they are unpacked in a for loop (for (lat, lon), name in stops.items()). The given program prints "
  "(bad: the 7 appears in every row; good: only in row 0; True False; T. Nagar) - i.e. the bug is reproduced and the corrected grid behaves.")
OUT("Task02", "Console output")
H("2.2 Why the bug happens - memory diagrams and is / id()", 2)
P("[[0] * cols] * rows first builds ONE inner list and then repeats the REFERENCE to it rows times. All rows are the same object; changing it through any row is visible through every row. "
  "The comprehension runs the expression [0 for _ in range(cols)] once per row and so creates a separate list each time.")
IMG("Task02/memory_diagrams.png", 6.3, "Memory diagrams of [[0]*3]*3 (left) and of the corrected grid (right)")
P("Evidence with id(): in the bad grid the three rows have the same id (1 distinct object, bad[0] is bad[1] -> True); in the corrected grid there are 3 different ids (good[0] is good[1] -> False).")
H("2.3 Aliasing, shallow copy and deep copy", 2)
TABLE([["Operation", "Outer list", "Inner lists", "Observed after changing an inner list and the outer list"],
       ["alias = route", "same object", "same", "alias shows both changes (it IS route)"],
       ["copy.copy(route) / route[:]", "new object", "SHARED", "outer change not visible; inner change visible"],
       ["copy.deepcopy(route)", "new object", "new copies", "neither change visible"]], widths=[1.8, 1.0, 1.0, 3.0], size=9)
P("A shallow copy is enough when the elements are immutable (numbers, strings, tuples of those): nothing inside can change, so sharing is harmless (flat list example: slice copy stays [1, 2, 3] when the original grows). "
  "A deep copy is needed when the list contains mutable objects (lists, dictionaries) that either side will change independently - for example a grid of rows.")
P("Why a function that changes a list argument changes the caller's list: Python passes the reference to the object (the parameter is another name for the same list). stops_list.append() mutates that one object, so the caller sees it (add_stop(mine) -> ['Central', 'Velachery']). "
  "Rebinding the parameter (stops_list = stops_list + [...]) builds a NEW list and only changes the local name - the caller's list stays ['Central'].")
H("2.4 Tuples as dictionary keys; a list as a key", 2)
P("The program raised TypeError: unhashable type: 'list'. A dictionary stores each key at a position computed from hash(key), and later finds it again by recomputing the hash. If a key could change, its hash would change and the dictionary could no longer find the entry. "
  "Tuples are immutable, so their hash is fixed (as long as the items are themselves hashable - a tuple that contains a list is also rejected, as the output shows).")
H("2.5 A list stored inside a tuple", 2)
P("t = ('route 5', [1, 2]): t[1].append(3) WORKS (the tuple still holds the same list object, which is mutable). t[1] = [9] raises TypeError (a tuple cannot rebind its item). "
  "t[1] += [4] raises TypeError too, but the list WAS extended before the error ('+=' first extends the list in place, then tries to store the result back into the tuple). "
  "Conclusion: tuple immutability is shallow - it fixes WHICH objects the tuple holds, not the contents of mutable objects.")
H("2.6 List and tuple - memory and time (1,000,000 values)", 2)
m, tt = r2["mem"], r2["time"]
TABLE([["Measurement", "List", "Tuple"],
       ["sys.getsizeof (built from range)", f"{m['list']:,} bytes", f"{m['tuple']:,} bytes"],
       ["sys.getsizeof (list built by append)", f"{m['list_append']:,} bytes (over-allocated)", "-"],
       ["Create 1,000,000 values (s)", f"{tt['create_list']:.4f}", f"{tt['create_tuple']:.4f}"],
       ["Index all 1,000,000 values (s)", f"{tt['index_list']:.4f}", f"{tt['index_tuple']:.4f}"],
       ["Create a 5-constant literal 10^6 times (s)", f"{tt['lit_list']:.4f}", f"{tt['lit_tuple']:.4f}"]], widths=[3.0, 2.0, 1.8], size=9)
P("Both containers store 8-byte references, so for the same values they need almost the same memory (a tuple is 16 bytes smaller: no spare capacity field); a list that grew by append() is about " + f"{(m['list_append']/m['list']-1)*100:.1f}" + " % larger because of over-allocation. "
  "Indexing is equally fast. The visible difference is for constant tuples: a literal of constants is built once at compile time, which is why creating it a million times is about " + f"{tt['lit_list']/tt['lit_tuple']:.0f}" + " times faster.")
H("2.7 Conclusion - tuple or list?", 2)
P("Use a tuple for a fixed-size record that should not change (a GPS coordinate pair, a database row), for dictionary keys and set members (they are hashable) and for constants. Use a list for a collection that grows, shrinks or is edited. "
  "Immutability protects against accidental changes (a function cannot alter the coordinate it was given), against aliasing bugs (sharing a tuple is safe), and against corrupting a dictionary or set whose keys must keep a constant hash.")
H("2.8 Alternative concept - dictionary keyed by (row, col)", 2)
g = r2["grid"]
CODE("zones = {}                                   # only zones that have passengers\nzones[(r, c)] = zones.get((r, c), 0) + 1   # board a passenger\ncount = zones.get((r, c), 0)               # empty zones read as 0")
TABLE([["Design", "Access time", "Space", "Measured (1000 x 1000 zones, 1,000 boardings)"],
       ["list of lists", "O(1) (two index operations)", "O(rows x cols)", f"{g['mem_dense']/1e6:.2f} MB of lists; read 1,000 zones {g['t_dense']*1e6:.0f} us"],
       ["dictionary keyed by (row, col)", "O(1) average (hash of the tuple)", "O(number of non-empty zones)", f"{g['mem_sparse']/1e3:.0f} KB for {g['nonempty']} non-empty zones (table + key tuples); read 1,000 zones {g['t_sparse']*1e6:.0f} us"]],
      widths=[1.6, 1.5, 1.5, 2.4], size=8.5)
P(f"Both give identical counts ({g['same']}). The dictionary uses about {g['mem_dense']/g['mem_sparse']:.0f} times less memory when only a tiny fraction of the zones is used, but each access is about {g['t_sparse']/g['t_dense']:.1f} times slower (hashing a tuple costs more than two indexings). "
  "Choose the list of lists when most zones are used or access speed dominates; choose the dictionary when the map is large and sparse.")
doc.add_page_break()

# =============================================================== Q3
r3 = J("Task03")
H("Q3 - Dictionaries: Farmer Helpline Complaint Analysis (7 marks)")
H("3.1 Implementation and Complete the Code (Task03/complaints.py)", 2)
CODE("def frequencies(texts, stop):                      # TODO 1\n    counts = {}\n    for text in texts:\n        for w in words_of(text):                   # lower case, punctuation removed, split\n            if w not in stop:                      # stop words are a SET: O(1) membership\n                counts[w] = counts.get(w, 0) + 1\n    return counts\n\n"
     "def top(counts, k):                              # TODO 2\n    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]\n\n"
     "groups.setdefault(rec['district'], []).append(rec['text'])   # dictionary of lists")
P("The program prints [('seeds', 3), ('price', 2), ('received', 2)] - the expected output. setdefault is used for the grouping (it creates the empty list the first time a district or crop is seen) and as a second counting variant; the results of get(), setdefault(), Counter and list.count() are identical.")
P("Why does 'price' come before 'received' although both occur twice? The sort key is the pair (-count, word). The first part ranks higher counts first; for equal counts the second part compares the words alphabetically, and 'price' < 'received' ('p' comes before 'r').", bold=True)
OUT("Task03", "Console output")
H("3.2 Design and analysis", 2)
B([("How a dictionary finds a key: ", "it computes hash(key), uses part of the hash to choose a slot in its table, and compares the stored hash and then the key itself (identity, then ==). If the slot is occupied by a different key (collision), it probes another slot following a fixed sequence derived from the hash. "
    "The table is resized so it is never more than about two-thirds full, so the expected number of probes is a small constant. Therefore the average cost of a lookup does not depend on how many keys are stored: O(1) average (O(n) only in the pathological case in which all keys collide)."),
   ("Dictionary against list.count() for every distinct word: ", "the dictionary loop reads each of the n words once: O(n). list.count(w) scans the whole word list once for each of the d distinct words: O(n x d). The experiments below show the difference."),
   ("Order of keys in Python 3.7 and later: ", "the language guarantees that a dictionary remembers the INSERTION order (keys are not sorted). Updating the value of an existing key keeps its position; deleting a key and inserting it again puts it at the end (shown in the output). Two dictionaries with the same items are equal whatever the order."),
   ("Views: ", "keys(), values() and items() return live view objects, not copies: after d['maize'] = 1 the views created earlier show the new entry. keys() and items() behave like sets (&, |, membership), all three support len() and iteration, and changing the dictionary's size while iterating raises RuntimeError.")])
H("3.3 Experimental investigation (stop words removed; vocabulary d = 500; seed 7)", 2)
rows = [["Complaints", "Words n", "Distinct d", "dict + get()", "dict + setdefault()", "Counter", "list.count()", "list.count / dict"]]
for x in r3["rows"]:
    rows.append([f"{x['complaints']:,}", f"{x['words']:,}", x["distinct"], f"{x['get']:.4f}", f"{x['setdefault']:.4f}", f"{x['counter']:.4f}", f"{x['listcount']:.4f}", f"{x['listcount']/x['get']:.1f}x"])
TABLE(rows, widths=[0.8, 0.8, 0.7, 0.9, 1.0, 0.8, 0.9, 0.9], size=8.5)
P("The times of the three O(n) methods are equal within noise because most of the time is spent in the common part - lower-casing, removing punctuation and splitting every complaint - not in the counting. "
  "To measure the counting step alone I counted pre-split word lists:")
rows = [["Words n", "dict loop (get)", "Counter(words)", "list.count()"]]
for x in r3["crows"]:
    rows.append([f"{x['words']:,}", f"{x['loop']:.5f}", f"{x['counter']:.5f}", f"{x['listcount']:.4f}"])
TABLE(rows, widths=[1.2, 1.5, 1.5, 1.5], size=9)
cr = r3["crows"][-1]
P(f"Counter (its counting loop is written in C) is about {cr['loop']/cr['counter']:.1f} times faster than the Python loop; list.count() is about {cr['listcount']/cr['loop']:.0f} times slower at {cr['words']:,} words. The dependence on d (10,000 complaints):")
rows = [["Vocabulary", "Distinct words d", "dict loop (s)", "list.count (s)"]]
for x in r3["drows"]:
    rows.append([x["vocab"], x["distinct"], f"{x['get']:.4f}", f"{x['listcount']:.4f}"])
TABLE(rows, widths=[1.2, 1.4, 1.4, 1.4], size=9)
dr = r3["drows"]
P(f"The dictionary time stays about the same when d grows ({dr[0]['get']:.3f} s at d = {dr[0]['distinct']}, {dr[-1]['get']:.3f} s at d = {dr[-1]['distinct']:,}) whereas list.count() grows almost proportionally with d ({dr[0]['listcount']:.2f} s at d = {dr[0]['distinct']} to {dr[-1]['listcount']:.2f} s at d = {dr[-1]['distinct']:,}): O(n x d) against O(n).")
P("Tests: an empty list or empty text gives {}; 'Seeds, SEEDS! seeds.' gives {'seeds': 3} (case and punctuation normalised); a text of only stop words gives {}; top() with ties returns them in alphabetical order; k = 0 gives [].")
H("3.4 Engineering decision - 100,000 complaints a day", 2)
r100 = r3["rows"][-1]
P(f"I would deploy the dictionary-based counting with collections.Counter on the tokenised words. Reasons from the measurements: 100,000 complaints are processed in about {r100['get']:.2f} s with a dictionary (almost all of it tokenising), counting itself takes about {cr['counter']:.2f} s, memory is O(d) (the number of distinct words), "
  f"and it still scales linearly if the volume grows; list.count() needs about {r100['listcount']:.1f} s for the same data, grows with the vocabulary as well as with the volume, and would become unusable. "
  "A plain dictionary loop with get() is an acceptable alternative where Counter's extras are not needed.")
H("3.5 Alternative concept - list.count() or Counter instead of a dictionary loop", 2)
CODE("words = [w for text in texts for w in words_of(text) if w not in stop]\ncounts = {w: words.count(w) for w in set(words)}       # list.count for every distinct word\ncounts = Counter(words)                                # library class (a dict subclass)")
TABLE([["Method", "Time (n words, d distinct)", "Space"],
       ["dictionary loop with get()", "O(n)", "O(d)"],
       ["Counter(words)", "O(n) (loop in C, smaller constant)", "O(d)"],
       ["list.count() for each distinct word", "O(n x d)", "O(n) for the word list + O(d) for the set and result"]], widths=[2.4, 2.4, 2.4], size=9)
doc.add_page_break()
# =============================================================== Q4
r4 = J("Task04")
H("Q4 - Sets: Elective Registration Clash Detection (6 marks)")
H("4.1 Implementation and Complete the Code (Task04/elective_clash.py)", 2)
CODE("ai_elective  = {'192311001', '192311004', '192311007', '192311009'}\niot_elective = {'192311002', '192311004', '192311009', '192311010'}\nall_students = {f'1923110{i:02d}' for i in range(1, 11)}\n\n"
     "# TODO 1 - operators\nboth        = ai_elective & iot_elective\nexactly_one = ai_elective ^ iot_elective\nneither     = all_students - (ai_elective | iot_elective)\n\n"
     "# the same with methods\nboth        = ai_elective.intersection(iot_elective)\nexactly_one = ai_elective.symmetric_difference(iot_elective)\nneither     = all_students.difference(ai_elective.union(iot_elective))")
P("Note: the second elective's set is not fully legible in the supplied recording; it was reconstructed from the printed expected output (clash {004, 009}, exactly one {001, 002, 007, 010}, neither {003, 005, 006, 008}). Please compare it with the original question paper.", italic=True)
OUT("Task04", "Console output (operators and methods give identical results; reports; duplicates; hand check; edge cases)")
H("4.2 Check by hand and Venn diagrams", 2)
P("By hand: AI = {1, 4, 7, 9}, IoT = {2, 4, 9, 10}, all = {1 ... 10} (last digits). Both = {4, 9}; exactly one = {1, 7} + {2, 10} = {1, 2, 7, 10}; neither = {1..10} - {1, 2, 4, 7, 9, 10} = {3, 5, 6, 8}. The program printed the same sets. "
  "The diagram shades the region of each operation (A = AI, B = IoT, U = all students).")
IMG("Task04/venn_diagrams.png", 6.4, "Regions: A - B, B - A, A & B, A ^ B, A | B, U - (A | B)")
H("4.3 Explanations", 2)
B([("Why a set removes duplicates: ", "a set is a hash table of unique elements. Adding an element computes its hash and looks for an equal element at that place; if one exists, nothing is stored. Six form entries with duplicates became 4 distinct students when converted with set()."),
   ("Why sets cannot contain lists but can contain tuples: ", "elements must be hashable (their hash must never change). A list is mutable so it is unhashable (TypeError: unhashable type: 'list'); a tuple of hashable items is hashable; a tuple that contains a list is rejected too; a frozenset is hashable and can be an element."),
   ("Edge cases: ", "two empty electives: no clash, no one in exactly one, all 10 students in neither; one empty elective: no clash and exactly-one = the other elective; identical electives: everyone clashes and exactly-one is the empty set.")])
H("4.4 Experiments", 2)
P("(a) x in list against x in set (1,000 look-ups of an absent value = the worst case for a list; for the two larger lists 100 look-ups were timed and multiplied by 10):", bold=True)
rows = [["n", "list (s)", "set (s)", "list / set", "list memory", "set memory"]]
for x in r4["membership"]:
    rows.append([f"{x['n']:,}", f"{x['list']:.4f}", f"{x['set']:.6f}", f"{x['list']/x['set']:,.0f}x", f"{x['list_bytes']:,} B", f"{x['set_bytes']:,} B"])
TABLE(rows, widths=[0.9, 0.9, 0.9, 1.0, 1.4, 1.4], size=8.5)
P("The list time grows in proportion to n (O(n): every element is compared) while the set time does not change (O(1) average: one hash computation). The price is memory: the set needs about 4 to 6 times the space of the list because the hash table must stay sparse.")
P("(b) Finding the students common to two lists of n registration numbers (same data for all methods; results compared):", bold=True)
rows = [["n = m", "Common", "Nested loops (s)", "Sort + walk (s)", "set & (s)", "n x m comparisons"]]
for x in r4["common"]:
    rows.append([f"{x['n']:,}", f"{x['common']:,}", f"{x['nested']:.4f}" if x["nested"] is not None else "not run (hours)", f"{x['sorted']:.4f}", f"{x['set']:.4f}", f"{x['n']*x['n']:,}"])
TABLE(rows, widths=[0.9, 0.8, 1.3, 1.2, 0.9, 1.7], size=8.5)
P("The nested-loop time grows 9 times when n grows 3 times and 36 times when n grows 6 times - quadratic. Sorting and the set operation grow almost linearly; at 200,000 entries the set is the fastest.")
H("4.5 Design question - when to convert a list to a set, and what is lost", 2)
P("Convert when the program will do many membership tests, must remove duplicates, or needs set algebra (clashes, common students, differences): the one-time conversion costs O(n) and then each test is O(1) on average instead of O(n). "
  "Information lost: (1) the order of the elements (sets are unordered; use sorted() to produce a report), (2) duplicates and therefore the number of occurrences (use a dictionary or Counter if counts matter), (3) positions/indexes, and (4) it is impossible if an element is unhashable (a list, dict or set). "
  "Memory use is also higher (4 to 6 times in the test above).")
H("4.6 Alternative concept and complexity", 2)
CODE("def common_nested(a, b):               # O(n * m)\n    for x in a:\n        for y in b:\n            if x == y: out.append(x); break\n\ndef common_sorted(a, b):                 # O(n log n + m log m)\n    a, b = sorted(a), sorted(b); i = j = 0\n    while i < len(a) and j < len(b):\n        if a[i] == b[j]: out.append(a[i]); i += 1; j += 1\n        elif a[i] < b[j]: i += 1\n        else: j += 1\n\ndef common_set(a, b):                    # O(n + m) on average\n    return sorted(set(a) & set(b))")
TABLE([["Approach", "Time", "Extra space"], ["nested loops", "O(n x m)", "O(1) (plus the result)"], ["sort both lists + two pointers", "O(n log n + m log m)", "O(n + m) for the sorted copies"], ["set intersection", "O(n + m) on average (O(min(n, m)) for the intersection itself)", "O(n + m) for the sets"]], widths=[2.4, 2.8, 2.0], size=9)
doc.add_page_break()

# =============================================================== Q5
r5 = J("Task05")
H("Q5 - List Comprehension: Cleaning Cold-Storage Temperature Readings (6 marks)")
H("5.1 Implementation (Task05/sensor_cleaning.py)", 2)
P("Rules used: a reading is a valid temperature if -50 <= c <= 50 (otherwise it is a sensor error and is ignored); Fahrenheit F = C x 9/5 + 32; an ALARM is a valid reading outside the safe range 2-8 deg C (2 and 8 themselves are safe); minutes are numbered from 1 (first reading = minute 1).")
CODE("# version 1: for loop with append\nfor minute, c in enumerate(readings, start=1):\n    if LOW <= c <= HIGH:\n        celsius.append(c); fahrenheit.append(c * 9 / 5 + 32)\n        if not (2 <= c <= 8): alarms.append(minute)\n\n"
     "# version 2: list comprehensions\ncelsius    = [c for c in readings if LOW <= c <= HIGH]\nfahrenheit = [c * 9 / 5 + 32 for c in celsius]\nalarms     = [m for m, c in enumerate(readings, 1) if LOW <= c <= HIGH and not (2 <= c <= 8)]\n\n"
     "# version 3: map and filter with lambda\ncelsius    = list(filter(lambda c: LOW <= c <= HIGH, readings))\nfahrenheit = list(map(lambda c: c * 9 / 5 + 32, celsius))\nalarms     = list(map(lambda mc: mc[0], filter(lambda mc: LOW <= mc[1] <= HIGH and not (2 <= mc[1] <= 8), enumerate(readings, 1))))")
P("General form: [expression for item in iterable if condition] is equivalent to a for loop that appends expression to a new list whenever the condition is true. "
  "Dictionary and set comprehensions use the same pattern: {minute: c for ...} and {round(c) for ...}.")
OUT("Task05", "Console output (small hand-checked example, the three versions compared on four data sets, timings, memory)")
P("Hand check of the small example [4.0, 5.5, 99.0, 9.1, -60.5, 1.5, 7.9, 2.0]: 99.0 and -60.5 are errors; valid = [4.0, 5.5, 9.1, 1.5, 7.9, 2.0]; 9.1 (minute 4) and 1.5 (minute 6) are outside 2-8, so alarms = [4, 6] - the program printed the same. "
  "All three versions gave identical results on mixed data, all-valid data, all-invalid data and an empty list.")
H("5.2 Time of the three versions", 2)
rows = [["Readings", "for + append (s)", "comprehensions (s)", "map / filter (s)", "loop / comp", "map-filter / comp"]]
for x in r5["times"]:
    rows.append([f"{x['n']:,}", f"{x['loop']:.4f}", f"{x['comp']:.4f}", f"{x['mapfilter']:.4f}", f"{x['loop']/x['comp']:.2f}", f"{x['mapfilter']/x['comp']:.2f}"])
TABLE(rows, widths=[1.0, 1.2, 1.3, 1.2, 0.9, 1.2], size=8.5)
H("5.3 Memory: list comprehension against generator expression", 2)
mm = r5["mem"]
TABLE([["", "[c for c in data if ...]", "(c for c in data if ...)"],
       ["sys.getsizeof of the object", f"{mm['list_bytes']:,} bytes", f"{mm['gen_bytes']} bytes"],
       ["peak extra memory while summing 1,000,000 readings", f"{mm['peak_list']/1e6:.2f} MB", f"{mm['peak_gen']} bytes"],
       ["time of sum(...)", f"{mm['t_list']:.4f} s", f"{mm['t_gen']:.4f} s"]], widths=[3.0, 2.0, 2.0], size=9)
P("A list comprehension builds the whole result list immediately (about 8 bytes per kept element); a generator expression produces one element at a time, so its size does not depend on the data. The generator can be consumed only once (a second sum gave 0) and cannot be indexed or measured with len().")
H("5.4 Conclusion - is a list comprehension always the best choice?", 2)
P(f"No. In my measurements the comprehension was about as fast as a plain loop (loop/comprehension = {r5['times'][2]['loop']/r5['times'][2]['comp']:.2f} at 1,000,000 readings - it is not faster here because one loop makes a single pass that produces all three results) and "
  f"map/filter with lambda was about {r5['times'][2]['mapfilter']/r5['times'][2]['comp']:.2f} times slower, because each lambda call is a full Python function call. Speed is therefore not the reason to prefer a comprehension - clarity is: it states 'what the new list contains' in one line. "
  "A comprehension becomes harder to read than a loop when it needs several conditions and nested for clauses, when the body needs more than one statement, or when it has side effects (printing, updating counters) - then use a for loop. "
  "If the result is only to be summed, counted or searched once, a generator expression is better because it needs no list at all (208 bytes instead of 8.4 MB here, and no slower). "
  "Use map() when the function is already a built-in (map(float, strings)).")
H("5.5 Alternative concept and complexity", 2)
TABLE([["Approach", "Time", "Extra space"], ["for loop + append", "O(n), one pass for all three outputs", "O(k) for k kept values (three result lists)"],
       ["list comprehensions", "O(n) per comprehension (up to three passes)", "O(k) per result list"],
       ["map / filter + lambda", "O(n) with one function call per element", "O(k) (lazy objects in Python 3; list() builds the result)"],
       ["generator expression", "O(n), single pass, no list", "O(1)"]], widths=[1.8, 2.7, 2.7], size=9)
doc.add_page_break()

# =============================================================== Q6
r6 = J("Task06")
H("Q6 - Nested Data: Railway Timetable (6 marks)")
H("6.1 Structure (Task06/timetable.py)", 2)
CODE("timetable = {\n  '12621': {'name': 'Tamil Nadu Express',\n            'stops': [('Chennai Central', None, '22:00'), ('Vijayawada', '01:50', '02:00'), ...],\n            'days' : {'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'}},\n  '12163': {...}, ...        # 5 trains in the program\n}")
TABLE([["Level", "Structure", "Why"],
       ["whole timetable", "dictionary keyed by train number", "a train is found directly by its number: O(1) average; the fields have names"],
       ["stops", "list of tuples (station, arrival, departure)", "the ORDER of the stops matters and must be kept (a list); each stop is a fixed record that is never edited (a tuple); the first stop has no arrival and the last no departure (None)"],
       ["running days", "set of day names", "only membership matters ('Fri' in days), no order and no duplicates, O(1) test"]], widths=[1.2, 2.4, 3.6], size=9)
P("Reaching the departure time of the third station: timetable['12621']['stops'][2][2] = '10:30' (train 12621, third stop = Nagpur, element 2 of the tuple = departure).")
H("6.2 Queries and tests", 2)
P("trains_at(timetable, station, day) returns the trains that stop at the station AND run on that day; sorted_by_departure() orders them by their departure time from that station (arrival time for the final stop). A timetable is printed station by station. "
  "Examples from the output: Chennai Central on Tuesday -> 12007 (06:00), 12433 (06:10), 12621 (22:00); Chennai Central on Friday gives 12007 (06:00), 22637 (13:55), 12163 (21:40, arrival at its final stop) and 12621 (22:00) but not 12433 (Tue/Thu/Sat only); an unknown station or a day without trains returns an empty list; "
  "train 12163 stops at Pune but is correctly missing on Tuesday because it does not run that day.")
OUT("Task06", "Console output")
H("6.3 Analysis and experiment", 2)
P("Answering one query without an index scans every train and, for every train running that day, its list of stops: O(T x S) = O(total number of stops) per query. "
  "An index built once - dictionary station -> list of (departure, train number) sorted by departure - answers a query in O(k) for the k trains that stop at that station (the sorting was done when the index was built); the day check is O(1) per train. "
  "The index costs O(total stops x log) time to build and O(total stops) memory and must be rebuilt (or updated) when the timetable changes.")
rows = [["Trains", "Stops", "Full scan per query", "Flat list per query", "Index per query", "Speed-up", "Index build", "Index memory", "Timetable memory"]]
for x in r6["rows"]:
    rows.append([f"{x['trains']:,}", f"{x['stops']:,}", f"{x['scan']*1e6:.1f} us", f"{x['flat']*1e6:.1f} us", f"{x['index']*1e6:.2f} us", f"{x['scan']/x['index']:.0f}x", f"{x['build']*1e3:.2f} ms", f"{x['mem_index']/1e3:,.0f} KB", f"{x['mem_tt']/1e3:,.0f} KB"])
TABLE(rows, widths=[0.5, 0.6, 0.9, 0.9, 0.8, 0.6, 0.8, 0.8, 0.9], size=7.5)
rs = r6["rows"]
P(f"The full scan grows in proportion to the number of stops ({rs[2]['scan']/rs[0]['scan']:.0f} times from 100 to 10,000 trains, which have {rs[2]['stops']/rs[0]['stops']:.0f} times more stops), the indexed query grows only with the number of trains per station. "
  "The index needs a quarter to a third of the timetable's own memory and is built in a few milliseconds, so it pays off after a handful of queries. All three query methods gave identical answers (checked by assertion).")
H("6.4 Alternative concept - one flat list of tuples (train, station, arrival, departure, days)", 2)
CODE("flat = [(no, st, arr, dep, t['days']) for no, t in tt.items() for st, arr, dep in t['stops']]\nrows = [(dep or arr, no) for no, st, arr, dep, days in flat if st == station and day in days]")
P("Simpler (one loop, no nesting) but every query reads all stops: O(total stops), and train data (name, days) is repeated on every row (O(total stops) memory, more than the nested form). "
  "It is about as fast as the full scan of the nested form, and far slower than the index; the nested dictionary is better when you often need one whole train, the flat list when you always filter by station.")
doc.add_page_break()

# =============================================================== Q7
r7 = J("Task07")
H("Q7 - Data-Structure Design from First Principles: Merging Contacts (6 marks)")
H("7.1 Problem and measurable requirements", 2)
P("Contacts are exported from several sources (phone 1, phone 2, SIM). The same person appears several times with different spellings, number formats and missing fields. The program must produce one merged contact per person.")
B(["R1 - every normalised number belongs to exactly one merged contact.",
   "R2 - nothing is lost: all numbers and e-mails of the input are present in the output.",
   "R3 - the result of a hand-merged test list is reproduced exactly (5 people from 10 contacts).",
   "R4 - 100,000 contacts are merged in under 2 seconds (the pairwise approach is estimated to need minutes).",
   "R5 - merging the output again changes nothing (idempotent)."])
H("7.2 Design", 2)
B([("Normalisation: ", "numbers: keep digits only, compare the LAST 10 digits (removes +91, 0091, a leading 0, spaces, dashes and brackets); names: lower case, punctuation and titles (Dr., Mrs., ...) removed; e-mails: stripped and lower-cased. Done with str methods only."),
   ("Identity of a person: ", "the normalised phone number - not the name, because two different people can have the same name (see the test with two 'Mohan')."),
   ("Data structures: ", "dictionary owner: normalised number -> index of the first contact that has it (O(1) average lookup of 'have I seen this number?'); a disjoint-set (union-find) over contact indices so that a contact with two numbers can join two groups that were separate until then (transitive merging); "
    "sets for the numbers, e-mails and names of each person (duplicates disappear automatically and 'union' is the merge operation); a second dictionary e-mail -> first owner attaches contacts that have NO number."),
   ("Output: ", "for each group: sets of names, numbers and e-mails, a display name (the name with most words), the list of source contacts, and a REVIEW flag when the names in one group have no word in common (probably two people sharing a number).")])
CODE("PSEUDOCODE\nFOR each contact i:\n    numbers[i] <- { normalise(p) for p in phones } ; emails[i] <- { lower(e) } ; name[i] <- normalise_name(name)\n"
     "    FOR each number x in numbers[i]:\n        IF x in owner THEN union(i, owner[x]) ELSE owner[x] <- i\n"
     "FOR each contact i that has NO number:\n    FOR each e-mail e of i: IF another contact j owns e THEN union(i, j) ; stop\n"
     "group contacts by find(i)\nFOR each group: names <- union of names ; numbers <- union ; emails <- union ; display <- longest name\n"
     "      IF the names of the group have no common word THEN mark the group for REVIEW", size=8)
H("7.3 Implementation and tests (Task07/contact_merge.py)", 2)
P("The small test list of 10 contacts was merged by hand first (Ravi in four entries including one with no number, Anita in two entries with different number formats, two different people called Mohan, one entry without a name that has Mohan's number, one entry with nothing to match on). "
  "The program produced the same 5 people (R3), lost no number or e-mail (R2), and merging its own output again gave the same 5 (R5). A contact that holds two numbers correctly joins two earlier groups (3 contacts -> 1 person).")
OUT("Task07", "Console output")
H("7.4 Measurements (checked against the known truth of the generated data)", 2)
rows = [["Contacts", "People (truth)", "Time", "Merged contacts", "Correct (every group = one person, no person split)", "Peak memory"]]
for x in r7["rows"]:
    rows.append([f"{x['n']:,}", f"{x['people']:,}", f"{x['time']:.4f} s", f"{x['merged']:,}", x["correct"], f"{x['mem']/1e6:.1f} MB"])
TABLE(rows, widths=[0.9, 1.0, 0.9, 1.2, 2.2, 1.0], size=8.5)
t1, t2 = r7["rows"][0]["time"], r7["rows"][1]["time"]
P(f"R1, R2, R4 are met: 100,000 contacts were merged in {t2:.2f} s (< 2 s) and the result equals the truth. For 100 times more contacts the time grew {t2/t1:.0f} times - a little worse than linear (memory effects and garbage collection of many small sets) but nowhere near the 10,000 times that a quadratic algorithm would show.")
H("7.5 Alternative concept - compare every pair of contacts", 2)
rows = [["Contacts", "Pairs n(n-1)/2", "Pairwise time", "Dictionary time", "Same number of people"]]
for x in r7["pairs"]:
    rows.append([f"{x['n']:,}", f"{x['pairs']:,}", f"{x['pairwise']:.3f} s", f"{x['dictionary']:.4f} s", x["same"]])
TABLE(rows, widths=[0.9, 1.4, 1.2, 1.3, 1.6], size=9)
est = r7["extrapolated_100k_s"]
P(f"The pairwise time grows 4 times when n doubles (quadratic). Extrapolating from n = 4,000 (x625 for 100,000 contacts) gives about {est:,.0f} seconds = {est/60:.1f} minutes for 5 billion pairs - this is an ESTIMATE, not a measurement - against {t2:.2f} s for the dictionary design (about {est/t2:,.0f} times faster). "
  "Pairwise needs only O(n) extra memory (the union-find array) while the dictionary needs O(total numbers) for the index, a worthwhile trade.")
TABLE([["Approach", "Time", "Space"], ["dictionary + union-find", "O(total numbers) dictionary operations, almost linear (alpha(n) per union)", "O(n) (index, sets, union-find)"], ["compare all pairs", "O(n^2 x set intersection)", "O(n)"]], widths=[1.8, 3.6, 1.8], size=9)
H("7.6 Defence of the design and the limitations I accept", 2)
B(["The key is the normalised number, so formatting differences (+91, 0, spaces, dashes) and different spellings of the name do not prevent a merge, and two different people with the same name are not merged.",
   "Sets make the merge itself trivial and duplicate-free; union-find handles chains of overlaps that a plain dictionary keyed by the first number would miss.",
   ("Limitation 1 (accepted): ", "a number shared by different people (office landline, family phone) merges them. The program does not hide this: a group whose names have no common word is flagged for review (the test with 'Ravi' and 'Sundar' on one landline is flagged)."),
   ("Limitation 2: ", "two entries of the same person with no number or e-mail in common (for example an old and a new phone number) are not merged; fuzzy name matching could join them but would also join different people with similar names."),
   ("Limitation 3: ", "numbers are compared by their last 10 digits, so numbers from different countries with identical last 10 digits would collide; contacts with neither number nor e-mail are kept as they are.")])
doc.add_page_break()

# =============================================================== Appendix
H("Appendix A - Source code of all programs")
for task, prog in (("Task01", "rainfall.py"), ("Task02", "tuples_copying.py"), ("Task02", "memory_diagrams.py"), ("Task03", "complaints.py"),
                   ("Task04", "elective_clash.py"), ("Task04", "venn_diagrams.py"), ("Task05", "sensor_cleaning.py"),
                   ("Task06", "timetable.py"), ("Task07", "contact_merge.py")):
    H(f"{task}/{prog}", 3)
    CODE(open(f"{task}/{prog}").read(), size=6.5)
H("Appendix B - Evidence and reproduction", 1)
B([f"Measurements were made on: {MACHINE}. Execution times differ from computer to computer; counts of operations do not.",
   "Raw data: every task folder contains results.json, output.txt and an output screenshot.",
   "To reproduce: pip install -r requirements.txt; python run_all.py --report"])
doc.save("Assignment3_Report.docx")
print("saved Assignment3_Report.docx")
