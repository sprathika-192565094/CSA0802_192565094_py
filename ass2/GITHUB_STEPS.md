# GitHub steps (do these progressively - the assignment needs at least one commit per task)

1. Fill in your name and register number in `README.md` and at the top of `build_report.py` (NAME, REGNO, REPO).
2. Create an EMPTY repository on GitHub named `CSA08-<RegisterNumber>-Assignment2` and add the faculty as collaborators (or make it public).
3. In the unzipped folder:

```
git init
git branch -M main
git remote add origin https://github.com/<username>/CSA08-<RegisterNumber>-Assignment2.git
```

4. Work through the tasks one at a time. After running each program on YOUR computer (python TaskXX/<file>.py) commit it:

```
git add Task01 && git commit -m "Task01: subsidy rules - if vs if-elif-else, match-case, slab table"
git add Task02 && git commit -m "Task02: OTP attempts - while, for/else, recursion, changed condition"
git add Task03 && git commit -m "Task03: vehicle number validator with slicing and regex comparison"
git add Task04 && git commit -m "Task04: += vs join vs f-string vs StringIO, timings"
git add Task05 && git commit -m "Task05: default-parameter bug, scope rules, closure design"
git add Task06 && git commit -m "Task06: temple steps - recursion, memoisation, recursion limit, loop"
git add Task07 && git commit -m "Task07: design challenge - diagnose, redesign, validate"
git add README.md requirements.txt run_all.py capture_outputs.py build_report.py .gitignore Assignment2_Report.* && git commit -m "Add README, report and helper scripts"
git push -u origin main
```

5. Put the repository link in the report (title page) and submit the PDF on the portal.
