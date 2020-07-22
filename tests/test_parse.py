from hypothesis_auto import auto_pytest_magic

from isort import parse
from isort.settings import Config

TEST_CONTENTS = """
import xyz
import abc
import (\\ # one
    one as \\ # two
    three)
import \\
    zebra as \\ # one
    not_bacon
from x import (\\ # one
    one as \\ # two
    three)


def function():
    pass
"""


def test_file_contents():
    (
        in_lines,
        out_lines,
        import_index,
        _,
        _,
        _,
        _,
        _,
        change_count,
        original_line_count,
        _,
        _,
    ) = parse.file_contents(TEST_CONTENTS, config=Config(default_section=""))
    assert "\n".join(in_lines) == TEST_CONTENTS
    assert "import" not in "\n".join(out_lines)
    assert import_index == 1
    assert change_count == -11
    assert original_line_count == len(in_lines)


auto_pytest_magic(parse.import_type)
auto_pytest_magic(parse.skip_line)
auto_pytest_magic(parse._strip_syntax)
auto_pytest_magic(parse._infer_line_separator)
