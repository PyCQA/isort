import os
import sys
from datetime import datetime
from difflib import unified_diff


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
            return "import {0}".format(import_line)
        parts = import_line.split(".")
        end = parts.pop(-1)
        return "from {0} import {1}".format(".".join(parts), end)

    return import_line


def show_unified_diff(*, file_input: str, file_output: str, file_path: str) -> None:
    unified_diff_lines = unified_diff(
        file_input.splitlines(keepends=True),
        file_output.splitlines(keepends=True),
        fromfile=file_path + ':before',
        tofile=file_path + ':after',
        fromfiledate=str(datetime.fromtimestamp(os.path.getmtime(file_path))
                         if file_path else datetime.now()),
        tofiledate=str(datetime.now())
    )
    for line in unified_diff_lines:
        sys.stdout.write(line)


def ask_whether_to_apply_changes_to_file(file_path: str) -> bool:
    answer = None
    while answer not in ('yes', 'y', 'no', 'n', 'quit', 'q'):
        answer = input("Apply suggested changes to '{0}' [y/n/q]? ".format(file_path)).lower()
        if answer in ('no', 'n'):
            return False
        if answer in ('quit', 'q'):
            sys.exit(1)
    return True
