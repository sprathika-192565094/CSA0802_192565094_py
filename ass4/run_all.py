"""python run_all.py            -> run all programs, save outputs and screenshots
   python run_all.py --report   -> also rebuild Assignment4_Report.docx"""
import subprocess, sys

subprocess.run([sys.executable, "capture_outputs.py"], check=True)
if "--report" in sys.argv:
    subprocess.run([sys.executable, "build_report.py"], check=True)
