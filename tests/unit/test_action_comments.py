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

# isort: off
import a
import a
"""
    )


def test_isort_off_honors_import_and_from_imports_issue_2528():
    """Regression test for issue #2528: ensure isort: off honors both import and from import statements.
    
    Previously, there was a differential behavior where isort: off would respect from imports but not
    plain import statements. This test ensures both import types are properly handled.
    """
    # Test plain imports with isort: off
    assert (
        isort.code(
            """# isort: off
import z
import a
import b

# isort: on
import c
import d
"""
        )
        == """# isort: off
import z
import a
import b

# isort: on
import c
import d
"""
    )

    # Test from imports with isort: off
    assert (
        isort.code(
            """# isort: off
from z import foo
from a import bar
from b import baz

# isort: on
from c import qux
from d import quux
"""
        )
        == """# isort: off
from z import foo
from a import bar
from b import baz

# isort: on
from c import qux
from d import quux
"""
    )

    # Test mixed imports with isort: off - both types should be preserved
    assert (
        isort.code(
            """# isort: off
import z
from a import foo
import b
from c import bar

# isort: on
import e
from f import baz
"""
        )
        == """# isort: off
import z
from a import foo
import b
from c import bar

# isort: on
import e
from f import baz
"""
    )

    # Test when isort: off appears mid-file between imports
    assert (
        isort.code(
            """import a
import c

# isort: off
import z
from b import foo
import b

# isort: on
import e
from f import baz
"""
        )
        == """import a
import c

# isort: off
import z
from b import foo
import b

# isort: on
import e
from f import baz
"""
    )

    # Test isort: off without space after # (e.g., #isort: off)
    assert (
        isort.code(
            """#isort: off
import z
import a
import b

#isort: on
import c
import d
"""
        )
        == """#isort: off
import z
import a
import b

#isort: on
import c
import d
"""
    )

    # Test isort: off without space after isort (e.g., # isort:off)
    assert (
        isort.code(
            """# isort:off
import z
from a import foo

# isort:on
import b
"""
        )
        == """# isort:off
import z
from a import foo

# isort:on
import b
"""
    )
