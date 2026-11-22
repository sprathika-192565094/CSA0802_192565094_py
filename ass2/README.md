# CSA08 - Python Programming - Assignment 2 (CO2)

| | |
|---|---|
| **Student name** | `<YOUR NAME>` |
| **Register number** | `<REGISTER NUMBER>` |
| **Repository** | `CSA08-<RegisterNumber>-Assignment2` |

## Environment
* **Python version:** 3.12 (any version >= 3.10 works; `match-case` in Task01 needs 3.10+)
* **Libraries:** only the standard library is used by the task programs.
  `matplotlib` (graphs in Task06 and Task07), `pillow` (output images) and `python-docx` (report builder) are listed in `requirements.txt`.

```
pip install -r requirements.txt
```

## Repository layout
```
Task01/  subsidy.py            Q1  if / elif / match-case / slab table
Task02/  otp_kiosk.py          Q2  while, for, break, continue, pass, loop-else, recursion
Task03/  vehicle_validator.py  Q3  string methods + slicing, regex comparison
Task04/  string_building.py    Q4  += vs join() vs f-string vs StringIO/file
Task05/  canteen_orders.py     Q5  default-parameter bug, scope, closures
Task06/  temple_steps.py       Q6  recursion, memoisation, recursion limit
Task07/  design_challenge.py   Q7  diagnose, redesign, validate (redesign of Q6)
```
Every task folder also contains `output.txt` (console output), `output_screenshot.png`, and `results.json` (raw measurements:
operation counts, call counts and timings). Task06 and Task07 also contain the graphs (`calls_growth.png`, `original_vs_redesign.png`).

## How to run each program
No input files are needed (inputs are built into the programs so results are repeatable).

| Task | Command | Result |
|---|---|---|
| 01 | `cd Task01 && python subsidy.py` | Predictions vs results for 8 households at all boundaries; the separate-`if` version gives wrong/double subsidies, `if-elif-else`, `match-case` and the slab table agree with the predictions. |
| 02 | `cd Task02 && python otp_kiosk.py` | `while`, `for/else` and recursive OTP loops behave identically; blank entries are not counted; the changed condition (+2 attempts) is handled by the `while` design. |
| 03 | `cd Task03 && python vehicle_validator.py` | Normalise / validate / format work on all test numbers; slicing and regex versions agree; immutability demonstrated. |
| 04 | `cd Task04 && python string_building.py` | Same 3,048,890-character text from every method; `join()` is the fastest; `+=` on an attribute shows the quadratic cost. |
| 05 | `cd Task05 && python canteen_orders.py` | Default-list bug reproduced and fixed with `None`; scope rules demonstrated. |
| 06 | `cd Task06 && python temple_steps.py` | naive calls = 2*ways(n)-1 (242,785 for n=25), memo calls = n+1 (26); RecursionError at n=1000 explained; loop version is the deployed design. |
| 07 | `cd Task07 && python design_challenge.py` | Original recursion vs two-variable loop: 2,692,537 calls -> 29 additions for n=30. |

Run everything and refresh the outputs: `python run_all.py` (add `--report` to rebuild the Word report).

## Notes
* Timings depend on the computer; the report states the machine used. Run the programs on your own machine before submitting.
* Counts of operations and function calls (not only times) are the primary evidence.
