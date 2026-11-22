"""Run every task, save outputs + screenshots, then (optionally) rebuild the report.
    python run_all.py            -> runs Task01..Task07 and captures outputs
    python run_all.py --report   -> also rebuilds Assignment2_Report.docx from the fresh results"""
import subprocess, sys

subprocess.run([sys.executable, "capture_outputs.py"], check=True)
if "--report" in sys.argv:
    subprocess.run([sys.executable, "build_report.py"], check=True)
