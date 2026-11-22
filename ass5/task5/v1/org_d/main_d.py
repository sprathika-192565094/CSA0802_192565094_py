"""Organisation (d): package attendance/."""
import os
from attendance import (read_records, percentage, below_threshold,
                        write_summary, write_list, write_errors)


def run(folder, outdir):
    os.makedirs(outdir, exist_ok=True)
    records, bad = read_records(folder)
    pcts = percentage(records)
    write_summary(os.path.join(outdir, "summary.csv"), pcts)
    write_list(os.path.join(outdir, "below_75.txt"), below_threshold(pcts))
    write_errors(os.path.join(outdir, "errors.log"), bad)


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "../sample_attendance",
        sys.argv[2] if len(sys.argv) > 2 else "out")
