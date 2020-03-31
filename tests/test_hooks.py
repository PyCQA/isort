from io import BytesIO
from unittest.mock import MagicMock, patch

from isort import hooks


def test_git_hook():
    """Simple smoke level testing of git hooks"""

    # Ensure correct subprocess command is called
    with patch("subprocess.run", MagicMock()) as run_mock:
        hooks.git_hook()
        assert run_mock.called_with(
            ["git", "diff-index", "--cached", "--name-only", "--diff-filter=ACMRTUXB HEAD"]
        )

    # Test with incorrectly sorted file returned from git
    with patch("isort.hooks.get_lines", MagicMock(return_value=["isort/isort.py"])) as run_mock:

        class FakeProecssResponse(object):
            stdout = b"import b\nimport a"

        with patch("subprocess.run", MagicMock(return_value=FakeProecssResponse())) as run_mock:
            with patch("isort.hooks.api", MagicMock()):
                hooks.git_hook(modify=True)
