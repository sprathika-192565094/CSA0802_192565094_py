"""Task 3.1 / 3.3 evidence: provoke every failure and show the exception actually raised."""
import os, tempfile
from unittest import mock
from attendance_processor import process_file, parse_line, InvalidRecord, ProcessingError

d = tempfile.mkdtemp()
good = os.path.join(d, "good.csv")
open(good, "w", encoding="utf-8").write("192311001,2026-10-08,P\n192311002,2026-10-08\n192311003,2026-10-08,A\n192311004,2026-10-08,L\n")
empty = os.path.join(d, "empty.csv"); open(empty, "w").close()
badenc = os.path.join(d, "badenc.csv"); open(badenc, "wb").write(b"\xff\xfe\x00\x01,2026,P\n")
adir = os.path.join(d, "folder.csv"); os.mkdir(adir)

cases = [
    ("missing folder", os.path.join(d, "nofolder", "x.csv"), None),
    ("missing file", os.path.join(d, "nofile.csv"), None),
    ("permission denied (simulated)", good, PermissionError(13, "Permission denied")),
    ("wrong encoding", badenc, None),
    ("path is a directory", adir, None),
    ("empty file", empty, None),
    ("damaged lines only partly bad", good, None),
]
print(f"{'Failure':32} {'Built-in exception caught':22} Result")
for label, path, sim in cases:
    log = []
    try:
        if sim:
            with mock.patch("builtins.open", side_effect=sim):
                process_file(path, log)
        else:
            res = process_file(path, log)
            print(f"{label:32} {'(none)':22} counts={res} log={[l.split(':',1)[1] if ':' in l else l for l in log]}")
            continue
    except ProcessingError as e:
        print(f"{label:32} {(type(e.__cause__).__name__ if e.__cause__ else '(raised in else)'):22} {e}")

print()
for text in ["192311001,2026-10-08", "192311001,2026-10-08,L", "192311001,2026-10-08,P"]:
    try:
        print("parse_line ->", parse_line(text))
    except InvalidRecord as e:
        print("parse_line ->", type(e).__name__, "-", e)
