# CSA08 - Python Programming - Assignment 3

| | |
|---|---|
| **Student name** | `<YOUR NAME>` |
| **Register number** | `<REGISTER NUMBER>` |
| **Repository** | `CSA08-<RegisterNumber>-Assignment3` |

## Environment
* **Python version:** 3.12 (any version >= 3.8 works)
* **Libraries:** the task programs use only the standard library. `matplotlib` (diagrams in Task02/Task04), `pillow` (output images) and `python-docx` (report builder) are in `requirements.txt`.

```
pip install -r requirements.txt
```

## Repository layout and how to run
| Task | Topic | Command | Result |
|---|---|---|---|
| Task01 | Lists and slicing - rainfall records | `cd Task01 && python rainfall.py` | weekly totals, extremes, 3 moving-average methods; counted additions equal 6(n-6) and 2n-8 |
| Task02 | Tuples, mutability, copying | `cd Task02 && python tuples_copying.py` (and `python memory_diagrams.py`) | grid aliasing bug, copy types, tuple vs list memory, dictionary grid |
| Task03 | Dictionaries - complaint analysis | `cd Task03 && python complaints.py` | word frequencies, grouping, dict vs list.count vs Counter |
| Task04 | Sets - elective clashes | `cd Task04 && python elective_clash.py` (and `python venn_diagrams.py`) | both / exactly one / neither, set vs list timing |
| Task05 | List comprehension - sensor cleaning | `cd Task05 && python sensor_cleaning.py` | loop vs comprehension vs map/filter, generator memory |
| Task06 | Nested data - railway timetable | `cd Task06 && python timetable.py` | queries, station index vs full scan |
| Task07 | Design - merging contacts | `cd Task07 && python contact_merge.py` | dictionary + union-find merge, pairwise comparison |

Every task folder contains `output.txt`, `output_screenshot.png` and `results.json` (raw counts and timings).
Run everything: `python run_all.py` (add `--report` to rebuild `Assignment3_Report.docx`).

## Notes
* Timings depend on the computer; run the programs on your own machine before submitting. Operation counts do not depend on the machine.
* Inputs are generated inside the programs (fixed random seeds), so results are repeatable.
