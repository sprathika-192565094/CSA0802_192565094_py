"""Builds Assignment4_Report.docx from the programs, their output.txt files and results.json.
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
REPO = "https://github.com/<your-username>/CSA08-<RegisterNumber>-Assignment4"
MACHINE = f"Python {platform.python_version()} on {platform.system()} {platform.machine()}"


def J(path):
    return json.load(open(path))


def OUTF(task, prog, caption, img=True):
    """Console output of task/prog as copyable text and as a screenshot-style image."""
    P(caption, bold=True)
    CODE(open(f"{task}/output_{prog}.txt").read(), size=6.5)
    if img:
        import glob
        for p in sorted(glob.glob(f"{task}/screenshot_{prog}*.png")):
            IMG(p, 6.4, f"Output screenshot - {task}/{prog}.py")


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


rA = J("TaskA/results.json")
rB1 = J("TaskB1/results.json")
rP = J("TaskB1/results_pandas.json")
rB2 = J("TaskB2/results.json")
rB3 = J("TaskB3/results.json")
rB4 = J("TaskB4/results.json")
rS = J("TaskB4/results_scale.json")

# =============================================================== title page
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("\n\nCSA08 - Python Programming\nAssignment 4 - City Air-Quality Monitoring Network")
r.bold = True
r.font.size = Pt(21)
TABLE([["Student name", NAME], ["Register number", REGNO], ["GitHub repository", REPO],
       ["Environment used for the measurements", MACHINE]], widths=[2.4, 4.3], header=False, size=11)
P("Part A - Data and Program Design (25 marks): A1 Data acquisition, A2 Cleaning and normalisation, A3 Analysis and visualisation, A4 Debugging and profiling plan, A5 AI application for citizen complaints.   "
  "Part B - Implementation and Experimental Investigation (25 marks): B1 Cleaning pipeline, B2 Adversarial data, B3 Loops vs libraries vs SQL, B4 Final engineering decision.   Appendix A: source code; Appendix B: reproduction.")
P("Workflow followed: Acquire - Inspect - Clean - Normalise - Store - Query - Visualise - Profile - Challenge - Interpret. "
  "Every number in this report comes from a program in the repository (results files and output files of each task folder); no number is typed in from memory.", italic=True)
P("Pseudocode conventions used in Part A: ALGORITHM name / INPUT / OUTPUT / BEGIN ... END; SET x TO ...; IF ... THEN ... ELSE ... END IF; FOR EACH item IN collection DO ... END FOR; WHILE ... DO ... END WHILE; RETURN. No Python syntax is used in the pseudocode.", italic=True)
doc.add_page_break()

# =============================================================== PART A
H("PART A - DATA AND PROGRAM DESIGN")
H("TASK A1 - Design the Data Acquisition (7 marks)", 1)
H("A1.1 Inspect the source (2 marks)", 2)
P("Structure of a station file. Each of the 12 stations sends one CSV file per day (named for example adyar_2026-10-01.csv, so the station is identified by the file name). The file is text, one header line and up to 24 data lines, one per hour: "
  "date, hour (0-23), pm25, pm10, no (all in micrograms per cubic metre) and temperature (degrees Celsius, but two stations report Fahrenheit). After reading, the program adds the station name so that all files can be combined into the table station, date, hour, pm25, pm10, no, temperature.")
TABLE([["#", "Data-quality problem expected", "Example (taken from the sample file used in B1)"],
       ["1", "Missing value: blank cell", "Adyar, 2026-10-01, hour 02, pm25 = (empty)"],
       ["2", "Missing value: marker text 'NA'", "Adyar, hour 01, pm25 = NA"],
       ["3", "Text where a number is expected (sensor error code)", "Manali, hour 01, pm25 = ERR"],
       ["4", "Negative value (sensor fault)", "Adyar, hour 03, pm25 = -5"],
       ["5", "Impossibly large value", "Adyar, hour 04, pm25 = 9999 (the limit is 999)"],
       ["6", "Duplicate rows (file sent twice, or a row repeated)", "Adyar hour 04 appears two times"],
       ["7", "Temperature in Fahrenheit", "Manali temperature 86.0 (= 30.0 C)"],
       ["8", "Different date formats", "Guindy writes 01/10/2026 (day first) while the others write 2026-10-01"],
       ["9", "Inconsistent station names", "' adyar ' (lower case, blanks) instead of 'Adyar'"],
       ["10", "Different hour formats", "'6' instead of '06'"],
       ["11", "Missing rows (an hour that never arrives), a file that does not arrive", "no line for hour 14 in a file"],
       ["12", "Damaged files (examined in B2)", "missing column, semicolon instead of comma, UTF-16 or Windows-1252 text, empty file"]],
      widths=[0.3, 3.0, 3.6], size=8.5)
H("A1.2 Design the storage (3 marks)", 2)
P("Two tables are used. Station facts (name, zone, the unit of its temperature) are stored once; each reading refers to its station by a number. This avoids repeating the name 8,760 times per station and avoids spelling differences.")
CODE("CREATE TABLE stations (\n    station_id INTEGER PRIMARY KEY,\n    name       TEXT NOT NULL UNIQUE,\n    zone       TEXT,\n    temp_unit  TEXT NOT NULL DEFAULT 'C' CHECK (temp_unit IN ('C', 'F'))\n);\n"
     "CREATE TABLE readings (\n    station_id INTEGER NOT NULL REFERENCES stations(station_id),\n    day        TEXT    NOT NULL,                 -- ISO date yyyy-mm-dd\n    hour       INTEGER NOT NULL CHECK (hour BETWEEN 0 AND 23),\n"
     "    pm25 REAL CHECK (pm25 IS NULL OR pm25 BETWEEN 0 AND 999),\n    pm10 REAL, no REAL,\n    temp_c REAL,                                 -- always Celsius after cleaning\n    PRIMARY KEY (station_id, day, hour)\n) WITHOUT ROWID;", size=7.5)
TABLE([["CSV column / source", "Table.column", "Type", "Transformation"],
       ["file name (station)", "stations.name -> readings.station_id", "TEXT -> INTEGER", "name normalised (trim, Title Case), looked up in stations"],
       ["date", "readings.day", "TEXT", "rewritten to ISO yyyy-mm-dd"],
       ["hour", "readings.hour", "INTEGER", "'6' -> 6, must be 0-23"],
       ["pm25, pm10, no", "readings.pm25, pm10, no", "REAL", "text -> number; invalid -> NULL"],
       ["temperature", "readings.temp_c", "REAL", "Fahrenheit stations converted to Celsius"]], widths=[1.6, 2.2, 1.1, 2.0], size=8.5)
P("Primary key (station_id, day, hour): a second row for the same hour of the same station cannot be stored, which makes duplicates impossible; the key also stores the rows in the order station-day-hour, so a question about one station and a range of days reads one contiguous block. "
  "Missing readings are stored as NULL (never as 0 or -999), because AVG, MIN, MAX and COUNT in SQL ignore NULL automatically. The CHECK constraints are the last line of defence if the cleaning code has a fault.")
H("A1.3 CSV or SQL? (2 marks)", 2)
tq = rB1["csv_vs_sql"]
TABLE([["Question of the board", "From CSV files", "With SQL"],
       ["Q1 Average PM2.5 of Adyar in October", "read every line of every file, test the station, add up: O(n)", "WHERE name = ? AND day BETWEEN ...: the primary key finds the block: O(log n + k) for k rows of that station-month"],
       ["Q2 Stations with the highest mean PM2.5", "read every line, keep sum and count per station: O(n)", "GROUP BY station + ORDER BY: still reads all rows O(n), faster constant, or O(stations x days) on a daily summary table"],
       ["Q3 Hours with the worst air", "read every line, sum per hour: O(n)", "GROUP BY hour: O(n); on a summary table much less"]], widths=[1.8, 2.4, 2.8], size=8.5)
P(f"Measured on one month of 12 stations (8,928 cleaned rows): the CSV program needs {tq['t_csv']*1000:.1f} ms for all three answers together (it reads the file once); SQL answers Q1 in {tq['t_q1']*1000:.2f} ms, Q2 in {tq['t_q2']*1000:.2f} ms and Q3 in {tq['t_q3']*1000:.2f} ms. "
  f"Both give identical answers ({tq['same']}). At the larger scale of B4 (1.29 million rows) a one-station query takes {rS['before']['A  average of one station in one month']*1000:.1f} ms when the whole table must be scanned and {rS['after']['A  average of one station in one month']*1000:.2f} ms with an index. "
  "SQL also gives, without extra programming, constraints, joins, concurrent readers and no need to re-parse text for every question. The CSV files are still kept as the original record (acquire once, never edit).")
H("Alternative concept and complexity analysis - pandas DataFrame for every question", 3)
p1, p3 = rP["rows"][1], rP["rows"][2]
P("Solution: for every question read_csv() the files into a DataFrame, filter with a boolean mask and use groupby(). "
  f"Time per question: reading and parsing is a full scan, O(n), every time (the cleaning pipeline in pandas needed {p3['pandas']['seconds']:.1f} s for 1,000,000 rows); an indexed SQL query is about O(log n + k) - in the B4 experiment {rS['before']['A  average of one station in one month']/rS['after']['A  average of one station in one month']:.0f} times faster than a scan at 1.29 million rows. "
  f"Space: the DataFrame lives in memory, O(n) (peak {p3['pandas']['peak_mb']:.0f} MB for 1,000,000 rows including the file parsing) while the SQLite database stays on disk ({rS['size_before']:.0f} MB for 1.29 million rows without index) and loads only the pages a query needs. "
  "pandas is excellent for one-off analysis; for a board that asks questions every day the stored, indexed database avoids paying the full read cost again.")

H("TASK A2 - Design the Cleaning and Normalisation (5 marks)", 1)
H("A2.1 Cleaning rules (2 marks)", 2)
TABLE([["Problem", "Rule", "Justification"],
       ["Missing (blank, NA, ERR, other text)", "Treat as missing (NULL). Forward-fill from the previous valid value of the same station for at most 3 consecutive hours; longer gaps stay NULL and are not averaged (counted in n_valid).",
        "Pollution changes slowly from hour to hour, so the last value is a reasonable estimate for a short gap; a long gap must not be invented. Median fill is rejected as the default and dropping is only safe when the gaps are random (see experiment below)."],
       ["Impossible values (PM2.5 < 0 or > 999, PM10 > 1999, NO > 999, temperature outside -10 to 60 C)", "Replace by missing (NULL), then apply the missing-value rule.",
        "A faulty sensor value carries no information; clipping to the limit would invent a value. The ranges are physical limits of the instruments, not statistical outlier rules, so real pollution peaks are kept."],
       ["Duplicate rows", "Key = (station, date, hour); keep the first, count and log the rest.", "A resent file repeats identical rows; counting them twice would bias averages."],
       ["Fahrenheit temperatures", "For stations whose temp_unit is 'F': C = (F - 32) x 5/9, BEFORE the range check.", "The unit is a property of the station (stored in the stations table), not guessed from the value; converting first prevents 86 F being rejected as 'above 60'."]],
      widths=[1.5, 2.6, 2.9], size=8.5)
CODE("ALGORITHM CleanReadings\nINPUT  raw rows (station, date, hour, pm25, pm10, no, temperature) as text; list of Fahrenheit stations; valid range of each column\nOUTPUT clean rows, counts of every correction\nBEGIN\n    SET seen TO an empty dictionary keyed by (station, date, hour)\n"
     "    FOR EACH raw row DO\n        SET station TO canonical name of the station; SET date TO ISO form of the date; SET hour TO the integer value of the hour\n        IF date or hour cannot be read THEN count the row as rejected; CONTINUE with the next row END IF\n"
     "        IF (station, date, hour) IS IN seen THEN add 1 to the duplicate counter; CONTINUE with the next row END IF\n        FOR EACH column IN (pm25, pm10, no, temperature) DO\n            SET value TO the number in the text, or MISSING if the text is blank, NA or not a number\n"
     "            IF column IS temperature AND station IS Fahrenheit AND value IS NOT MISSING THEN SET value TO (value - 32) * 5 / 9 END IF\n            IF value IS OUTSIDE the valid range of the column THEN SET value TO MISSING END IF\n        END FOR\n        STORE the values in seen at (station, date, hour)\n    END FOR\n"
     "    SORT seen BY station, date, hour\n    FOR EACH column AND EACH station DO\n        SET gap TO 0\n        FOR EACH row of the station IN ORDER DO\n            IF value IS MISSING THEN add 1 to gap; IF gap <= 3 AND a previous valid value exists THEN SET value TO the previous valid value END IF\n"
     "            ELSE SET previous valid value TO value; SET gap TO 0 END IF\n        END FOR\n    END FOR\n    RETURN the rows of seen and the counters\nEND", size=7.5)
H("A2.2 Normalisation (2 marks)", 2)
CODE("ALGORITHM MinMax                                   ALGORITHM ZScore\nINPUT  list of PM2.5 values                        INPUT  list of PM2.5 values\nOUTPUT list of values between 0 and 1              OUTPUT list of standardised values\nBEGIN                                              BEGIN\n    SET low TO the smallest value                      SET m TO the mean of the values\n    SET high TO the largest value                      SET s TO the population standard deviation\n    IF high = low THEN RETURN a list of zeros          IF s = 0 THEN RETURN a list of zeros\n    FOR EACH v DO v' = (v - low) / (high - low)        FOR EACH v DO v' = (v - m) / s\n    RETURN the new list                                RETURN the new list\nEND                                                END", size=7.5)
n_ = rA["norm"]
P(f"Example with 8 readings [42, 55, 61, 48, 70, 66, 52, 58]: min-max gives {n_['minmax']}; z-score gives {n_['z']}. Adding one valid but extreme reading of 450 changes min-max to {n_['minmax_spike']} - the eight normal readings are squeezed between 0.015 and 0.069 - whereas z-score still shows the normal readings at about -0.2 to -0.5 and the spike at {n_['z_spike'][-1]}.")
B([("Min-max is appropriate ", "when a bounded scale 0-1 is needed (colour scales, a chart that compares several pollutants on one axis, inputs of algorithms that need bounded values) and when the data have no extreme values, because the extremes define the scale."),
   ("Z-score is appropriate ", "when stations with different levels must be compared by how unusual a reading is (a value above +3 is a candidate outlier), when the data have outliers, or when the method assumes centred data. It has no fixed range."),
   ("Both ", "need a guard against a constant series (division by zero) - the implementation returns zeros - and the minimum, maximum, mean and standard deviation must be computed from the CLEANED training period and reused, not recomputed on each new day.")])
H("A2.3 Formatting (1 mark)", 2)
TABLE([["Item", "Standard format"],
       ["Date", "ISO 8601 text yyyy-mm-dd (2026-10-01); dd/mm/yyyy and dd-mm-yyyy are accepted on input (day first) and rewritten"],
       ["Hour", "integer 0-23 in local time (IST), never text"],
       ["Station name", "the canonical name stored in the stations table (Title Case, single spaces: 'Anna Nagar', 'T. Nagar'); matching ignores case and extra blanks"],
       ["Numbers", "decimal point (not comma), one decimal place, no units in the cell; PM2.5, PM10 and NO in micrograms per cubic metre; temperature in degrees Celsius"],
       ["Missing value", "NULL in the database, empty cell in CSV; never 0, -1 or 9999"],
       ["Files", "UTF-8 text, comma delimiter, one header line"]], widths=[1.4, 5.6], size=8.5)
H("Alternative concept and complexity analysis - drop the missing readings instead of filling them", 3)
P("Solution: remove every row with a missing PM2.5 and average what remains. Experiment (TaskA/partA_experiments.py): one month of true hourly values of 12 stations was damaged in two ways and the daily means were recomputed with each method; the error is the difference to the true daily mean.")
rows = [["Scenario", "Method", "Mean absolute error (ug/m3)", "Bias (ug/m3)"]]
for x in rA["missing"]:
    rows.append([x["scenario"], x["method"], f"{x['mae']:.2f}", f"{x['bias']:+.2f}"])
TABLE(rows, widths=[2.9, 1.2, 1.6, 1.3], size=8.5)
P("When readings are missing at random, dropping is almost as good as forward fill (the mean is unbiased). When the missing readings are concentrated in the peak hours - which is what happens when a sensor fails under load - dropping makes every daily mean too low (bias -1.12) because the highest values disappear, forward fill reduces the error to about half, and median fill is the worst in both cases because it replaces peaks by an ordinary value. "
  "This is why the design fills short gaps and keeps n_valid so that a day with many missing hours can be flagged.")
rows = [["Values", "Drop O(n)", "Forward fill O(n)", "Median fill O(n log n)", "Peak memory drop / ffill / median"]]
for x in rA["missing_cost"]:
    rows.append([f"{x['n']:,}", f"{x['drop']['t']:.4f} s", f"{x['ffill']['t']:.4f} s", f"{x['median']['t']:.4f} s", f"{x['drop']['mb']:.1f} / {x['ffill']['mb']:.1f} / {x['median']['mb']:.1f} MB"])
TABLE(rows, widths=[1.0, 1.1, 1.3, 1.5, 2.1], size=8.5)
mc = rA["missing_cost"]
P(f"Dropping and forward fill are both one pass (O(n)); the median needs a sort (O(n log n)) and was {mc[1]['median']['t']/mc[1]['drop']['t']:.0f} to {mc[2]['median']['t']/mc[2]['drop']['t']:.0f} times slower than dropping at 100,000 to 1,000,000 values and {mc[2]['median']['t']/mc[2]['ffill']['t']:.1f} times slower than forward fill at 1,000,000.  Space: dropping builds a shorter list ({mc[2]['drop']['mb']:.1f} MB per million values); forward fill and median fill build a full-length new list ({mc[2]['ffill']['mb']:.0f} MB per million values). The costs are small compared with reading the file, so the accuracy of the daily mean decides the choice.")

H("TASK A3 - Design the Analysis and Visualisation (5 marks)", 1)
H("A3.1 Choose the charts (3 marks)", 2)
TABLE([["Question of the board", "Chart", "Justification"],
       ["Trend of PM2.5 over a month", "Line chart of the daily mean (x = day, y = ug/m3) with the 60 ug/m3 daily standard as a reference line", "Time is ordered and continuous, the eye follows the slope; markers show single days; the reference line shows which days break the limit."],
       ["Comparison of stations", "Box plot, one box per station (y = hourly PM2.5)", "Shows the median, the spread and outliers of 12 groups at once; a bar of the mean would hide the spread and the extreme hours."],
       ["Relationship between temperature and PM2.5", "Scatter plot (x = temperature, y = PM2.5) with the correlation coefficient in the title", "Both variables are numeric and measured at the same time; a scatter shows the shape, the strength and any outliers; correlation r summarises it."],
       ["Hours with the worst air", "Bar chart of the mean PM2.5 for each hour 0-23 with the worst three hours highlighted", "24 categories on a cycle; bar heights are compared by length; a histogram would show the distribution of values, not the hour."]],
      widths=[1.7, 2.3, 3.0], size=8.5)
P("All charts have a title, labelled axes with units and a legend where needed. A histogram of PM2.5 and a heat map (hour x day) were considered; they are useful extensions but do not answer the four questions directly.")
H("A3.2 Design the summary table (2 marks)", 2)
P("Table daily_summary(station_id, day, min_pm25, max_pm25, mean_pm25, n_valid) with one row per station and day (primary key station_id + day). It is produced by one query that is run after each daily load (for the new day only):")
CODE("ALGORITHM BuildDailySummary\nINPUT  table readings   OUTPUT table daily_summary\nBEGIN\n    FOR EACH group of readings WITH THE SAME station_id AND day DO\n        SET min TO the smallest pm25 that is not missing; SET max TO the largest pm25 that is not missing\n        SET mean TO the average of the pm25 values that are not missing\n        SET n_valid TO the number of pm25 values that are not missing\n        STORE one row (station_id, day, min, max, mean, n_valid)\n    END FOR\nEND\n"
     "(in SQL: SELECT station_id, day, MIN(pm25), MAX(pm25), AVG(pm25), COUNT(pm25) FROM readings GROUP BY station_id, day)", size=7.5)
P("MIN, MAX and AVG ignore NULL, and COUNT(pm25) counts only the valid readings, so n_valid tells the reader how much evidence stands behind each mean (24 means a complete day). The result is demonstrated in B1.")
H("Alternative concept and complexity analysis - daily summary in Python loops after reading all rows", 3)
s3 = rB3["sizes"]
P(f"Solution: read all rows with the csv module, collect the readings of every (station, day) in a dictionary of lists, then compute min, max, mean and count with Python functions. Time: O(n) for both approaches (every row is read once). Measured for the daily mean at 1,051,200 rows (120 stations x one year): loops {s3[2]['loops']:.2f} s; SQL GROUP BY {s3[2]['sql_query']:.2f} s once the data are in the database ({s3[2]['sql_load']:.2f} s to load them). "
  f"Memory: the loop approach keeps every reading (O(n): peak {rB3['mem']['store all readings, then statistics.mean']/1e6:.1f} MB for 105,120 rows); the database does the grouping inside the engine with memory O(groups) and the data stay on disk. "
  "With a running sum and count per group (see B3) the loop version needs only O(stations x days) memory.")

H("TASK A4 - Plan Debugging and Profiling (4 marks)", 1)
H("A4.1 Debugging plan (2 marks)", 2)
TABLE([["Tool", "Use in the cleaning code", "When"],
       ["print", "show 5 rows before and after one rule on the small sample file (for example the Fahrenheit rows)", "first quick look, removed afterwards"],
       ["assert", "state facts that must always be true: assert len(clean) <= len(raw); every pm25 is None or between 0 and 999; no (station, date, hour) key twice; counted corrections add up", "permanent checks in the code, cheap, removed in production with python -O"],
       ["logging", "logging.getLogger('aq'); DEBUG: why a value was changed; INFO: counts per file; WARNING: a file or row rejected; ERROR: failure; written to a file with time stamps", "permanent; the level is changed by configuration, not by editing code"],
       ["pdb / IDE debugger", "python -m pdb or breakpoint() placed where an assertion failed; commands: n (next), s (step into), p variable, l (list), b line (breakpoint), c (continue), w (stack)", "when the cause is still unknown after logging"]], widths=[1.1, 4.0, 1.9], size=8.5)
P("Procedure: (1) reproduce the fault on the smallest file that shows it (the 12-row sample of B1); (2) add an assert for the expected fact - the first failing assert narrows the fault to one stage; (3) log the inputs and decisions of that stage at DEBUG level; (4) if the reason is still unclear, stop at the failing row in the debugger and inspect the variables; "
  "(5) fix the cause, keep the failing row as a permanent test row, rerun all asserts.")
H("A4.2 Profiling plan (2 marks)", 2)
B(["time.perf_counter() around each stage (read, clean, store, query, chart) to see which stage dominates and to compare the three data sizes against a time budget.",
   "timeit for micro-decisions (for example two ways to parse a number or to normalise the station name), run many times so that noise is small.",
   "cProfile on the whole pipeline at the 12-station size, sorted by tottime (time inside a function) and cumtime (including callees); the top function is examined first and only that is optimised. The result is shown in B3.3.",
   "Repeat the profile after each change and keep the numbers in the report to prove that the change helped."])
H("Alternative concept and complexity analysis - print statements for all debugging", 3)
d_ = rA["debug_cost"]["rows"][-1]
P(f"Solution: a print() at every decision. Measured cost of one call (output to a null device, 100,000 calls): print {d_['print']:.2f} microseconds, logging with DEBUG enabled {d_['log_on']:.2f} microseconds, logging with the level set to WARNING (calls disabled) {d_['log_off']:.2f} microseconds, "
  f"print behind 'if DEBUG:' {d_['guard']:.3f} microseconds, assert {d_['assert_']:.3f} microseconds; the empty loop costs {d_['none']:.3f}. "
  f"For 100,000 readings that is about {d_['print']*0.1:.0f} ms of printing and about {d_['log_on']*0.1:.0f} ms of enabled logging (both O(number of calls)); a real terminal or file is slower than the null device. Space is O(1) for both.")
TABLE([["Approach", "How it is switched off when the program is finished"],
       ["print", "the calls must be deleted or commented out by hand (easy to miss one) or wrapped in 'if DEBUG:' (still costs the test)"],
       ["logging", "logging.getLogger('aq').setLevel(logging.WARNING) or logging.disable(logging.CRITICAL): no code change; disabled calls cost only about 0.1 microsecond"],
       ["assert", "run python -O: all assert statements are removed completely (1,000,000 asserts: " + f"{rA['debug_cost']['assert_normal_ms']:.0f} ms normal, {rA['debug_cost']['assert_O_ms']:.0f} ms with -O)"],
       ["pdb / breakpoint()", "set the environment variable PYTHONBREAKPOINT=0 and breakpoint() does nothing"]], widths=[1.5, 5.5], size=8.5)

H("TASK A5 - Design an AI Application for Citizen Complaints (4 marks)", 1)
H("A5.1 Sentiment scorer and summariser (2 marks)", 2)
CODE("ALGORITHM SentimentScore\nINPUT  text, sets POSITIVE, NEGATIVE, NEGATORS      OUTPUT total score (> 0 positive, < 0 negative, 0 neutral)\nBEGIN\n    SET words TO the lower-case words of text with punctuation removed\n    SET total TO 0\n    FOR EACH position i IN words DO\n"
     "        SET value TO +1 IF words[i] IS IN POSITIVE, -1 IF words[i] IS IN NEGATIVE, otherwise 0\n        IF value <> 0 AND i > 1 AND words[i-1] IS IN NEGATORS THEN SET value TO -value END IF\n        ADD value TO total\n    END FOR\n    RETURN total\nEND", size=7.5)
CODE("ALGORITHM ExtractiveSummary\nINPUT  complaint text, set STOPWORDS, number k      OUTPUT the k most important sentences in their original order\nBEGIN\n    SET sentences TO the text split at '.', '!' and '?'\n    SET frequency TO a dictionary: each important word (not in STOPWORDS) -> number of times it occurs in the complaint\n"
     "    FOR EACH sentence DO SET score[sentence] TO the sum of frequency[word] over its important words END FOR\n    SET best TO the k sentences with the highest score (the earlier sentence wins a tie)\n    RETURN best sorted by their position in the text\nEND", size=7.5)
P("Negation is handled by flipping the value of a sentiment word whose previous word is a negator (not good = negative, not bad = positive). Known weaknesses (examined in B2): negators that are not adjacent, double negatives, sarcasm, words that are not in the list, contractions such as isn't, and punctuation attached to a word.")
H("A5.2 Basic chatbot (2 marks)", 2)
CODE("ALGORITHM AnswerQuestion\nINPUT  question text, database of readings\nOUTPUT answer text\nBEGIN\n    SET words TO the lower-case words of the question\n    SET station TO the station name from the database whose name occurs in the question, or NONE\n"
     "    SET pollutant TO 'pm25' IF 'pm2.5' or 'pm25' occurs, 'pm10' IF 'pm10' occurs, 'no' IF 'no' or 'nitric' occurs, otherwise 'pm25'\n    SET day TO today IF 'today' occurs, yesterday IF 'yesterday' occurs, otherwise today\n"
     "    IF none of the keywords air, pm2.5, pm10, quality, level occurs THEN RETURN the help message listing what can be asked END IF\n    IF station IS NONE THEN RETURN 'Which station? Choose one of ' followed by the list of stations END IF\n"
     "    SET value TO the result of a parameterised query: average of the pollutant for that station and day\n    IF value IS MISSING THEN RETURN 'No valid readings yet for ' station END IF\n    RETURN 'The average ' pollutant ' at ' station ' on ' day ' is ' value ' ug/m3 (' category ')'\nEND", size=7.5)
B(["Limitations: it understands only the keywords it knows (no synonyms such as 'dust', 'smog', or spelling mistakes and no Tamil or Hindi); station names that are parts of other names ('Nagar') are ambiguous; it has no memory of earlier questions ('and yesterday?'); ",
   "it answers only what is in the database (no forecast, no reasons, no health advice); a question with two stations or two pollutants gets one answer; sarcasm and negation in the question are ignored; the value shown depends on the data quality (n_valid should be reported).",
   "Safety: the station name and day are passed to SQL as parameters (? placeholders), never joined into the SQL text (see B2)."])
H("Alternative concept and complexity analysis - a trained model instead of the word list", 3)
nb = rB4["nb"]
P(f"Solution: turn each complaint into word counts (CountVectorizer) and train a Naive Bayes classifier on labelled complaints. In this assignment the model was trained on 3,000 synthetic labelled complaints (vocabulary of {nb['vocab']} words) and tested on my 54 real-style complaints (B4).")
TABLE([["", "Word-list scorer", "Naive Bayes model"],
       ["Time per complaint", f"{rB4['time']['score_us']:.1f} microseconds (O(words))", f"{nb['t_single_us']:.0f} microseconds one at a time; {nb['t_batch_us']:.1f} microseconds in a batch of 50,000 (O(words x classes))"],
       ["Memory", f"{nb['lex_kb']:.2f} KB (three word sets)", f"{nb['model_kb']:.1f} KB for this small model; real models with thousands of words and a pre-trained language model need megabytes to gigabytes"],
       ["Agreement with my reading", f"{rB4['sentiment']['agree']} of 54 ({rB4['sentiment']['agree']/54*100:.1f} %)", f"{nb['acc']} of 54 ({nb['acc']/54*100:.1f} %) - optimistic, the training data are synthetic"],
       ["Needs", "a human-written word list", "labelled training data (thousands of real complaints) and retraining when the language changes"]], widths=[1.5, 2.3, 3.2], size=8.5)
P("The model can learn words the list does not know (stench, terrible), so it is expected to be more accurate when real labelled data exist, but its accuracy here is not proof of that. Both approaches are O(words) per complaint; the difference is in the effort of preparing data and in explainability (the word list can be read and corrected by an officer).")
doc.add_page_break()
# =============================================================== PART B
H("PART B - IMPLEMENTATION AND EXPERIMENTAL INVESTIGATION")
H("TASK B1 - Implement and Validate the Cleaning Pipeline (7 marks)", 1)
H("Complete the Code (TaskB1/complete_code_b1.py)", 2)
CODE("def load_clean(text):\n    rows = []\n    for row in csv.DictReader(io.StringIO(text)):          # TODO 1\n        raw = row['pm25'].strip()\n        if raw == '' or raw.upper() == 'NA': continue\n        value = float(raw)\n        if value < 0 or value > 999: continue               # extra check: readings above 999 are skipped\n        rows.append((row['station'], row['date'], value))\n    return rows\n\n"
     "def min_max(values):                                       # TODO 2\n    lo, hi = min(values), max(values)\n    return [round((v - lo) / (hi - lo), 3) for v in values]", size=7.5)
OUTF("TaskB1", "complete_code_b1", "Console output - identical to the expected output of the question; the added test row 1500 is skipped and the boundary value 999 is kept")
H("B1.1 Validate the implementation on a small file containing every problem of A1.1 (2 marks)", 2)
sm = rB1["sample"]["stats"]
TABLE([["Problem of A1.1", "Rule applied", "Count in the 12-row sample"],
       ["Missing (blank, NA)", "missing -> forward fill (max 3 h)", sm["missing"]], ["Text (ERR)", "missing", sm["not_numeric"]], ["Negative value", "missing", sm["negative"]],
       ["Impossibly large value", "missing", sm["too_large"]], ["Duplicate row", "removed", sm["duplicates"]], ["Fahrenheit", "converted to Celsius", sm["fahrenheit"]],
       ["Date format dd/mm/yyyy", "rewritten to ISO", sm["dates_reformatted"]], ["Station name variants", "normalised", sm["names_fixed"]],
       ["Values forward-filled / still missing", "gap <= 3 h filled; longer left empty", f"{sm['filled']} / {sm['still_missing']}"]], widths=[2.6, 2.8, 1.6], size=8.5)
P("The before-and-after listing is in the console output below (12 rows received, 11 stored). Six automatic checks all passed: the duplicate is removed; 86.0 F becomes 30.0 C; the NA at Adyar hour 1 is replaced by the previous value 48.0; ' adyar ' becomes Adyar; the date 01/10/2026 becomes 2026-10-01; no stored value is outside its valid range. "
  "Adyar hour 4 stays empty on purpose: the hours 1, 2, 3 and 4 are four consecutive missing values and the rule fills at most three.")
mo = rB1["month"]
P(f"Full month (12 stations, 1-31 October): {mo['stats']['rows_in']:,} rows received, {mo['stats']['rows_out']:,} stored (12 x 31 x 24 = 8,928), cleaning time {mo['t_clean']:.3f} s. Corrections: {mo['stats']['missing']:,} missing, {mo['stats']['not_numeric']} text, {mo['stats']['negative']} negative, {mo['stats']['too_large']} too large, {mo['stats']['duplicates']} duplicates removed, "
  f"{mo['stats']['fahrenheit']:,} Fahrenheit values converted, {mo['stats']['dates_reformatted']} dates and {mo['stats']['names_fixed']} names normalised, {mo['stats']['filled']:,} values forward-filled. Because the data were generated, the true values are known: "
  f"{mo['equal']:,} of {mo['equal']+mo['filled_or_changed']:,} stored PM2.5 values equal the true value and the rest are filled values; the mean absolute error of all stored values is {mo['mae']:.2f} ug/m3.")
H("B1.2 Compare the code with the Part A design (1 mark)", 2)
B(["Same as the design: the order of the rules (names, dates, duplicates, numbers, conversion, range, fill), the limits, the keep-the-first duplicate rule, forward fill of at most 3 hours, NULL for missing.",
   "Change 1 - conversion before range check: in the first draft of the design the range test came first; the sample file showed that 86.0 F would be rejected as 'above 60'. The implementation converts first (the design in A2.1 was corrected to say so).",
   "Change 2 - a new rule 'text instead of a number' (ERR) with its own counter, because the file of one station contained such codes; parse_number returns a reason ('missing' or 'not a number') so that both are counted separately.",
   "Change 3 - rows whose date or hour cannot be read are rejected and counted (the design only said 'normalise the date'); a row without a date cannot be stored under the primary key.",
   "Change 4 - the fill counts gaps per column and per station, not per row, so a missing PM2.5 does not stop the temperature from being filled."])
H("B1.3 Store in SQLite and answer the three questions (2 marks)", 2)
sq = rB1["sql"]
CODE("con.executemany('INSERT OR REPLACE INTO readings VALUES (?, ?, ?, ?, ?, ?, ?)', rows)   # ONE call for all rows\n\n"
     "Q1  SELECT ROUND(AVG(r.pm25),2) FROM readings r JOIN stations s ON s.station_id = r.station_id\n    WHERE s.name = ? AND r.day BETWEEN '2026-10-01' AND '2026-10-31'\nQ2  SELECT s.name, ROUND(AVG(r.pm25),2) AS m FROM readings r JOIN stations s ON s.station_id = r.station_id GROUP BY s.name ORDER BY m DESC LIMIT 3\n"
     "Q3  SELECT hour, ROUND(AVG(pm25),2) AS m FROM readings GROUP BY hour ORDER BY m DESC LIMIT 3", size=7.5)
TABLE([["Question", "Answer from SQL", "Time"],
       ["Q1 average PM2.5 of Adyar in October", f"{sq['q1']} ug/m3", f"{tq['t_q1']*1000:.2f} ms"],
       ["Q2 three stations with the highest mean", ", ".join(f"{a} {b}" for a, b in sq["q2"]), f"{tq['t_q2']*1000:.2f} ms"],
       ["Q3 three worst hours", ", ".join(f"hour {a} ({b})" for a, b in sq["q3"]), f"{tq['t_q3']*1000:.2f} ms"]], widths=[2.6, 3.2, 1.0], size=8.5)
P(f"The same three answers were computed from the cleaned CSV file with the csv module (one pass, {tq['t_csv']*1000:.1f} ms): identical. Loading {mo['stats']['rows_out']:,} rows with one executemany call took {sq['t_load']*1000:.0f} ms.")
H("B1.4 Visualise (2 marks)", 2)
ch = rB1["charts"]
IMG("TaskB1/chart1_trend.png", 5.6, "Chart 1 - line chart")
P(f"Interpretation: the daily mean at Adyar moves irregularly between {ch['low'][1]:.1f} ug/m3 ({ch['low'][0]}) and {ch['peak'][1]:.1f} ug/m3 ({ch['peak'][0]}); only {ch['days_above_60']} of {ch['ndays']} days exceed the 60 ug/m3 reference line. There is no steady rise or fall within the month - the day-to-day swings (a factor of almost 3) are larger than any trend, which points to weather as the main driver.")
IMG("TaskB1/chart2_stations.png", 6.0, "Chart 2 - box plot of the stations")
P(f"Interpretation: stations differ a lot: the highest median is {ch['med_hi'][1]} ({ch['med_hi'][0]:.1f} ug/m3) and the lowest {ch['med_lo'][1]} ({ch['med_lo'][0]:.1f}), about {ch['med_hi'][0]/ch['med_lo'][0]:.1f} times as much. The boxes of the worst stations are higher and wider (more variable) than the whole box of the cleanest station, so the difference is real and not caused by a few extreme hours.")
IMG("TaskB1/chart3_scatter.png", 4.9, "Chart 3 - scatter plot")
P(f"Interpretation: the correlation coefficient is r = {ch['r']:.2f} over {ch['npts']:,} hourly points - a weak negative relationship: slightly higher PM2.5 at lower temperatures. The cloud is wide, so temperature explains only a few percent of the variation; and since both variables follow the time of day, the plot does not prove that temperature causes the difference.")
IMG("TaskB1/chart4_hours.png", 5.6, "Chart 4 - bar chart by hour")
P(f"Interpretation: the worst hours are {', '.join(str(h) for h in ch['worst_hours'])} - the morning and evening traffic peaks - and the best hour is {ch['best_hour'][0]} ({ch['best_hour'][1]:.1f} ug/m3), in the afternoon. A message to the public could advise outdoor exercise in the afternoon instead of early morning or evening.")
OUTF("TaskB1", "cleaning_pipeline", "Console output of the full pipeline (sample before/after, month statistics, SQL, CSV comparison, charts, summary table)")
H("Alternative concept and complexity analysis - cleaning with pandas (read_csv, to_numeric, masks, groupby ffill) instead of the csv module and loops", 3)
CODE("df = pd.read_csv(path, dtype=str, keep_default_na=False)\ndf[col] = pd.to_numeric(df[col].str.strip(), errors='coerce')          # blank, NA, ERR -> NaN\ndf.loc[f, 'temperature'] = (df.loc[f, 'temperature'] - 32) * 5 / 9      # Fahrenheit stations (vectorised)\ndf[col] = df[col].where(df[col].between(lo, hi))                     # impossible values -> NaN\ndf = df.drop_duplicates(['station', 'date', 'hour']).sort_values([...])\ndf[cols] = df.groupby('station')[cols].ffill(limit=3)", size=7.5)
rows = [["Rows", "csv + loops: time", "peak memory", "pandas: time", "peak memory", "speed-up"]]
for x in rP["rows"]:
    rows.append([f"{x['n']:,}", f"{x['python']['seconds']:.3f} s", f"{x['python']['peak_mb']:.0f} MB", f"{x['pandas']['seconds']:.3f} s", f"{x['pandas']['peak_mb']:.0f} MB", f"{x['python']['seconds']/x['pandas']['seconds']:.1f}x"])
TABLE(rows, widths=[1.0, 1.3, 1.1, 1.2, 1.1, 1.0], size=8.5)
P(f"Each measurement ran in its own process (time of reading the file and cleaning; peak memory = maximum resident set size). On the 1,000-row file all {rP['agree']['same_rows'] and 1000} output rows were compared value by value with the loop version: {rP['agree']['mismatches']} differences. "
  "Both are O(n) in time. pandas has a start-up cost (about 0.2 s for loading the library), so for small files the loop version is faster; from 100,000 rows pandas is about 2 times faster and at 1,000,000 rows about 3 times, because the work is done in compiled code. "
  f"At 1,000,000 rows the loop version used {rP['rows'][2]['python']['peak_mb']:.0f} MB against {rP['rows'][2]['pandas']['peak_mb']:.0f} MB for pandas (the loop version builds a dictionary of Python objects for every row), so the loop version's memory also grows O(n) but with a much larger constant. "
  "For the daily files of the real network (12 stations x 24 rows) the loop version is more than fast enough and has no dependency; for a rebuild of years of data pandas is the better tool.")
doc.add_page_break()

# =============================================================== B2
H("TASK B2 - Engineer Adversarial Data (5 marks)", 1)
H("Complete the Code (TaskB2/complete_code_b2.py)", 2)
CODE("con.executemany('INSERT INTO aq (station, day, pm25) VALUES (?, ?, ?)', readings)      # TODO 1\ncon.commit()\n\ndef station_average(name):                                                                   # TODO 2\n    return con.execute('SELECT AVG(pm25) FROM aq WHERE station = ?', (name,)).fetchone()[0]", size=7.5)
OUTF("TaskB2", "complete_code_b2", "Console output - identical to the expected output (54.0 108.0 / None)", img=False)
P("Why the injection attempt returns None instead of all the rows: with a ? placeholder the whole text Adyar' OR '1'='1 is sent to SQLite as ONE value, never as part of the SQL text. SQLite therefore looks for a station whose name is exactly that string, finds none, and AVG of no rows is NULL (None in Python). "
  "The quote and the word OR have no special meaning inside a value.", bold=False)
H("Adversarial inputs and what they reveal", 2)
rows = [["Adversarial file", "First version (trusts the file)", "Hardened loader"]]
for k, v in rB2["files"].items():
    rows.append([k, v["naive"], " | ".join(v["robust"])])
TABLE(rows, widths=[1.8, 2.3, 2.9], size=8)
P("The first version crashed on four of the six bad files (KeyError for a missing column and for a wrong delimiter - the header is read as one single column - and UnicodeDecodeError for UTF-16 and Windows-1252 text) and, worse, an empty file and a file with only a header returned success with ZERO rows, which would silently produce an empty day in the database. "
  "The hardened loader rejects what it cannot trust with a clear reason (missing columns, empty file), repairs what is safe to repair (BOM or UTF-16 detection, Windows-1252 fallback, delimiter sniffing between , ; tab |) and warns when it did so.")
inj = rB2["injection"]
H("A station name containing a quote; building the SQL with + and with ?", 2)
rows = [["Input", "SQL built with +", "SQL with a ? placeholder"]]
for k, v in inj.items():
    rows.append([k, v["concat"], v["placeholder"]])
TABLE(rows, widths=[2.2, 2.6, 2.2], size=8)
B(["Name with a quote (Women's Road): the + version produces ... station = 'Women's Road' - the quote ends the string early and SQLite reports a syntax error; the ? version treats the quote as ordinary text and returns the correct average 70.0.",
   "Injection Adyar' OR '1'='1: the + version becomes ... station = 'Adyar' OR '1'='1' which is always true, so it returns the average of ALL stations (78.8) - an attacker or a careless user obtains data they did not ask for; the ? version returns None.",
   "Stacked statement x'; DROP TABLE aq; --: the Python sqlite3 execute() refuses more than one statement (ProgrammingError), so the table survives here, but this is a protection of the library, not of the program; with executescript() the same text would run. Only placeholders remove the problem completely."])
H("Sentiment scorer against sarcasm, double negatives and mixed opinions", 2)
rows = [["Sentence", "My reading", "Scorer", "Why"]]
for x in rB2["sentiment"]:
    rows.append([x["text"], x["human"], f"{x['scorer']} ({x['score']:+d})", ("OK - " if x["ok"] else "FAIL - ") + x["kind"]])
TABLE(rows, widths=[3.0, 0.9, 1.0, 2.1], size=8)
P("The scorer was wrong on 7 of the 10 adversarial sentences: it takes 'helpful' literally in sarcasm; it only looks one word back for a negator and counts one negation per word, so 'not never' patterns, 'never really helpful' and contractions (isn't) are missed; it cannot see words outside the list (terrible, stench); "
  "punctuation other than . and , stays attached to the word (Smoke! is not recognised); and positive and negative words cancel to 0, which hides a mixed opinion in the 'neutral' label.")
H("What each adversarial input reveals about the design", 2)
TABLE([["Input", "What it reveals", "Design change"],
       ["Missing column / wrong delimiter", "the program assumed a perfect header", "validate the header before reading rows; sniff the delimiter; reject with a reason"],
       ["Other encoding", "an assumption about the character set", "try BOM, UTF-8, then a fallback; never decode blindly"],
       ["Empty file / header only", "'no rows' looked like success", "an empty input is a failure that must be reported, counted and alerted"],
       ["Quote in a station name", "string building makes data become code", "always use ? placeholders (also in the chatbot of A5.2)"],
       ["Sarcasm, double negative, mixed opinion", "a word list has no understanding of context", "treat the label as a triage aid with human review of 'neutral' and risky patterns; collect labelled data for a trained model"]], widths=[1.7, 2.4, 2.9], size=8.5)
H("Alternative concept and complexity analysis - building SQL by joining strings; executemany() against execute() in a loop", 3)
P("Joining strings: f\"SELECT ... WHERE station = '{name}'\" works for ordinary names, but for the input Adyar' OR '1'='1 it executes a different query (shown above) and returns all rows; it also breaks on any name containing a quote. Time and space are the same as with placeholders, but placeholders also let SQLite prepare the statement once.")
rows = [["Rows", "executemany (s)", "execute in a loop, one commit (s)", "loop / executemany", "on disk: executemany (s)", "on disk: commit after every row"]]
for x in rB2["insert"]:
    rows.append([f"{x['n']:,}", f"{x['many']:.4f}", f"{x['loop']:.4f}", f"{x['loop']/x['many']:.2f}x", f"{x['disk_many']:.4f}", f"{x['disk_commit_each']:.3f} s (1,000 rows)" if x["disk_commit_each"] else "not run"])
TABLE(rows, widths=[0.7, 1.1, 1.6, 1.1, 1.2, 1.5], size=8)
ins0 = rB2["insert"][0]
P(f"Both are O(n) in time; executemany is about {rB2['insert'][1]['loop']/rB2['insert'][1]['many']:.1f} times faster because the statement is prepared once and the loop stays inside the library, instead of one Python-to-SQLite call per row. The big difference is the commit: committing after every row on a disk database needed {ins0['disk_commit_each']:.2f} s for only 1,000 rows, "
  f"about {ins0['disk_commit_each']/ins0['disk_many']:.0f} times more than one executemany with one commit, because every commit forces the data to the disk. Space is O(n) for the row list in both cases.")
doc.add_page_break()

# =============================================================== B3
H("TASK B3 - Loops vs Libraries vs SQL (8 marks)", 1)
H("B3.1 Correctness on small data (2 marks)", 2)
P("Three implementations compute the daily mean PM2.5 per station: (1) plain Python - csv.DictReader, a dictionary of lists keyed by (station, date), statistics.mean; (2) pandas - read_csv and groupby(['station', 'date']).mean(); (3) SQL - the rows are loaded into SQLite and SELECT station, day, AVG(pm25) ... GROUP BY station, day. "
  "Blank readings are skipped in all three (pandas mean skips NaN; SQL AVG ignores NULL). On a file with 2 stations, 3 days and 10 % blanks all methods give the same 6 daily means (agreement tolerance 1e-6) - see the first lines of the output below; the same check passed for 1, 12 and 120 stations.")
H("B3.2 Increase the data size (2 marks)", 2)
rows = [["Stations", "Rows", "File MB", "Python loops", "pandas", "SQL load", "SQL query only", "SQL load + query", "All agree"]]
for x in rB3["sizes"]:
    rows.append([x["stations"], f"{x['rows']:,}", f"{x['file_mb']:.1f}", f"{x['loops']:.3f} s", f"{x['pandas']:.3f} s", f"{x['sql_load']:.3f} s", f"{x['sql_query']:.3f} s", f"{x['sql_load']+x['sql_query']:.3f} s", x["agree"]])
TABLE(rows, widths=[0.6, 0.9, 0.6, 0.9, 0.7, 0.8, 0.9, 0.9, 0.6], size=8)
s3 = rB3["sizes"]
P(f"All times grow in proportion to the number of rows (O(n)): from 105,120 to 1,051,200 rows (10 times) the loop version takes {s3[2]['loops']/s3[1]['loops']:.1f} times as long, pandas {s3[2]['pandas']/s3[1]['pandas']:.1f} times, SQL load + query {(s3[2]['sql_load']+s3[2]['sql_query'])/(s3[1]['sql_load']+s3[1]['sql_query']):.1f} times. "
  f"At one year of 120 stations pandas is {s3[2]['loops']/s3[2]['pandas']:.1f} times faster than the loops; the SQL query alone is as fast as pandas ({s3[2]['sql_query']:.2f} s) but SQL has to be loaded first ({s3[2]['sql_load']:.2f} s) unless the data are already in the database.")
H("B3.3 Profile the plain-Python version (2 marks)", 2)
pt = rB3["profile_top"]
P(f"cProfile of the loop version on 12 stations (105,120 rows): the function with the highest own time is {pt[0][1]} with {pt[0][0]:.3f} s of the profiled run (profiling itself adds overhead): it is the csv reader that parses one line at a time, called {pt[0][2]:,} times. "
  "The most important single part that can be replaced is statistics.mean, which is roughly 40 % of the profiled run (cumulative time, see the report below): it sums exactly with fractions (internal _sum, as_integer_ratio, Fraction objects). "
  "Replacing it by a running sum and count (the alternative below) removed that cost and reduced the run time from {:.3f} s to {:.3f} s. The profile therefore says: parsing is unavoidable in Python, the statistics module is a choice.".format(s3[1]["loops"], s3[1]["running"]))
OUTF("TaskB3", "loops_vs_libraries_vs_sql", "Console output (correctness, three sizes, cProfile report, memory)")
H("B3.4 Engineering trade-off (2 marks)", 2)
TABLE([["Method", "Strengths", "Weaknesses"],
       ["Python loops + csv", "no library needed; full control of every rule; constant memory possible with a running sum", f"slowest ({s3[2]['loops']:.2f} s at 1 million rows); more code; statistics.mean is slow"],
       ["pandas", f"shortest code; fast ({s3[2]['pandas']:.2f} s including the file read); good for exploration and charts", "whole table in memory; dependency; every run re-reads the file"],
       ["SQL GROUP BY", f"query only {s3[2]['sql_query']:.2f} s; data stored once, indexed, shared by many users and reports; constraints", f"load time {s3[2]['sql_load']:.2f} s if the data are not already in the database; needs a schema"]], widths=[1.4, 2.8, 2.8], size=8.5)
P("The differences come from where the work is done: Python loops execute interpreted bytecode for every row, pandas and SQLite run compiled code (C) on whole columns or pages, and SQL additionally keeps the data in a file so the reading and parsing cost is paid once, not at every run. "
  "Decision: for a quick one-time analysis I would use pandas (fewest lines, fast, and the same DataFrame feeds the charts). For the daily automated report I would use SQL: the day's rows are inserted once, the summary is computed by GROUP BY inside the database (or only for the new day), nothing is re-parsed, and the result is reproducible by any user of the database.")
H("Alternative concept and complexity analysis - one pass with a running sum and count per (station, day)", 3)
CODE("acc = {}\nfor row in rows:\n    a = acc.setdefault((row['station'], row['date']), [0.0, 0])\n    a[0] += float(row['pm25']); a[1] += 1\nmeans = {key: total / count for key, (total, count) in acc.items()}", size=7.5)
mem = rB3["mem"]
TABLE([["Design", "Time", "Space", "Measured (12 stations)"],
       ["store all readings, then statistics.mean", "O(n)", "O(n) - every reading kept", f"{s3[1]['loops']:.3f} s; peak {mem['store all readings, then statistics.mean']/1e6:.2f} MB"],
       ["running sum and count", "O(n)", "O(stations x days) - one pair per group", f"{s3[1]['running']:.3f} s; peak {mem['running sum and count (one pass)']/1e6:.2f} MB"]], widths=[2.3, 0.7, 2.2, 1.8], size=8.5)
P(f"Both read every row once (O(n)); the running-sum version is {s3[1]['loops']/s3[1]['running']:.1f} times faster here and needs about {mem['store all readings, then statistics.mean']/mem['running sum and count (one pass)']:.0f} times less memory. It gives the same means (checked on all sizes; the floating-point sum can differ from statistics.mean in the 10th decimal, within the 1e-6 tolerance). "
  "It cannot compute a median or a percentile, which need all values - then the readings must be kept (or sorted by the database).")
doc.add_page_break()

# =============================================================== B4
H("TASK B4 - Final Engineering Decision (5 marks)", 1)
P("New situation: 100 more stations reporting every 15 minutes (112 stations x 96 readings = 10,752 rows a day, about 3.9 million a year) and 50,000 complaints a month.", italic=True)
H("Complete the Code (TaskB4/complete_code_b4.py)", 2)
CODE("for i, w in enumerate(words):                                   # TODO 1\n    value = 1 if w in POSITIVE else -1 if w in NEGATIVE else 0\n    if value != 0 and i > 0 and words[i - 1] in NEGATORS:\n        value = -value\n    total += value", size=7.5)
OUTF("TaskB4", "complete_code_b4", "Console output - identical to the expected output; two wrongly labelled complaints are explained", img=False)
P("Wrongly labelled complaint: 'The staff were never really helpful.' is labelled positive. The negator 'never' is not directly before 'helpful' (the word 'really' is between them), so the rule that looks only at the previous word does not flip the +1. A human reads this as negative.")
H("B4.1 Sentiment scorer and summariser on 54 complaints (2 marks)", 2)
sA = rB4["sentiment"]
conf = sA["conf"]
rows = [["My reading \\ scorer", "negative", "neutral", "positive", "recall"]]
for h in ("negative", "neutral", "positive"):
    tot = sum(conf[f"{h}|{p}"] for p in ("negative", "neutral", "positive"))
    rows.append([h, conf[f"{h}|negative"], conf[f"{h}|neutral"], conf[f"{h}|positive"], f"{conf[f'{h}|{h}']/tot*100:.0f} %"])
TABLE(rows, widths=[1.8, 1.0, 1.0, 1.0, 1.0], size=9)
P(f"I wrote 54 complaints (22 negative, 20 positive, 12 neutral - file complaints_data.py) and labelled them by my own reading before running the scorer. Agreement: {sA['agree']} of 54 labels = {sA['agree']/54*100:.1f} %. All 12 neutral complaints were recognised; the scorer is weakest on negative complaints (68 % recall): 6 were called neutral because they use words that are not in the list "
  "(dust, fumes, stinks, wrong, not working, not cleaned), 1 sarcastic complaint was called positive; 5 positive complaints were called neutral because they express praise with words outside the list or mix a positive and a negative word (improved + smoke). The scorer never called a positive complaint negative and a neutral one positive.")
sm_ = rB4["summary"]
P(f"Summariser (k = 1): in each complaint I marked the sentence that states the main point. The frequency-based summariser selected my sentence in {sm_['freq_hits']} of 54 complaints ({sm_['freq_hits']/54*100:.0f} %). The simple 'first sentence' summariser selected it in {sm_['first_hits']} of 54 ({sm_['first_hits']/54*100:.0f} %). "
  f"The main point is the first sentence in {54-sm_['not_first']} of the 54 complaints, so the first-sentence method is a strong baseline; in the {sm_['not_first']} complaints where it is not the first sentence, the frequency method found it only {sm_['freq_hits_not_first']} time and the first-sentence method never. "
  "The reason: inside one short complaint most words occur only once, so the sentence score is mostly the number of important words and favours the longest sentence, which is usually the first. The summariser needs longer texts (several complaints about the same thing) to profit from word frequency.")
OUTF("TaskB4", "ai_complaints", "Console output (agreement, confusion table, wrong labels, summaries, timings, Naive Bayes comparison)")
P(f"Time: scorer {rB4['time']['score_us']:.1f} microseconds per complaint, frequency summariser {rB4['time']['summarise_us']:.1f}, first-sentence {rB4['time']['first_us']:.1f}; for 50,000 complaints a month the scorer needs {rB4['time']['score_us']*50000/1e6:.2f} s and scorer + summariser {(rB4['time']['score_us']+rB4['time']['summarise_us'])*50000/1e6:.2f} s.")
H("Alternative concept and complexity analysis - first k sentences instead of the most frequent words", 3)
P(f"Solution: return the first k sentences. Time O(1) after the text is split (the frequency method is O(words): count, then score every sentence), space O(k) against O(words) for the frequency table. Measured: {rB4['time']['first_us']:.1f} against {rB4['time']['summarise_us']:.1f} microseconds per complaint. "
  f"Quality on my 54 complaints: {sm_['first_hits']} correct for the first-sentence method and {sm_['freq_hits']} for the frequency method - practically equal, so for single complaints the cheap first-sentence method is as good; the frequency method becomes worthwhile for long complaints or for combining many complaints into one summary.")
H("B4.2 Check the database - index on (station, day) (1 mark)", 2)
bef, aft, cov = rS["before"], rS["after"], rS["cover"]
rows = [["Query", "No index (ms)", "Index (station, day) (ms)", "Speed-up", "Covering index (station, day, pm25) (ms)"]]
for k in bef:
    rows.append([k, f"{bef[k]*1000:.1f}", f"{aft[k]*1000:.2f}", f"{bef[k]/aft[k]:.1f}x", f"{cov[k]*1000:.2f}"])
TABLE(rows, widths=[2.4, 0.9, 1.4, 0.8, 1.5], size=8)
P(f"Test table: {rS['n']:,} rows (112 stations x 96 readings x 120 days), inserted with one executemany call in {rS['t_insert']:.1f} s, database {rS['size_before']:.0f} MB; one year would be about 3.9 million rows. Without an index the slowest query was {rS['slowest'].split('  ')[0]} ({bef[rS['slowest']]*1000:.0f} ms): it must read every row, and the index on (station, day) cannot help it ({bef[rS['slowest']]/aft[rS['slowest']]:.1f}x). "
  f"The index does what it should for the queries that select one station and a range of days (A and B): {bef['A  average of one station in one month']*1000:.1f} ms became {aft['A  average of one station in one month']*1000:.2f} ms ({bef['A  average of one station in one month']/aft['A  average of one station in one month']:.0f} times faster); the query plan changed from {rS['plan_before'][0]} to {rS['plan_after'][0]}. "
  f"The price: creating the index took {rS['t_index']:.2f} s, the file grew from {rS['size_before']:.0f} to {rS['size_after_idx']:.0f} MB, and one daily load of 10,752 rows with both indexes took {rS['t_daily_load']:.2f} s (still negligible). "
  "The full-table summaries (C, D) should be answered from the daily_summary table of A3.2, which has only 112 x 365 rows per year, not from the raw readings. Note: the production table of A1.2 already has the primary key (station_id, day, hour) as its clustered order, which is equivalent to this index.")
OUTF("TaskB4", "scale_database", "Console output of the index experiment")
H("B4.3 Production decision (2 marks)", 2)
TABLE([["Area", "Decision", "Evidence from the measurements"],
       ["Storage", "Keep SQLite for one server and one writer (daily batch); readings table keyed by (station_id, day, hour) plus the daily_summary table; switch to a client-server database (PostgreSQL) only if many users must write at the same time.",
        f"3.9 million rows a year is about {rS['size_before']*365/120:.0f} MB; a daily load of 10,752 rows takes {rS['t_daily_load']:.2f} s even with two indexes; indexed queries take {aft['A  average of one station in one month']*1000:.2f} ms."],
       ["Cleaning", "Daily files (112 x 96 rows): the csv-module pipeline with the rules of A2 and logging; a monthly or historical rebuild: the pandas version.",
        f"The loop version cleans 1,000,000 rows in {rP['rows'][2]['python']['seconds']:.1f} s ({rP['rows'][2]['python']['peak_mb']:.0f} MB), pandas in {rP['rows'][2]['pandas']['seconds']:.1f} s ({rP['rows'][2]['pandas']['peak_mb']:.0f} MB); a day has only 10,752 rows, i.e. about 0.15 s."],
       ["Analysis", "SQL GROUP BY on each new day into daily_summary; charts read the summary table; ad-hoc exploration in pandas.",
        f"SQL group-by of 1.05 million rows: {s3[2]['sql_query']:.2f} s; scanning queries on 1.29 million raw rows: about {bef['C  three stations with the highest mean']*1000:.0f} ms each, so they should use the small summary table."],
       ["Complaints (50,000 a month)", "Use the word-list scorer and the summariser as a first filter now; add a human review queue for complaints with neutral score and for known failure patterns (sarcasm, 'never really'); start collecting real labels. Move to a trained model when several thousand real labelled complaints exist.",
        f"Scoring 50,000 complaints takes {rB4['time']['score_us']*50000/1e6:.2f} s; agreement with my reading is {sA['agree']/54*100:.1f} %; the model trained on synthetic data reached {rB4['nb']['acc']/54*100:.1f} % - not a reliable proof; a trained model costs more effort, not less time."]],
      widths=[1.1, 3.0, 2.9], size=8)
P("The simple AI methods are good enough as a triage tool at this scale, because the cost is negligible and they can be explained and corrected; they are not good enough for decisions about individual complaints (about one complaint in five is mislabelled and the errors are systematic). "
  "The trained model is needed only when the volume of reliably labelled data justifies it and when measured agreement on real complaints is clearly better than the word list.")
doc.add_page_break()

# =============================================================== Appendix
H("Appendix A - Source code of all programs")
for path in ("aqlib.py", "sentiment.py", "TaskA/partA_experiments.py", "TaskB1/complete_code_b1.py", "TaskB1/cleaning_pipeline.py", "TaskB1/pandas_vs_python.py",
             "TaskB2/complete_code_b2.py", "TaskB2/adversarial_inputs.py", "TaskB3/loops_vs_libraries_vs_sql.py", "TaskB4/complete_code_b4.py",
             "TaskB4/complaints_data.py", "TaskB4/ai_complaints.py", "TaskB4/scale_database.py"):
    H(path, 3)
    CODE(open(path).read(), size=6)
H("Appendix B - Evidence and reproduction", 1)
B([f"Measurements were made on: {MACHINE}. Times depend on the computer; counts, row numbers and results do not.",
   "Each task folder contains the programs, the generated input files (TaskB1/sample_messy.csv, october_raw.csv), the SQLite database (TaskB1/airquality.db), charts, output_*.txt, screenshot_*.png and results*.json.",
   "To reproduce: pip install -r requirements.txt; python run_all.py --report (the 1,000,000-row and 120-station tests need about 1 GB of memory and 2 minutes)."])
doc.save("Assignment4_Report.docx")
print("saved Assignment4_Report.docx")
