"""Runs every task program, saves its console output to TaskXX/output.txt and renders it as a
terminal-style image TaskXX/output_screenshot.png (use real screenshots too if your marker wants them)."""
import subprocess, sys, os, glob
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
PROGRAMS = {"Task01": "rainfall.py", "Task02": "tuples_copying.py", "Task03": "complaints.py",
            "Task04": "elective_clash.py", "Task05": "sensor_cleaning.py",
            "Task06": "timetable.py", "Task07": "contact_merge.py"}


def render(text, path, size=15, max_lines=60, title="python"):
    lines = text.rstrip("\n").split("\n")
    pages = [lines[i:i + max_lines] for i in range(0, len(lines), max_lines)] or [[""]]
    try:
        font = ImageFont.truetype(FONT, size)
    except OSError:
        font = ImageFont.load_default()
    paths = []
    for pi, page in enumerate(pages):
        w = max(900, int(max(len(l) for l in page) * size * 0.61) + 40)
        h = len(page) * (size + 5) + 50
        img = Image.new("RGB", (w, h), (30, 30, 30))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, w, 26], fill=(60, 60, 60))
        d.text((10, 5), "Terminal  -  " + title, fill=(200, 200, 200), font=font)
        y = 36
        for l in page:
            d.text((14, y), l, fill=(230, 230, 230), font=font)
            y += size + 5
        p = path if len(pages) == 1 else path.replace(".png", f"_part{pi + 1}.png")
        img.save(p)
        paths.append(p)
    return paths


if __name__ == "__main__":
    for task, prog in PROGRAMS.items():
        r = subprocess.run([sys.executable, prog], cwd=task, capture_output=True, text=True)
        text = r.stdout + (("\n[stderr]\n" + r.stderr) if r.stderr else "")
        open(f"{task}/output.txt", "w").write(text)
        for p in render(text, f"{task}/output_screenshot.png", title="python " + prog):
            print(task, "->", p)
        print(task, "exit code", r.returncode)
