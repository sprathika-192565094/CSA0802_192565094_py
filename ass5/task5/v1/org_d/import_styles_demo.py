"""Task 5.3 - the three import styles."""
import attendance.stats                       # style 1: whole sub-module, full dotted name
from attendance import stats                  # style 2: sub-module bound to the name `stats`
from attendance.stats import percentage       # style 3: one function bound directly

data = {"192311001": {"d1": "P", "d2": "A"}}
print(attendance.stats.percentage(data))      # style 1 call
print(stats.percentage(data))                 # style 2 call
print(percentage(data))                       # style 3 call
