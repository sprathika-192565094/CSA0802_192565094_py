"""Task 4.3 - repaired library return logger."""
import traceback
from datetime import datetime


def read_books(day_file):
    """Return the non-empty book titles of one day's file (file closed by `with`)."""
    with open(day_file, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def save_returns(books, log_path="returns.log"):
    """APPEND one title per line; the file is always closed."""
    with open(log_path, "a", encoding="utf-8") as log:       # 'a' keeps earlier days
        for b in books:
            log.write(b + "\n")                              # newline separates books


def log_error(day_file, err, error_log="errors.log"):
    with open(error_log, "a", encoding="utf-8") as ef:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ef.write(f"{stamp} | {day_file} | {type(err).__name__}: {err}\n")


def process(day_file, log_path="returns.log", error_log="errors.log"):
    """Process one day. Returns True on success, False if the day failed."""
    try:
        books = read_books(day_file)
        save_returns(books, log_path)
    except FileNotFoundError as err:
        log_error(day_file, err, error_log)
    except (UnicodeDecodeError, PermissionError, OSError) as err:
        log_error(day_file, err, error_log)
    except Exception as err:                                  # unexpected: record full traceback, then re-raise
        log_error(day_file, err, error_log)
        with open(error_log, "a", encoding="utf-8") as ef:
            ef.write(traceback.format_exc())
        raise
    else:
        return True
    return False
