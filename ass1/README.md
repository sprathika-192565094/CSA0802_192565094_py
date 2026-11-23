# Ksheera Milk Payment Calculator — CO1

Student: ____________________  
Register number: ____________________  
Python version: Python 3 (standard library only; verify with `python --version`)

## Files
- `milkrate.py`: constants, validation, rate calculation, payout, ten-day total, tests and benchmark.
- `main.py`: demonstrates importing and using the shared module.
- `Assignment_Report.docx`: concise written answers for Tasks 1–12.

## Run
```bash
python milkrate.py
python main.py
```

The program uses `Decimal` and `ROUND_HALF_UP` for monetary amounts. It assumes fractional 0.1 percentage-point steps are rounded half-up. The source assignment does not specify an SNF validation range, so one has not been invented. The bonus is assumed to apply to all litres when total supply is strictly greater than 500 litres.

Benchmark times are measured on the machine that runs the script and should be copied into the report only after execution. Update the student details before submission.
