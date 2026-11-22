"""Organisation (b): main script importing attendance_lib."""
import os
import attendance_lib as lib


def run(folder, outdir):
    os.makedirs(outdir, exist_ok=True)
    records, bad = lib.read_records(folder)
    pcts = lib.percentage(records)
    lib.write_summary(os.path.join(outdir, "summary.csv"), pcts)
    lib.write_list(os.path.join(outdir, "below_75.txt"), lib.below_threshold(pcts))
    lib.write_errors(os.path.join(outdir, "errors.log"), bad)


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "../sample_attendance",
        sys.argv[2] if len(sys.argv) > 2 else "out")
