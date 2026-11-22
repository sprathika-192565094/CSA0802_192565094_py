"""Organisation (c): three modules in one folder."""
import os
import reader
import stats
import report


def run(folder, outdir):
    os.makedirs(outdir, exist_ok=True)
    records, bad = reader.read_records(folder)
    pcts = stats.percentage(records)
    report.write_summary(os.path.join(outdir, "summary.csv"), pcts)
    report.write_list(os.path.join(outdir, "below_75.txt"), stats.below_threshold(pcts))
    report.write_errors(os.path.join(outdir, "errors.log"), bad)
    report.write_list(os.path.join(outdir, "absent_3_days.txt"), stats.three_day_absent(records))


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "../sample_attendance",
        sys.argv[2] if len(sys.argv) > 2 else "out")
