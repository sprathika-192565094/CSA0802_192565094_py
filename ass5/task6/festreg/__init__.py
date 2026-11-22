"""festreg - College Fest Registration Desk package."""
from .exceptions import FestError, InvalidRecord, DuplicateRegistration
from .reader import read_department_file
from .validator import validate_line
from .writer import write_master, write_event_files, write_summary, write_error_log
from .pipeline import run

__all__ = ["FestError", "InvalidRecord", "DuplicateRegistration", "read_department_file",
           "validate_line", "write_master", "write_event_files", "write_summary",
           "write_error_log", "run"]
