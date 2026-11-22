"""Run the fest registration desk:  python main.py <input_dir> <output_dir>"""
import sys
from festreg import run

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "input_clean"
    dst = sys.argv[2] if len(sys.argv) > 2 else "output"
    stats, errors = run(src, dst)
    print(stats)
    print(f"{len(errors)} problem(s) logged in {dst}/error_log.txt")
