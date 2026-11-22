"""attendance package - public API."""
from .reader import read_records
from .stats import percentage, below_threshold, three_day_absent
from .report import write_summary, write_list, write_errors
