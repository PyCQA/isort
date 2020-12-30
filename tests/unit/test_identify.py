from io import StringIO
from typing import List

from isort import identify


def imports_in_code(code: str, **kwargs) -> List[identify.Import]:
    return list(identify.imports(StringIO(code), **kwargs))


def test_top_only():
    imports_in_function = """
import abc

def xyz():
    import defg
"""
    assert len(imports_in_code(imports_in_function)) == 2
    assert len(imports_in_code(imports_in_function, top_only=True)) == 1

    imports_after_class = """
import abc

class MyObject:
    pass

import defg
"""
    assert len(imports_in_code(imports_after_class)) == 2
    assert len(imports_in_code(imports_after_class, top_only=True)) == 1


def test_top_doc_string():
    assert (
        len(
            imports_in_code(
                '''
#! /bin/bash import x
"""import abc
from y import z
"""
import abc
'''
            )
        )
        == 1
    )


def test_yield_and_raise_edge_cases():
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
    assert (
        len(
            imports_in_code(
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
    import c

    import abc
    import xyz
"""
            )
        )
        == 2
    )
