"""Tests for isort action comments, such as isort: skip"""

import isort


def test_isort_off_and_on():
    """Test so ensure isort: off action comment and associated on action comment work together"""

    # as top of file comment
    assert (
        isort.code(
            """# isort: off
import a
import a

# isort: on
import a
import a
"""
        )
        == """# isort: off
import a
import a

# isort: on
import a
"""
    )
    # as middle comment
    # When # isort: off follows an import section, the section before is
    # preserved as-is (not sorted or deduplicated), respecting the user-supplied
    # isort: off directive.
    assert (
        isort.code(
            """
import a
import a

# isort: off
import a
import a
"""
        )
        == """
import a
import a

# isort: off
import a
import a
"""
    )


def test_isort_off_preserves_preceding_imports_issue_2528():
    """Regression test for issue #2528.

    When `# isort: off` is followed by an import section, isort should not
    reformat or consolidate blank lines in the preceding import section.
    Previously, `import X` style statements were being modified despite
    `# isort: off` being present.
    See: https://github.com/PyCQA/isort/issues/2528
    """
    # Case from ufoLib2/tests/serde/test_json.py
    content = """import pytest

import ufoLib2.objects


# isort: off
pytest.importorskip("cattrs")


import ufoLib2.serde.json  # noqa: E402
"""
    assert isort.code(content) == content

    # Case from ufoLib2/tests/serde/test_msgpack.py
    content = """from pathlib import Path

import pytest

import ufoLib2.objects

# isort: off
pytest.importorskip("cattrs")
pytest.importorskip("msgpack")

import msgpack  # type: ignore  # noqa

import ufoLib2.serde.msgpack  # noqa: E402
"""
    assert isort.code(content) == content

    # Case from ufoLib2/tests/test_converters.py (already worked before)
    content = """from ufoLib2.objects.info import (
    GaspBehavior,
    WoffMetadataVendor,
)


# isort: off
cattrs = pytest.importorskip("cattrs")
from ufoLib2.converters import register_hooks, structure, unstructure  # noqa: E402
"""
    assert isort.code(content) == content
