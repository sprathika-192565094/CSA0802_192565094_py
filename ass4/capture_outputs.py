"""Runs every program of the assignment, saves its console output (output_<program>.txt) and renders it as a terminal-style image."""
import os
import subprocess
import sys
import time
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
PROGRAMS = [("TaskA", "partA_experiments.py"), ("TaskB1", "complete_code_b1.py"), ("TaskB1", "cleaning_pipeline.py"), ("TaskB1", "pandas_vs_python.py"),
            ("TaskB2", "complete_code_b2.py"), ("TaskB2", "adversarial_inputs.py"), ("TaskB3", "loops_vs_libraries_vs_sql.py"),
            ("TaskB4", "complete_code_b4.py"), ("TaskB4", "ai_complaints.py"), ("TaskB4", "scale_database.py")]


def render(text, path, title, size=14, max_lines=62):
    lines = text.rstrip("\n").split("\n")
    pages = [lines[i:i + max_lines] for i in range(0, len(lines), max_lines)] or [[""]]
    try:
        font = ImageFont.truetype(FONT, size)
    except OSError:
        font = ImageFont.load_default()
    paths = []
    for pi, page in enumerate(pages):
        w = min(1700, max(900, int(max(len(l) for l in page) * size * 0.61) + 40))
        h = len(page) * (size + 5) + 50
        img = Image.new("RGB", (w, h), (30, 30, 30))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, w, 26], fill=(60, 60, 60))
        d.text((10, 5), "Terminal  -  " + title + (f"   (part {pi + 1} of {len(pages)})" if len(pages) > 1 else ""), fill=(200, 200, 200), font=font)
        y = 36
        for l in page:
            d.text((14, y), l[:int((w - 28) / (size * 0.61))], fill=(230, 230, 230), font=font)
            y += size + 5
        p = path if len(pages) == 1 else path.replace(".png", f"_part{pi + 1}.png")
        img.save(p)
        paths.append(p)
    return paths


if __name__ == "__main__":
    only = sys.argv[1:]
    for task, prog in PROGRAMS:
        if only and prog not in only:
            continue
        t = time.time()
        r = subprocess.run([sys.executable, prog], cwd=task, capture_output=True, text=True, timeout=290)
        text = r.stdout + (("\n[stderr]\n" + r.stderr) if r.stderr.strip() else "")
        base = prog[:-3]
        open(f"{task}/output_{base}.txt", "w").write(text)
        render(text, f"{task}/screenshot_{base}.png", f"python {prog}")
        print(task, prog, "exit", r.returncode, f"{time.time() - t:.0f}s", flush=True)
