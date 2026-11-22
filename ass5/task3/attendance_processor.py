"""Task 3 - exception-aware attendance processor (3.2 custom exception, 3.3 full try statement)."""


class InvalidRecord(Exception):
    """Raised when a line of the attendance file is not in the expected format."""


class ProcessingError(Exception):
    """Raised when a whole file cannot be processed (wraps the original cause)."""


def parse_line(line):
    """'192311001,2026-10-08,P' -> ('192311001', '2026-10-08', 'P')"""
    parts = line.strip().split(",")
    if len(parts) != 3:                                   # RAISED here (where the fault is detected)
        raise InvalidRecord(f"expected 3 fields, found {len(parts)}")
    regno, date, status = parts
    if status not in ("P", "A"):
        raise InvalidRecord(f"invalid status {status!r}")
    return regno, date, status


def process_file(path, error_log):
    """Count P/A in one file. Bad lines are logged (HANDLED here); file-level
    failures are converted to ProcessingError using `raise ... from ...`."""
    counts = {"P": 0, "A": 0}
    f = None
    try:
        f = open(path, encoding="utf-8")
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                _, _, status = parse_line(line)
            except InvalidRecord as err:                   # HANDLED: log and carry on
                error_log.append(f"{path}:{line_no}: {err}")
                continue
            counts[status] += 1
    except FileNotFoundError as err:
        raise ProcessingError(f"missing file or folder: {path}") from err
    except PermissionError as err:
        raise ProcessingError(f"permission denied: {path}") from err
    except UnicodeDecodeError as err:
        raise ProcessingError(f"wrong encoding in {path}") from err
    except OSError as err:                                 # e.g. a directory given as a file
        raise ProcessingError(f"cannot read {path}: {err.strerror}") from err
    else:                                                  # runs only if no exception occurred
        if counts["P"] + counts["A"] == 0:
            raise ProcessingError(f"empty file (no valid records): {path}")
        return counts
    finally:                                               # always runs: release the file
        if f is not None:
            f.close()
