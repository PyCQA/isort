from io import StringIO
from typing import List

from isort import identify


def imports_in_code(code: str, **kwargs) -> List[identify.Import]:
    return list(identify.imports(StringIO(code, **kwargs)))


def test_yield_edge_cases():
    assert not imports_in_code(
        """
raise SomeException("Blah") \\
    from exceptionsInfo.popitem()[1]
"""
    )
    assert not imports_in_code(
        """
def generator_function():
    yield \\
        from other_function()[1]
"""
    )
    assert (
        len(
            imports_in_code(
                """
# one

# two


def function():
    # three \\
    import b
    import a
"""
            )
        )
        == 2
    )
    assert (
        len(
            imports_in_code(
                """
# one

# two


def function():
    raise \\
    import b
    import a
"""
            )
        )
        == 1
    )
    assert not imports_in_code(
        """
def generator_function():
    (
     yield
     from other_function()[1]
    )
"""
    )
    assert not imports_in_code(
        """
def generator_function():
    (
    (
    ((((
    (((((
    ((
    (((
     yield



     from other_function()[1]
    )))))))))))))
    )))
"""
    )
    assert (
        len(
            imports_in_code(
                """
def generator_function():
    import os

    yield \\
    from other_function()[1]
"""
            )
        )
        == 1
    )

    assert not imports_in_code(
        """
def generator_function():
    (
    (
    ((((
    (((((
    ((
    (((
     yield
"""
    )
    assert not imports_in_code(
        """
def generator_function():
    (
    (
    ((((
    (((((
    ((
    (((
     raise (
"""
    )
    assert not imports_in_code(
        """
def generator_function():
    (
    (
    ((((
    (((((
    ((
    (((
     raise \\
     from \\
"""
    )
