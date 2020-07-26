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


def test_style_error():
    message = "ERROR"
    styled = isort.format.style_error(message)
    assert message in styled
    assert styled == colorama.Fore.RED + message + colorama.Style.RESET_ALL


def test_style_success():
    message = "OK"
    styled = isort.format.style_success(message)
    assert message in styled
    assert styled == colorama.Fore.GREEN + message + colorama.Style.RESET_ALL
