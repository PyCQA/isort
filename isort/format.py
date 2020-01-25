import sys
from datetime import datetime
from difflib import unified_diff
from pathlib import Path
from typing import Optional


def format_simplified(import_line: str) -> str:
    import_line = import_line.strip()
    if import_line.startswith("from "):
        import_line = import_line.replace("from ", "")
        import_line = import_line.replace(" import ", ".")
    elif import_line.startswith("import "):
        import_line = import_line.replace("import ", "")

    return import_line


def format_natural(import_line: str) -> str:
    import_line = import_line.strip()
    if not import_line.startswith("from ") and not import_line.startswith("import "):
        if "." not in import_line:
            return f"import {import_line}"
        parts = import_line.split(".")
        end = parts.pop(-1)
        return f"from {'.'.join(parts)} import {end}"

    return import_line


def show_unified_diff(*, file_input: str, file_output: str, file_path: Optional[Path]):
    file_name = "" if file_path is None else str(file_path)
    file_mtime = str(
        datetime.now() if file_path is None else datetime.fromtimestamp(file_path.stat().st_mtime)
    )

    unified_diff_lines = unified_diff(
        file_input.splitlines(keepends=True),
        file_output.splitlines(keepends=True),
        fromfile=file_name + ":before",
        tofile=file_name + ":after",
        fromfiledate=file_mtime,
        tofiledate=str(datetime.now()),
    )
    for line in unified_diff_lines:
        sys.stdout.write(line)


def ask_whether_to_apply_changes_to_file(file_path: str) -> bool:
    answer = None
    while answer not in ("yes", "y", "no", "n", "quit", "q"):
        answer = input(f"Apply suggested changes to '{file_path}' [y/n/q]? ")  # nosec
        answer = answer.lower()
        if answer in ("no", "n"):
            return False
        if answer in ("quit", "q"):
            sys.exit(1)
    return True


def remove_whitespace(content: str, line_separator: str = "\n") -> str:
    content = content.replace(line_separator, "").replace(" ", "").replace("\x0c", "")
    return content
