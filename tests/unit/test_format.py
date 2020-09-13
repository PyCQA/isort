from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import colorama
import pytest
from hypothesis import given, reject
from hypothesis import strategies as st

import isort.format


def test_ask_whether_to_apply_changes_to_file():
    with patch("isort.format.input", MagicMock(return_value="y")):
        assert isort.format.ask_whether_to_apply_changes_to_file("")
    with patch("isort.format.input", MagicMock(return_value="n")):
        assert not isort.format.ask_whether_to_apply_changes_to_file("")
    with patch("isort.format.input", MagicMock(return_value="q")):
        with pytest.raises(SystemExit):
            assert isort.format.ask_whether_to_apply_changes_to_file("")


def test_basic_printer(capsys):
    printer = isort.format.create_terminal_printer(color=False)
    printer.success("All good!")
    out, _ = capsys.readouterr()
    assert out == "SUCCESS: All good!\n"
    printer.error("Some error")
    _, err = capsys.readouterr()
    assert err == "ERROR: Some error\n"


def test_basic_printer_diff(capsys):
    printer = isort.format.create_terminal_printer(color=False)
    printer.diff_line("+ added line\n")
    printer.diff_line("- removed line\n")

    out, _ = capsys.readouterr()
    assert out == "+ added line\n- removed line\n"


def test_colored_printer_success(capsys):
    printer = isort.format.create_terminal_printer(color=True)
    printer.success("All good!")
    out, _ = capsys.readouterr()
    assert "SUCCESS" in out
    assert "All good!" in out
    assert colorama.Fore.GREEN in out


def test_colored_printer_error(capsys):
    printer = isort.format.create_terminal_printer(color=True)
    printer.error("Some error")
    _, err = capsys.readouterr()
    assert "ERROR" in err
    assert "Some error" in err
    assert colorama.Fore.RED in err


def test_colored_printer_diff(capsys):
    printer = isort.format.create_terminal_printer(color=True)
    printer.diff_line("+++ file1\n")
    printer.diff_line("--- file2\n")
    printer.diff_line("+ added line\n")
    printer.diff_line("normal line\n")
    printer.diff_line("- removed line\n")
    printer.diff_line("normal line\n")

    out, _ = capsys.readouterr()
    # No color added to lines with multiple + and -'s
    assert out.startswith("+++ file1\n--- file2\n")
    # Added lines are green
    assert colorama.Fore.GREEN + "+ added line" in out
    # Removed lines are red
    assert colorama.Fore.RED + "- removed line" in out
    # Normal lines are resetted back
    assert colorama.Style.RESET_ALL + "normal line" in out


def test_colored_printer_diff_output(capsys):
    output = StringIO()
    printer = isort.format.create_terminal_printer(color=True, output=output)
    printer.diff_line("a line\n")

    out, _ = capsys.readouterr()
    assert out == ""

    output.seek(0)
    assert output.read().startswith("a line\n")


@patch("isort.format.colorama_unavailable", True)
def test_colorama_not_available_handled_gracefully(capsys):
    with pytest.raises(SystemExit) as system_exit:
        _ = isort.format.create_terminal_printer(color=True)
    assert system_exit.value.code > 0
    _, err = capsys.readouterr()
    assert "colorama" in err
    assert "colors extra" in err


# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.


@given(
    file_input=st.text(),
    file_output=st.text(),
    file_path=st.one_of(st.none(), st.builds(Path)),
    output=st.one_of(st.none(), st.builds(StringIO, st.text())),
)
def test_fuzz_show_unified_diff(file_input, file_output, file_path, output):
    try:
        isort.format.show_unified_diff(
            file_input=file_input,
            file_output=file_output,
            file_path=file_path,
            output=output,
        )
    except UnicodeEncodeError:
        reject()
