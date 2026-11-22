"""Builds Assignment2_Report.docx from the programs, their output.txt files and results.json.
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
REPO = "https://github.com/<your-username>/CSA08-<RegisterNumber>-Assignment2"
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
r = t.add_run("\n\nCSA08 - Python Programming\nAssignment 2 (CO2) - Assignment Report")
r.bold = True
r.font.size = Pt(22)
TABLE([["Student name", NAME], ["Register number", REGNO], ["GitHub repository", REPO],
       ["Environment used for the measurements", MACHINE]], widths=[2.4, 4.3], header=False, size=11)
P("Contents: Q1 Decisions with many boundaries - Q2 Loops that count attempts - Q3 Vehicle registration validator - "
  "Q4 Building long text - Q5 Functions, parameters and scope - Q6 Recursion and its limits - "
  "Q7 Day-4 Design Challenge - Appendix A (source code) - Appendix B (how the evidence was produced).")
P("Method used for every question: Predict, Design, Implement, Measure, Analyse, Evaluate (Q7: Diagnose, Redesign, Validate). "
  "All numbers in this report are copied from results.json / output.txt of the programs in the repository.", italic=True)
doc.add_page_break()

# =============================================================== Q1
r1 = J("Task01")
H("Q1 - Decisions with Many Boundaries (6 marks)")
H("1.1 Rule used", 2)
B(["units <= 100: FULL subsidy.",
   "101 <= units <= 200: PARTIAL subsidy only if the household has a ration card, otherwise NONE.",
   "units > 200: NONE unless a member is above 80 years old, then SENIOR subsidy."])
H("1.2 Predictions (made before running any code)", 2)
TABLE([["#", "Units", "Ration card", "Member > 80", "Predicted decision", "Reason"],
       ["1", "150", "Yes", "Yes", "PARTIAL", "Falls in the 101-200 slab; the senior member only matters above 200"],
       ["2", "100", "No", "No", "FULL", "Boundary: 100 belongs to the first slab"],
       ["3", "100", "Yes", "No", "FULL", "Boundary: a ration card must not add a second subsidy"],
       ["4", "101", "Yes", "No", "PARTIAL", "Boundary: first unit of the middle slab, has a card"],
       ["5", "101", "No", "No", "NONE", "Boundary: middle slab, no card"],
       ["6", "200", "Yes", "No", "PARTIAL", "Boundary: last unit of the middle slab"],
       ["7", "201", "No", "Yes", "SENIOR", "Boundary: first unit of the top slab, senior member"],
       ["8", "201", "Yes", "No", "NONE", "Boundary: top slab, ration card is irrelevant"]],
      widths=[0.3, 0.5, 0.8, 0.9, 1.1, 3.0], size=8.5)
H("1.3 Why separate if statements can give more than one result", 2)
P("Every plain if is evaluated on its own. When the conditions overlap, several of them can be true for the same household, "
  "so several statements run and several subsidies are added. In the faulty program the second condition was written as "
  "units <= 200 and ration_card (lower bound missing) and the third as units > 100 and senior (should be > 200). A household with "
  "100 units and a ration card therefore satisfied the first AND the second condition. In an if-elif-else chain the conditions are "
  "tested from top to bottom and the first true branch is executed; all the other branches are skipped. Because the final else "
  "catches every remaining case, exactly one branch always runs, so exactly one decision is produced.")
H("1.4 Implementation (Task01/subsidy.py)", 2)
B(["decide_buggy - separate if statements (returns the list of all subsidies granted).",
   "decide_elif - if-elif-else with the chained comparison 101 <= units <= 200.",
   "decide_match - match-case version (alternative concept).",
   "decide_table - list of (upper limit, rule) pairs searched in a loop (alternative concept)."])
H("1.5 Observed results at every boundary", 2)
rows = [["Units", "Card", "Senior", "Predicted", "Separate ifs", "if-elif-else", "match-case", "Table"]]
for x in r1["rows"]:
    rows.append([x["units"], "Yes" if x["ration"] else "No", "Yes" if x["senior"] else "No", x["predicted"],
                 ", ".join(x["buggy"]) or "(none)", x["elif_"], x["match"], x["table"]])
TABLE(rows, widths=[0.5, 0.5, 0.6, 0.9, 1.4, 0.9, 0.9, 0.8], size=8.5)
P(f"The separate-if version gave a wrong result for {r1['buggy_wrong']} of the 8 predicted households (100 units with a card: FULL + PARTIAL; "
  f"150 units with card and senior: PARTIAL + SENIOR). Checking all 301 x 2 x 2 = 1204 combinations (0-300 units), it granted more than one "
  f"subsidy in {r1['buggy_double_exhaustive']} cases. The three correct versions agreed with each other in all 1204 cases and matched all 8 predictions.")
OUT("Task01", "Console output")
H("1.6 Design decision - nested if or combined Boolean conditions?", 2)
P("I selected if-elif-else with a chained comparison for the slab, and a single Boolean test inside the slab "
  "(PARTIAL if ration_card else NONE). Reasons: (1) the slab boundaries 100/101/200/201 each appear exactly once, so a change of a limit is made in one place; "
  "(2) the order of the branches gives the mutual exclusion for free, so no condition needs to repeat the previous one's negation; "
  "(3) a fully flat chain using and/or (elif 101 <= units <= 200 and ration_card ... elif units > 200 and senior ... else NONE) "
  "is also correct but repeats the slab test for every attribute and puts the 'NONE' cases in a catch-all else, which hides the policy "
  "(two different reasons for NONE); (4) deep nesting makes the reader follow indentation levels and repeats 'NONE' in each branch. "
  "The hybrid is the shortest version that is still one-to-one with the written rule.")
H("1.7 Alternative concept and complexity analysis", 2)
CODE("match (units, ration_card, senior):\n    case (u, _, _) if u <= 100: return 'FULL'\n    case (u, True, _) if u <= 200: return 'PARTIAL'\n"
     "    case (u, False, _) if u <= 200: return 'NONE'\n    case (_, _, True): return 'SENIOR'\n    case _: return 'NONE'\n\n"
     "SLABS = [(100, rule_full), (200, rule_partial), (inf, rule_senior)]\nfor upper, rule in SLABS:\n    if units <= upper: return rule(ration_card, senior)")
tm = r1["timings_ns"]
TABLE([["Approach", "Time per decision (k slabs)", "Extra space", "Measured (ns, 150 units)"],
       ["if-elif-else", "O(k) worst case (k = 3, constant)", "O(1)", tm["if-elif-else"]],
       ["match-case", "O(k): cases are tried in order, guards evaluated one by one", "O(1)", tm["match-case"]],
       ["Table of (limit, decision) pairs", "O(k) linear scan (O(log k) with bisect on sorted limits)", "O(k) for the table", tm["slab table"]]],
      widths=[1.7, 2.8, 1.2, 1.2], size=8.5)
P("With only three slabs all approaches are constant in practice; if-elif-else is fastest because the interpreter does no pattern construction or function calls. "
  "The table version costs a little more time and O(k) memory but is the best choice when slabs change often, because the limits become data (a list or a file) "
  "instead of code and a new slab needs no change in the control flow.")
doc.add_page_break()

# =============================================================== Q2
r2 = J("Task02")
H("Q2 - Loops that Count Attempts (4 marks)")
H("2.1 Designs (Task02/otp_kiosk.py)", 2)
CODE("def verify_while(read):                       def verify_for(read):\n"
     "    attempts = 0                                  for attempt in range(1, 4):\n"
     "    while attempts < 3:                               code = ''\n"
     "        code = read().strip()                         while code == '':        # blank not counted\n"
     "        if code == '': continue                           code = read().strip()\n"
     "        attempts += 1                                 if code == OTP: return 'GRANTED'\n"
     "        if code == OTP: return 'GRANTED'          else:                         # loop-else\n"
     "    return 'LOCKED'                                   return 'LOCKED for 30 minutes'")
P("Inputs are supplied from lists so every scenario can be repeated exactly. A blank entry is not counted: the while version uses continue before the counter is incremented; "
  "the for version waits inside an inner loop until something is typed, so the range(3) slot is not consumed.")
H("2.2 break, continue, pass and loop-else", 2)
B([("continue: ", "a blank entry skips the rest of the iteration (no attempt counted in the while version)."),
   ("break: ", "in the demonstration loop a correct OTP leaves the loop; the loop-else is then NOT executed."),
   ("pass: ", "an empty placeholder branch (for non-numeric input) that keeps the code valid while doing nothing."),
   ("loop-else: ", "runs only if the loop ended without break (three wrong attempts) - this is where the account is locked.")])
OUT("Task02", "Console output (all five scenarios agree in all three designs; demonstration of the four statements; changed condition)")
H("2.3 Answer the following", 2)
B([("When is while more natural than for? ", "When the number of iterations is not fixed in advance: here blank entries do not count and the limit may change (3 -> 5). "
    "A for loop over range(3) is natural only when the number of passes is exactly known."),
   ("Which bug can occur if the counter is updated in the wrong place? ", "(a) Incrementing before the blank-entry check counts blank entries as attempts, so a customer is locked out by pressing Enter. "
    "(b) Incrementing only inside the 'correct OTP' branch means wrong codes never increase the counter - an infinite loop. "
    "(c) Incrementing at the top of the loop, before reading, gives an off-by-one error (the customer gets only two real attempts).")])
H("2.4 Changed condition - two extra attempts after a correct security answer", 2)
P("The for-range(3) design is fixed at three passes, so it cannot simply be extended. The while design only needs a variable allowed (3) that is raised to 5 once, "
  "after the third failed attempt, if the security answer is correct. A flag bonus_used makes the extra attempts available only once; "
  "without this flag a customer could answer the question again and again and never be locked. Re-evaluating the design shows that the loop condition "
  "'attempts < allowed' (a value that can change) is the right abstraction, which is why the while design is kept. "
  "Observed: correct answer then correct 4th OTP -> ACCESS GRANTED on attempt 4; correct answer but five wrong OTPs -> LOCKED after 5 attempts; wrong answer -> LOCKED after 3 attempts.")
H("2.5 Alternative concept - recursion and complexity", 2)
CODE("def verify_recursive(read, attempt=1):\n    if attempt > 3: return 'LOCKED'\n    code = read().strip()\n"
     "    if code == '': return verify_recursive(read, attempt)        # same attempt number\n"
     "    if code == OTP: return f'GRANTED on attempt {attempt}'\n    return verify_recursive(read, attempt + 1)")
TABLE([["Version", "Time", "Stack space"],
       ["while loop", "O(a) for a attempts", "O(1)"],
       ["for range + loop-else", "O(a)", "O(1)"],
       ["recursive", "O(a)", "O(a) - one stack frame per attempt (and one per blank entry, because the blank case also calls itself)"]],
      widths=[1.7, 1.7, 3.5], size=9)
P("All versions gave identical answers in the five scenarios. With a = 3 the difference is irrelevant, but the loop is the safer design: its stack use does not depend on the user's behaviour, "
  "whereas the recursive version grows with every blank entry and could reach Python's recursion limit.")
doc.add_page_break()

# =============================================================== Q3
r3 = J("Task03")
H("Q3 - Vehicle Registration Number Validator (6 marks)")
H("3.1 Solution (Task03/vehicle_validator.py)", 2)
CODE("def normalise(text):                 # TODO 1\n    return text.replace(' ', '').replace('-', '').upper()\n\n"
     "def is_valid(reg):                   # TODO 2\n    n = len(reg)\n    if n not in (9, 10): return False\n"
     "    return (reg[:2].isalpha() and reg[2:4].isdigit()\n            and reg[4:-4].isalpha() and reg[-4:].isdigit())\n\n"
     "def format_receipt(reg):             # extra function\n    return ' '.join([reg[:2], reg[2:4], reg[4:-4], reg[-4:]])")
P("Only the permitted operations are used. The series part is reg[4:-4]: whatever lies between the 4-character prefix and the 4-digit number, so its length is n - 8 = 1 or 2 letters; "
  "a length check of 9 or 10 is therefore enough to enforce '1 or 2 letters'.")
H("3.2 Predictions and observed results (six inputs of my choice, two or more invalid)", 2)
rows = [["Input", "Normalised", "Predicted", "Observed", "Receipt format"]]
for x in r3["rows"]:
    rows.append([x["raw"], x["norm"], "valid" if x["predicted"] else "INVALID", "valid" if x["observed"] else "INVALID", x["receipt"]])
TABLE(rows, widths=[1.5, 1.4, 1.0, 1.0, 1.7], size=9)
P("kl 7 cc 4567 fails because the district has one digit; TN09AB123 fails because the number has three digits; T109AB1234 fails because a digit stands where the state letter is required. "
  "The four numbers given in the question gave exactly the expected output (valid, valid, INVALID, INVALID).")
OUT("Task03", "Console output")
H("3.3 Inquiry", 2)
B([("1. Why are strings immutable? ", "A string can then be shared safely by many variables without copying (no defensive copies), it can be used as a dictionary key or set member because its hash never changes "
    "(the hash is cached), Python can reuse (intern) equal strings, and strings used as names, file paths or keys cannot be altered behind the program's back. "
    "The price is that every 'change' builds a new string."),
   ("2. Why does text.upper() not modify the original? ", "Because the original object cannot be changed, upper() builds and returns a NEW string. The run shows t.upper() returns 'TN09AB1234' "
    "while t is still 'tn09ab1234' and the two are different objects; assigning t[0] = 'T' raises TypeError."),
   ("3. What do s[-4:] and s[4:-4] return? ", "For the 9-character 'MH12A9999': s[-4:] = '9999' and s[4:-4] = 'A'. For the 10-character 'TN09AB1234': s[-4:] = '1234' and s[4:-4] = 'AB'. "
    "Negative indices count from the end, so the same two slices work for both lengths.")])
H("3.4 Alternative concept - regular expression", 2)
CODE("re.fullmatch(r\"[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}\", reg)")
P(f"Time: both approaches inspect each character a constant number of times, so both are O(L) for a number of length L. Measured per validation: slicing {r3['t_slice_ns']} ns, regex {r3['t_regex_ns']} ns "
  "(the regex is not slower in complexity, only in constant factors for such short strings).")
TABLE([["Aspect", "Slicing + string methods", "Regular expression"],
       ["Readability", "Verbose but every rule is a visible, separate step; easy for beginners to follow", "One compact line; powerful but cryptic to readers who do not know the syntax"],
       ["Ease of modification", "Changing the series to 1-3 letters needs a new length test and slice indices (easy to get wrong)", "Change {1,2} to {1,3} in the pattern"],
       ["Error reporting", "Easy to report WHICH part failed", "Only match / no match"],
       ["Accuracy notes", "isalpha()/isdigit() also accept non-ASCII letters and digits; add isascii() if needed", "[A-Z] and [0-9] are strictly ASCII"]],
      widths=[1.4, 2.7, 2.7], size=8.5)
doc.add_page_break()

# =============================================================== Q4
r4 = J("Task04")
R = r4["results"]
H("Q4 - Building Long Text: + or join()? (6 marks)")
H("4.1 Implementations (Task04/string_building.py)", 2)
CODE("def build_plus(parts):\n    text = ''\n    for p in parts: text += p + ';'\n    return text\n\n"
     "def build_join(parts):                       # TODO 1\n    return ';'.join(parts) + ';'\n\n"
     "def build_fstring(parts):                     # one f-string per line\n    return ''.join(f'{p};' for p in parts)")
H("4.2 Prediction (before measuring)", 2)
P("Prediction: join() is the fastest and += the slowest. A string cannot be changed, so s += piece creates a new string of length len(s) + len(piece) and copies all the old characters into it; "
  "after n pieces up to O(n^2) characters have been copied. join() first adds up the lengths, allocates the result once and copies every piece once: O(n). "
  "The f-string method creates one extra small string per line before the final join, so I expected it to lie between the two.")
H("4.3 Program from the question", 2)
P(f"same text: True | length: {r4['length']:,} (identical to the expected length 3,048,890). In the single run of the given program: += time {r4['program_t_plus']:.4f} s, join time {r4['program_t_join']:.4f} s.")
H("4.4 Measured execution times (seconds; three runs each, average reported)", 2)
rows = [["Method", "n = 1,000 (3 runs)", "avg", "n = 10,000 (3 runs)", "avg", "n = 200,000 (3 runs)", "avg"]]
for name in ("+= loop", "list + join", "f-string + join", "StringIO", "file write", "+= on attribute"):
    row = [name]
    for n in (1000, 10000, 200000):
        k = f"{name}|{n}"
        if k in R:
            row += [" / ".join(f"{x:.5f}" for x in R[k]["runs"]), f"{R[k]['avg']:.5f}"]
        else:
            row += ["not run (quadratic)", "-"]
    rows.append(row)
TABLE(rows, widths=[1.1, 1.35, 0.6, 1.35, 0.6, 1.35, 0.6], size=7.5)
plus, join, fs = R["+= loop|200000"]["avg"], R["list + join|200000"]["avg"], R["f-string + join|200000"]["avg"]
att1, att10 = R["+= on attribute|1000"]["avg"], R["+= on attribute|10000"]["avg"]
loc10 = R["+= loop|10000"]["avg"]
OUT("Task04", "Console output")
H("4.5 Analysis - results explained with string immutability", 2)
B([f"At 200,000 lines join() took {join:.4f} s on average; += took {plus:.4f} s ({plus/join:.1f} times longer) and the f-string version {fs:.4f} s ({fs/join:.1f} times longer). "
   "join() was the fastest at every size, as predicted. My prediction for the f-string method was only partly right: in my runs it was not between the two but about as slow as +=, "
   "because the generator creates an extra short string for each of the 200,000 lines and pays the interpreter overhead of resuming the generator each time; the final join is cheap compared with this per-line cost.",
   f"The += loop does NOT show the full quadratic growth in this test, because CPython has an optimisation: when the left-hand side is a local variable that holds the only reference to the string, "
   f"the string is resized in place instead of copied. The optimisation is an implementation detail, not a language guarantee (it does not exist in other Python implementations such as PyPy and it stops working "
   f"as soon as the string has a second reference).",
   f"To expose the real cost of immutability I repeated += with the target stored as an attribute (self.text += ...), where the optimisation cannot be applied: the time rose from {att1:.5f} s (1,000 lines) to {att10:.5f} s (10,000 lines), "
   f"a factor of {att10/att1:.0f} for 10 times more lines - quadratic behaviour - and it is {att10/loc10:.0f} times slower than the same 10,000 lines with the local-variable +=. I did not run this variant at 200,000 lines because the copying would take minutes.",
   "Why join() remains the recommended practice: it is O(n) in every situation, on every Python implementation and for every kind of target; += is fast only by luck of an optimisation that disappears when the code is restructured."])
H("4.6 Alternative concept - StringIO or writing line by line to a file", 2)
CODE("buf = io.StringIO()\nfor p in parts:\n    buf.write(p); buf.write(';')\ntext = buf.getvalue()\n\n"
     "with open('statement.txt', 'w') as f:        # nothing large kept in memory\n    for p in parts: f.write(p + ';')")
sio, fw = R["StringIO|200000"]["avg"], R["file write|200000"]["avg"]
TABLE([["Approach", "Time", "Memory", f"Measured at 200,000 lines (s)"],
       ["+= on a local string", "O(n) with the CPython shortcut, up to O(n^2) characters copied without it", "O(n) result (+ one temporary copy when not optimised)", f"{plus:.4f}"],
       ["list of parts + join()", "O(n)", "O(n) for the list of parts + O(n) for the result (about 2 x the text)", f"{join:.4f}"],
       ["io.StringIO", "O(n) amortised (buffer grows geometrically)", "O(n) buffer, no list of parts", f"{sio:.4f}"],
       ["write line by line to a file", "O(n) plus disk-buffer cost", "O(1) extra - the text never has to exist in memory (best for huge statements)", f"{fw:.4f}"]],
      widths=[1.5, 2.1, 2.3, 1.0], size=8.5)
P("Conclusion: for building a statement in memory use join(); when the text is going to a file anyway (a statement being printed or emailed) streaming it with write() "
  "avoids holding the 3 MB string at all and has the lowest memory use.")
doc.add_page_break()

# =============================================================== Q5
H("Q5 - Functions, Parameters and Scope (7 marks)")
H("5.1 Explanation of the bug", 2)
P("Principle: a default value is created ONCE, when the def statement runs, and stored in the function object (add_item_buggy.__defaults__). "
  "With order=[] the same list object is used by every call that does not pass its own list. append() changes that single list, so items of the previous customer are still there for the next one. "
  "The run printed ['Tea', 'Vada'] ['Tea', 'Vada'] (both calls returned the same list) and add_item_buggy.__defaults__ ended as ([...all items...],) - the 'default' itself had been modified. "
  "In the corrected function the default is the immutable None; a NEW empty list is created inside the function body each time it is needed.")
CODE("def add_item(item, order=None):          # TODO 1\n    if order is None:\n        order = []\n    order.append(item)\n    return order")
H("5.2 Design questions", 2)
B([("Positional / keyword / default parameters: ", "positional for the obvious, required values in natural order (item); keyword when a call has several optional values or flags so the call documents itself "
    "(quantity=2, gst_rate=0.12); default values for optional parameters with a sensible standard (gst_rate=0.05) - never a mutable object as default."),
   ("Returning more than one value: ", "return total, gst returns a tuple that the caller unpacks (total, gst = price_with_gst('Dosa', 2) gave total=80, gst=4.0)."),
   ("local, global, nonlocal: ", "a name assigned inside a function is local to it (x in local_demo is not visible outside); global rebinds a module-level name; nonlocal rebinds a variable of the enclosing function (the closure counter returned 1, 2, 3 while a second counter started again at 1)."),
   ("Why changing a global needs the global keyword, and why it is avoided: ", "an assignment inside a function creates a local name, so bill_count += 1 without global raises UnboundLocalError (shown in the output). "
    "Globals are avoided because any function can change them (hidden coupling), the result of a call then depends on earlier calls, the function cannot be tested alone and it is not thread-safe; "
    "passing values in and returning results, or keeping state in a closure/class, is clearer.")])
H("5.3 Test with three customers in sequence", 2)
P("Arun ['Tea','Vada'], Bala ['Dosa'], Chitra ['Coffee','Vada','Tea'] - with the corrected function each order contains only that customer's items (independent). "
  "With the buggy function the same sequence produced Chitra's order = ['Tea','Vada','Tea','Vada','Dosa','Coffee','Vada','Tea'] (everything ever ordered).")
OUT("Task05", "Console output")
H("5.4 Alternative concepts and complexity", 2)
CODE("def new_order():                       # closure: one function (and one list) per customer\n    order = []\n    def add(item):\n        order.append(item); return order\n    return add\n\n"
     "def add_item_explicit(item, order):    # caller always passes the list\n    order.append(item); return order")
TABLE([["Design", "Time per item", "Space per customer", "Remarks"],
       ["default None + new list", "O(1) amortised", "O(m) for m items", "Simple; the caller keeps the returned list"],
       ["explicit list from caller", "O(1) amortised", "O(m)", "No hidden state; caller must remember to create a list"],
       ["closure (new_order)", "O(1) amortised", "O(m) + one function object and one cell (a constant)", "State is encapsulated; no way to forget the list; add() cannot be reused for another customer by mistake"]],
      widths=[1.7, 1.2, 1.7, 2.3], size=8.5)
P("Appending to a list is amortised O(1) in every design; storage for the items is the same O(m) - only the closure adds a small constant overhead.")
doc.add_page_break()

# =============================================================== Q6
r6 = J("Task06")
H("Q6 - Recursion and Its Limits (8 marks)")
H("6.1 Recursive design", 2)
P("Base case: ways(0) = ways(1) = 1 (one way to stand still, one way to climb one step). Recursive case: the last move is 1 step or 2 steps, so ways(n) = ways(n-1) + ways(n-2).")
CODE("def ways_naive(n):                       @lru_cache(maxsize=None)\n    global calls                          def ways_memo(n):                 # TODO 1\n    calls += 1                                global calls\n"
     "    if n <= 1: return 1                       calls += 1\n    return ways_naive(n-1) + ways_naive(n-2)      if n <= 1: return 1\n                                              return ways_memo(n-1) + ways_memo(n-2)")
H("6.2 Correctness check n = 1 to 6", 2)
TABLE([["n", "1", "2", "3", "4", "5", "6"], ["Manual (listing 1/2-step sequences)", "1", "2", "3", "5", "8", "13"],
       ["Program (naive = memo = loop)", "1", "2", "3", "5", "8", "13"]], widths=[2.4, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7])
P("Manual check for n = 4: 1111, 112, 121, 211, 22 = 5 ways. The three programs agree with the manual values for every n.")
H("6.3 Call tree for n = 5 and why the plain version repeats work", 2)
CODE("ways(5)\n  ways(4)\n    ways(3)\n      ways(2)\n        ways(1)\n        ways(0)\n      ways(1)\n    ways(2)\n      ways(1)\n      ways(0)\n  ways(3)\n    ways(2)\n      ways(1)\n      ways(0)\n    ways(1)", size=8)
P(f"The tree has {r6['tree_calls_n5']} calls although only 6 different values (0..5) are needed: ways(3) is computed twice, ways(2) three times, ways(1) five times. "
  "Each call recomputes subtrees that an earlier call already finished. Memoisation (a dictionary or lru_cache) stores the result of ways(k) the first time; "
  "every later request for k returns the stored value immediately, so the function body runs once per distinct n (n + 1 times).")
H("6.4 Growth investigation - predictions and observations", 2)
P("Prediction: every call of the plain version is either a leaf (returns 1) or has two children, so calls = 2*ways(n) - 1; the memoised version executes its body once for each of 0..n, i.e. n + 1 times.")
rows = [["n", "ways(n)", "Predicted naive calls", "Observed naive calls", "Naive time (s)", "Predicted memo calls", "Observed memo calls", "Memo time (s)"]]
for g in r6["growth"]:
    rows.append([g["n"], f"{g['ways']:,}", f"{2*g['ways']-1:,}", f"{g['naive_calls']:,}", f"{g['naive_time']:.5f}", g["n"] + 1, g["memo_calls"], f"{g['memo_time']:.6f}"])
TABLE(rows, widths=[0.4, 0.9, 1.1, 1.1, 0.8, 0.9, 0.9, 0.8], size=8)
P("All observed counts equal the predictions. From n = 25 to n = 30 the calls grew 11.09 times, equal to 1.618^5 (the golden ratio): exponential growth. The memoised version grows linearly.")
IMG("Task06/calls_growth.png", 5.2, "Calls versus n (log scale)")
H("6.5 Deployment decision - n = 1,000", 2)
P(f"sys.getrecursionlimit() = 1000. ways_memo(1000) needs about 1000 nested calls (plus the frames of the caller) so Python raises RecursionError: {r6['memo_1000_default']}. "
  "The limit exists to stop runaway recursion from overflowing the C stack.")
B([("Raise the limit: ", f"sys.setrecursionlimit(5000) lets memo(1000) finish (calls = {r6['memo_1000_calls']}, {r6['memo_1000_ms']:.3f} ms) - but it is only a patch: each frame uses real stack memory, and the limit cannot be raised forever. "
    f"My test with n = 1,000,000 and limit 10**7 ended with: {r6['crash_test']['message']} (on some builds or platforms this crashes the interpreter instead)."),
   ("Rewrite with a loop: ", f"no recursion depth, O(1) auxiliary space, {r6['loop_1000_ms']:.3f} ms for n = 1000; the answer has {r6['digits_1000']} digits and equals the memoised result (checked: {r6['memo_eq_loop']})."),
   ("Both: ", "keep the memoised recursion only as an independent cross-check for small n.")])
P("Decision: deploy the loop version. The trust needs the values for up to 1,000 steps; one pass of the loop even produces all 1,000 values (ways(1) ... ways(1000)) in O(1000) time without touching the recursion limit. "
  "The memoised recursive version is kept in the test file as a second, independent implementation to verify the loop (both agree for n = 1 ... 1000). "
  f"The plain recursion is impossible at this size: about 10^{r6['naive_1000_log10_calls']:.0f} calls, which at the measured {r6['calls_per_second']:,.0f} calls per second is about 10^{r6['naive_1000_log10_seconds']:.0f} seconds (the universe is about 4 x 10^17 s old), so it was not executed.")
OUT("Task06", "Console output")
H("6.6 Alternative concept - loop keeping the last two values, and complexity", 2)
CODE("def ways_loop(n):\n    prev, cur = 1, 1\n    for _ in range(2, n + 1):\n        prev, cur = cur, prev + cur\n    return cur")
TABLE([["Approach", "Time", "Space"],
       ["Plain recursion", "O(phi^n), phi = 1.618 (about 2^(0.69 n))", "O(n) stack depth"],
       ["Memoisation", "O(n) additions", "O(n) cache + O(n) stack"],
       ["Loop (last two values)", "O(n) additions", "O(1) auxiliary space"]], widths=[2.0, 2.6, 2.2])
P("(Counting each addition as one step. Because the answers are huge integers, one addition of the largest numbers costs O(n) bit operations, so in bit operations the memo and loop versions are O(n^2) - the ranking of the three approaches does not change.)")
doc.add_page_break()

# =============================================================== Q7
r7 = J("Task07")
d = r7["diagnose"]
rows7 = r7["rows"]
H("Q7 - Day-4 Design Challenge: Diagnose, Redesign and Validate (13 marks)")
P("Selected program: the plain recursive ways_naive(n) of Q6 - the program that fails when the input size grows (n = 35 already needs about 30 million calls). "
  "The redesign is written by hand; no built-in shortcut (lru_cache, a closed formula library call, etc.) is used to replace the algorithm.", bold=True)
H("A. Diagnose the bottleneck (2 marks)", 2)
P(f"Evidence from instrumenting the original program for n = 25 (Task07/design_challenge.py): {d['total']:,} calls, but only {d['distinct']} distinct arguments (0..25).")
c = d["counts"]
TABLE([["Argument k", "25", "20", "15", "10", "5", "2", "1", "0"],
       ["Times ways(k) was computed", c["25"], c["20"], c["15"], c["10"], f"{c['5']:,}", f"{c['2']:,}", f"{c['1']:,}", f"{c['0']:,}"]], widths=[1.9, 0.6, 0.6, 0.6, 0.6, 0.7, 0.7, 0.7, 0.7], size=8.5)
B([("Where most of the work is done: ", "in the leaves. The calls ways(1) and ways(0) alone make 50% of all calls; the small arguments are recomputed tens of thousands of times."),
   ("Which count grows with the input: ", "the number of calls: 177 (n=10), 21,891 (n=20), 242,785 (n=25), 2,692,537 (n=30) - multiplied by 1.618 for every extra step (exponential)."),
   ("Unnecessarily repeated work: ", f"yes - {d['wasted_pct']:.3f}% of the calls only recompute a value that was already computed; the result for k depends only on k, so the repetition is pure waste.")])
H("B. Design objective (2 marks)", 2)
P("For n = 30 reduce the work from 2,692,537 calls to at most n + 1 = 31 operations, make the execution time at least 1,000 times shorter, and make n = 1,000 computable without any RecursionError. "
  "(The objective follows from the diagnosis: exponential count of calls, repeated computation, recursion depth.)")
H("C. Design the revised solution (4 marks)", 2)
B([("What I changed: ", "the recursion is replaced by a bottom-up loop that computes ways(2), ways(3), ... ways(n) in increasing order and keeps only the last two values."),
   ("Property exploited: ", "overlapping subproblems (the same ways(k) is needed many times) together with the fact that ways(k) depends only on ways(k-1) and ways(k-2); therefore every value is needed only until the next two have been computed."),
   ("Extra memory: ", f"none beyond two variables (O(1) auxiliary space). A memo dictionary would need O(n); the measured peak for n = 20,000 was {r7['mem']['redesign (two values)']/1024:.0f} KiB for the two-variable loop against {r7['mem']['table of all values']/1024:,.0f} KiB when all values are stored."),
   ("New trade-offs: ", "the code no longer mirrors the mathematical definition word for word; intermediate values are lost (a table version is needed if all values must be printed); "
    f"for large n the numbers are huge integers, so one addition is no longer O(1) in bit operations (time grows from {r7['big']['1000']['time']:.5f} s for n = 1,000 to {r7['big']['100000']['time']:.3f} s for n = 100,000 - still small).")])
CODE("PSEUDOCODE\n  prev <- 1                 # ways(0)\n  cur  <- 1                 # ways(1)\n  FOR k FROM 2 TO n DO\n      next <- prev + cur    # ways(k)\n      prev <- cur\n      cur  <- next\n  END FOR\n  RETURN cur")
H("D. Prediction before implementing (1 mark)", 2)
P("Predicted: the number of operations falls from about 1.6^n to n: for n = 30 about 2.69 million / 29 = 90,000 times fewer; and the execution time falls by at least 1,000 times "
  "(an addition is far cheaper than a function call), with the gap widening for larger n. The measure in which I expect the improvement is the operation count (calls versus additions), followed by the time.")
H("E. Implement and validate (2 marks)", 2)
rows = [["n", "Answer", "Original calls", "Original time (s)", "Redesign additions", "Redesign time (s)", "Fewer operations", "Speed-up"]]
for x in rows7:
    rows.append([x["n"], f"{x['answer']:,}", f"{x['orig_calls']:,}", f"{x['orig_time']:.6f}", x["new_adds"], f"{x['new_time']:.8f}", f"{x['ops_reduction']:,.0f}x", f"{x['speedup']:,.0f}x"])
TABLE(rows, widths=[0.4, 0.9, 1.0, 0.9, 0.8, 0.9, 0.9, 0.9], size=8)
P("Same inputs (n = 10, 20, 25, 30, 35) were used for both versions, the answers were identical for all of them (checked by assertions, also against a table version and a dictionary memo), and n = 0 and n = 1 both return 1. "
  "The redesign's time is the average of 20,000 repetitions; the original is a single run (it is too slow to repeat at n = 35).")
IMG("Task07/original_vs_redesign.png", 6.3, "Operation counts and execution times (log scale)")
b = r7["big"]
P(f"Beyond the original's reach: n = 1,000 takes {b['1000']['time']:.5f} s ({b['1000']['digits']} digits), n = 10,000 takes {b['10000']['time']:.5f} s and n = 100,000 takes {b['100000']['time']:.4f} s ({b['100000']['digits']:,} digits). "
  "The intermediate dictionary-memo design still fails at n = 1,500 with a RecursionError because it is still recursive - another reason for choosing the loop.")
OUT("Task07", "Console output")
H("F. Defend the final design (2 marks)", 2)
x30 = rows7[3]
B([("Objective achieved? ", f"Yes, all three parts. For n = 30 the operations fell from {x30['orig_calls']:,} to {x30['new_adds']} (target <= 31); time from {x30['orig_time']:.4f} s to {x30['new_time']*1e6:.2f} microseconds "
    f"({x30['speedup']:,.0f} times faster, target 1,000 times); n = 1,000 runs without a RecursionError."),
   ("Size of the improvement: ", f"{x30['ops_reduction']:,.0f} times fewer operations at n = 30 and {rows7[4]['ops_reduction']:,.0f} times at n = 35: the gain itself grows exponentially, because the original grows exponentially and the redesign linearly. "
    f"My prediction of about 90,000 times fewer operations for n = 30 was accurate ({x30['ops_reduction']:,.0f}). The time gain ({x30['speedup']:,.0f} times) was far larger than the 1,000 times predicted, because a function call costs much more than an addition in the loop."),
   ("New costs and trade-offs: ", "less direct correspondence to the definition (harder to see why it is correct), no stored table (all values would need a table), and for very large n the cost of adding huge integers dominates (O(n^2) bit operations)."),
   ("When the original is still preferable: ", f"for very small n (n = 10 takes {rows7[0]['orig_time']*1e6:.0f} microseconds), for teaching, and when the recurrence is not a simple two-term one and the clarity of the direct recursion matters more than speed; "
    "it also needs no extra variables. It should never be used for n above about 35 in production.")])
P("Conclusion: the redesign meets the measurable objective with a large margin; the original is a correct but exponential algorithm whose only strength is readability.")
doc.add_page_break()

# =============================================================== Appendix A
H("Appendix A - Source code of all programs")
for task, prog in (("Task01", "subsidy.py"), ("Task02", "otp_kiosk.py"), ("Task03", "vehicle_validator.py"), ("Task04", "string_building.py"),
                   ("Task05", "canteen_orders.py"), ("Task06", "temple_steps.py"), ("Task07", "design_challenge.py")):
    H(f"{task}/{prog}", 3)
    CODE(open(f"{task}/{prog}").read(), size=6.5)
H("Appendix B - Evidence and reproduction", 1)
B([f"Measurements were made on: {MACHINE}. Execution times vary from computer to computer; operation counts and function calls do not.",
   "Raw data: every task folder contains results.json (operation counts, call counts and timings), output.txt and an output screenshot.",
   "To reproduce: pip install -r requirements.txt; python run_all.py --report"])
doc.save("Assignment2_Report.docx")
print("saved Assignment2_Report.docx")
