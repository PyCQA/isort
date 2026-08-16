import os
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

import pytest

from isort import exceptions, hooks
from isort._version import _IS_COMPILED


def test_git_hook(src_dir):
    """Simple smoke level testing of git hooks"""

    # Ensure correct subprocess command is called
    with patch(
        "subprocess.run", return_value=CompletedProcess("command", returncode=0, stdout=b"")
    ) as run_mock:
        hooks.git_hook()
        run_mock.assert_called_once()
        assert run_mock.call_args[0][0] == [
            "git",
            "diff-index",
            "--cached",
            "--name-only",
            "--diff-filter=ACMRTUXB",
            "HEAD",
        ]

    with patch(
        "subprocess.run", return_value=CompletedProcess("command", returncode=0, stdout=b"")
    ) as run_mock:
        hooks.git_hook(lazy=True)
        run_mock.assert_called_once()
        assert run_mock.call_args[0][0] == [
            "git",
            "diff-index",
            "--name-only",
            "--diff-filter=ACMRTUXB",
            "HEAD",
        ]

    # Test that non python files aren't processed
    with patch(
        "subprocess.run",
        return_value=CompletedProcess(
            "command", returncode=0, stdout=b"README.md\nsetup.cfg\nLICDENSE\nmkdocs.yml\ntest"
        ),
    ) as run_mock:
        hooks.git_hook(modify=True)
        run_mock.assert_called_once()

    # Test with incorrectly sorted file returned from git
    file_name = os.path.join(src_dir, "main.py")
    with patch(
        "subprocess.run",
        side_effect=[
            CompletedProcess("command", returncode=0, stdout=file_name.encode()),
            CompletedProcess("command", returncode=0, stdout=b"import b,a"),
        ],
    ) as run_mock:
        errors = hooks.git_hook(modify=True, strict=True)
        assert run_mock.call_count == 2
        assert errors == 1


@pytest.mark.skipif(reason="Can't use these mocks in mypyc-compiled code.", condition=_IS_COMPILED)
def test_git_hook_with_mocks(src_dir: str) -> None:
    """
    Additional tests for the git hook, split off to allow running some when compiled.
    """
    mock_main_py = MagicMock(return_value=[os.path.join(src_dir, "main.py")])

    mock_imperfect = MagicMock()
    mock_imperfect.return_value.stdout = b"import b\nimport a"

    # Test with sorted file returned from git and modify=False
    with patch("isort.hooks.get_lines", mock_main_py):
        with patch("subprocess.run", mock_imperfect):
            with patch("isort.api.sort_file", MagicMock(return_value=False)) as api_mock:
                hooks.git_hook(modify=False)
                api_mock.assert_not_called()

    # Test with skipped file returned from git
    with patch("isort.hooks.get_lines", MagicMock(return_value=[os.path.join(src_dir, "main.py")])):

        class FakeProcessResponse:
            stdout = b"# isort: skip-file\nimport b\nimport a\n"

        with patch("subprocess.run", MagicMock(return_value=FakeProcessResponse())):
            with patch("isort.api", MagicMock(side_effect=exceptions.FileSkipped("", ""))):
                hooks.git_hook(modify=True)


def test_git_hook_lazy(tmpdir):
    # Write an actual unsorted file to disk & check that `lazy=True` spots it

    has_problems = tmpdir.join("test_has_problems.py")
    has_problems.write_text("import b\nimport a\n", "utf8")

    with patch(
        "subprocess.run",
        side_effect=[
            CompletedProcess("command", returncode=0, stdout=str(has_problems).encode()),
            # Second call to subprocess.run should not be made when lazy=True
            RuntimeError("donotcall"),
        ],
    ) as run_mock:
        found_errors = hooks.git_hook(lazy=True, strict=True)
        # subprocess.run (via get_output) should not be called when lazy=True
        # because we're not asking git for the staged content
        assert run_mock.call_count == 1

    assert found_errors == 1


@pytest.mark.skipif(reason="Can't use these mocks in mypyc-compiled code.", condition=_IS_COMPILED)
def test_git_hook_uses_the_configuration_file_specified_in_settings_path(tmp_path: Path) -> None:
    subdirectory_path = tmp_path / "subdirectory"
    configuration_file_path = subdirectory_path / ".isort.cfg"

    # Inserting the modified file in the parent directory of the configuration file ensures that it
    # will not be found by the normal search routine
    modified_file_path = configuration_file_path.parent.parent / "somefile.py"

    # This section will be used to check that the configuration file was indeed loaded
    section = "testsection"

    os.mkdir(subdirectory_path)
    with open(configuration_file_path, "w") as fd:
        fd.write("[isort]\n")
        fd.write(f"sections={section}")

    with open(modified_file_path, "w") as fd:
        pass

    files_modified = [str(modified_file_path.absolute())]
    with patch("isort.hooks.get_lines", MagicMock(return_value=files_modified)):
        with patch("isort.hooks.get_output", MagicMock(return_value="")):
            with patch("isort.api.check_code_string", MagicMock()) as run_mock:
                hooks.git_hook(settings_file=str(configuration_file_path))

                assert run_mock.call_args[1]["config"].sections == (section,)
