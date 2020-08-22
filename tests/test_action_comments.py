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
