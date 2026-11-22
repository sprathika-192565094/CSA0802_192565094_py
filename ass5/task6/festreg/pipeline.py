"""Orchestration: read -> validate -> de-duplicate -> write. Never stops on a bad line or file."""
import os
from .exceptions import InvalidRecord, DuplicateRegistration
from .reader import read_department_file
from .validator import validate_line
from .writer import write_master, write_event_files, write_summary, write_error_log

DEPARTMENT_FILES = ["CSE.txt", "ECE.txt", "MECH.txt", "CIVIL.txt", "IT.txt"]


def run(input_dir, output_dir, files=DEPARTMENT_FILES):
    os.makedirs(output_dir, exist_ok=True)
    students = {}           # regno -> record            (dict: O(1) lookup)
    seen = set()            # register numbers already seen (set: O(1) average membership)
    event_map = {}          # event -> [(regno, name)]
    dept_count = {}
    errors = []             # (source, line_no, kind, message)
    stats = dict(files_read=0, files_missing=0, lines_read=0, accepted=0, duplicates=0, invalid=0)

    for name in files:
        path = os.path.join(input_dir, name)
        try:
            for line_no, line in read_department_file(path):
                stats["lines_read"] += 1
                try:
                    regno, sname, dept, email, events = validate_line(line)
                    if regno in seen:
                        raise DuplicateRegistration(f"register number {regno} already registered")
                except InvalidRecord as err:
                    stats["invalid"] += 1
                    errors.append((name, line_no, "InvalidRecord", str(err)))
                except DuplicateRegistration as err:
                    stats["duplicates"] += 1
                    errors.append((name, line_no, "DuplicateRegistration", str(err)))
                else:
                    seen.add(regno)
                    students[regno] = dict(name=sname, dept=dept, email=email, events=events)
                    dept_count[dept] = dept_count.get(dept, 0) + 1
                    for e in events:
                        event_map.setdefault(e, []).append((regno, sname))
                    stats["accepted"] += 1
        except FileNotFoundError as err:
            stats["files_missing"] += 1
            errors.append((name, None, "FileNotFoundError", "department file missing - skipped"))
        except PermissionError:
            errors.append((name, None, "PermissionError", "cannot open file - skipped"))
        except UnicodeDecodeError as err:
            errors.append((name, None, "UnicodeDecodeError", f"not UTF-8 text - rest of file skipped ({err.reason})"))
        else:
            stats["files_read"] += 1

    write_master(os.path.join(output_dir, "master_list.csv"), students)
    write_event_files(os.path.join(output_dir, "events"), event_map)
    write_summary(os.path.join(output_dir, "summary_report.txt"), stats, event_map, dept_count)
    write_error_log(os.path.join(output_dir, "error_log.txt"), errors)
    return stats, errors
