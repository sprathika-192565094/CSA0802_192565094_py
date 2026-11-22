def percentage(records):
    """Attendance percentage per student (recorded days only)."""
    result = {}
    for regno, days in records.items():
        present = sum(1 for s in days.values() if s == "P")
        result[regno] = round(100 * present / len(days), 2)
    return result


def below_threshold(pcts, limit=75):
    """Register numbers strictly below the limit."""
    return sorted(r for r, p in pcts.items() if p < limit)


def three_day_absent(records, run=3):
    """Students absent on `run` consecutive recorded days (new requirement)."""
    flagged = []
    for regno, days in records.items():
        streak = 0
        for date in sorted(days):
            streak = streak + 1 if days[date] == "A" else 0
            if streak >= run:
                flagged.append(regno)
                break
    return sorted(flagged)
