from unittest.mock import MagicMock, patch

import colorama
import pytest
from hypothesis_auto import auto_pytest_magic

import isort.format

auto_pytest_magic(isort.format.show_unified_diff, auto_allow_exceptions_=(UnicodeEncodeError,))


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
    out, _ = capsys.readouterr()
    assert out == "ERROR: Some error\n"


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
    out, _ = capsys.readouterr()
    assert "ERROR" in out
    assert "Some error" in out
    assert colorama.Fore.RED in out


@patch("isort.format.colorama_unavailable", True)
def test_colorama_not_available_handled_gracefully(capsys):
    with pytest.raises(SystemExit) as system_exit:
        _ = isort.format.create_terminal_printer(color=True)
    assert system_exit.value.code > 0
    _, err = capsys.readouterr()
    assert "colorama" in err
    assert "colors extra" in err
