import sys

from isort import parse
from isort.settings import DEFAULT_SECTIONS, default

TEST_CONTENTS = """
import xyz
import abc


def function():
    pass
"""


def test_file_contents():
    (
        in_lines,
        out_lines,
        import_index,
        place_imports,
        import_placements,
        as_map,
        imports,
        categorized_comments,
        first_comment_index_start,
        first_comment_index_end,
        change_count,
        original_line_count,
        line_separator,
        sections,
        section_comments,
    ) = parse.file_contents(TEST_CONTENTS, config=default)
    assert "\n".join(in_lines) == TEST_CONTENTS
    assert "import" not in "\n".join(out_lines)
    assert import_index == 1
    assert change_count == -2
    assert original_line_count == len(in_lines)


if sys.version_info[1] > 5:
    from hypothesis_auto import auto_pytest_magic

    auto_pytest_magic(parse.import_comment)
    auto_pytest_magic(parse.import_type)
    auto_pytest_magic(parse.skip_line)
    auto_pytest_magic(parse._strip_syntax)
    auto_pytest_magic(parse._infer_line_separator)
