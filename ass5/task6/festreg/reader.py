"""Reading one department file; file-level failures become FestError-free tuples."""


def read_department_file(path):
    """Yield (line_no, text) for every non-blank line, one line at a time.

    FileNotFoundError / PermissionError / UnicodeDecodeError are NOT handled here;
    they are handled by the pipeline, which knows how to log them and carry on.
    """
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                yield line_no, line
