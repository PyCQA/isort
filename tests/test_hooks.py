import os
from unittest.mock import MagicMock, patch

from isort import exceptions, hooks


def test_git_hook(src_dir):
    """Simple smoke level testing of git hooks"""

    # Ensure correct subprocess command is called
    with patch("subprocess.run", MagicMock()) as run_mock:
        hooks.git_hook()
        assert run_mock.called_once()
        assert run_mock.call_args[0][0] == [
            "git",
            "diff-index",
            "--cached",
            "--name-only",
            "--diff-filter=ACMRTUXB",
            "HEAD",
        ]

        hooks.git_hook(lazy=True)
        assert run_mock.called_once()
        assert run_mock.call_args[0][0] == [
            "git",
            "diff-index",
            "--name-only",
            "--diff-filter=ACMRTUXB",
            "HEAD",
        ]

    # Test with incorrectly sorted file returned from git
    with patch(
        "isort.hooks.get_lines", MagicMock(return_value=[os.path.join(src_dir, "main.py")])
    ) as run_mock:

        class FakeProcessResponse(object):
            stdout = b"import b\nimport a"

        with patch("subprocess.run", MagicMock(return_value=FakeProcessResponse())) as run_mock:
            with patch("isort.api", MagicMock(return_value=False)):
                hooks.git_hook(modify=True)

    # Test with skipped file returned from git
    with patch(
        "isort.hooks.get_lines", MagicMock(return_value=[os.path.join(src_dir, "main.py")])
    ) as run_mock:

        class FakeProcessResponse(object):
            stdout = b"# isort: skip-file\nimport b\nimport a\n"

        with patch("subprocess.run", MagicMock(return_value=FakeProcessResponse())) as run_mock:
            with patch("isort.api", MagicMock(side_effect=exceptions.FileSkipped("", ""))):
                hooks.git_hook(modify=True)
