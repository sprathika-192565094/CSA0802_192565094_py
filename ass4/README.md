# CSA08 - Python Programming - Assignment 4: City Air-Quality Monitoring Network

| | |
|---|---|
| **Student name** | `<YOUR NAME>` |
| **Register number** | `<REGISTER NUMBER>` |
| **Repository** | `CSA08-<RegisterNumber>-Assignment4` |

## Environment
* **Python:** 3.12 (3.9 or newer works). **Libraries:** `csv`, `sqlite3`, `statistics`, `re` (standard library) plus `pandas`, `numpy`, `matplotlib`, `scikit-learn` (only for the alternative concept of A5/B4), `pillow` and `python-docx` (screenshots and report builder).

```
pip install -r requirements.txt
```

## Layout and how to run (run each command from inside the task folder)
| Folder | Program | What it does |
|---|---|---|
| `aqlib.py`, `sentiment.py` | shared modules | data generator, cleaning rules, normalisation, SQLite schema; word-list sentiment scorer |
| `TaskA/` | `partA_experiments.py` | evidence for Part A: drop / forward fill / median fill, min-max and z-score, cost of print / logging / assert |
| `TaskB1/` | `complete_code_b1.py` | Complete the Code (load_clean, min_max) + the >999 check |
| `TaskB1/` | `cleaning_pipeline.py` | B1.1-B1.4: sample file before/after, full month, SQLite with executemany, three SQL questions, four charts, daily summary table |
| `TaskB1/` | `pandas_vs_python.py` | alternative concept: pandas cleaning at 1,000 / 100,000 / 1,000,000 rows (time and peak memory) |
| `TaskB2/` | `complete_code_b2.py` | Complete the Code (executemany, parameterised SELECT) |
| `TaskB2/` | `adversarial_inputs.py` | bad files, SQL injection with + and ?, sentiment traps, executemany vs execute |
| `TaskB3/` | `loops_vs_libraries_vs_sql.py` | daily mean per station with loops, pandas and SQL at 1, 12 and 120 stations; cProfile; running-sum alternative |
| `TaskB4/` | `complete_code_b4.py` | Complete the Code (score with negation) |
| `TaskB4/` | `ai_complaints.py` (+ `complaints_data.py`) | 54 labelled complaints: agreement, summariser, Naive Bayes comparison |
| `TaskB4/` | `scale_database.py` | 112 stations x 96 readings: queries without and with an index |

Run everything: `python run_all.py` (add `--report` to rebuild `Assignment4_Report.docx`). The 1,000,000-row and 120-station tests need about 1 GB of memory and 1-2 minutes.

Each task folder contains `output_<program>.txt`, `screenshot_<program>.png` and `results*.json`. Generated inputs: `TaskB1/sample_messy.csv`, `TaskB1/october_raw.csv`; database: `TaskB1/airquality.db`; charts: `TaskB1/chart*.png`.

## Notes
* Part A (designs, pseudocode, chart choices) is in `Assignment4_Report.pdf`; Part A experiments are in `TaskA/`.
* Timings depend on the computer; counts and results do not.
