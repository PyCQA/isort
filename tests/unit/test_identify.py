from io import StringIO
from typing import Any

from isort import Config, identify
from isort.identify import Import


def imports_in_code(code: str, **kwargs: Any) -> list[identify.Import]:
    return list(identify.imports(StringIO(code), **kwargs))


def test_top_only() -> None:
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


def test_top_doc_string() -> None:
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


def test_yield_and_raise_edge_cases() -> None:
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


def test_complex_examples() -> None:
    assert (
        len(
            imports_in_code(
                """
import a, b, c; import n

x = (
    1,
    2,
    3
)

import x
from os \\
    import path
from os (
    import path
)
from os import \\
    path
from os \\
    import (
        path
    )
from os import ( \\"""
            )
        )
        == 9
    )
    assert not imports_in_code("from os import \\")
    assert imports_in_code(
        """
from os \\
    import (
        system"""
    ) == [
        Import(
            line_number=2,
            indented=False,
            module="os",
            attribute="system",
            alias=None,
            cimport=False,
            file_path=None,
        )
    ]
    assert imports_in_code(
        """
from os \\
    cimport (
        system"""
    ) == [
        Import(
            line_number=2,
            indented=False,
            module="os",
            attribute="system",
            alias=None,
            cimport=True,
            file_path=None,
        )
    ]


def test_aliases() -> None:
    assert imports_in_code("import os as os")[0].alias == "os"
    assert not imports_in_code(
        "import os as os",
        config=Config(
            remove_redundant_aliases=True,
        ),
    )[0].alias

    assert imports_in_code("from os import path as path")[0].alias == "path"
    assert not imports_in_code(
        "from os import path as path", config=Config(remove_redundant_aliases=True)
    )[0].alias


def test_indented() -> None:
    assert not imports_in_code("import os")[0].indented
    assert imports_in_code("     import os")[0].indented
    assert imports_in_code("\timport os")[0].indented


def test_lazy_imports_identify_underlying_statement() -> None:
    """PEP 810 lazy imports are identified as the import statement after the ``lazy`` prefix."""
    lazy_from = imports_in_code("lazy from x import y\n")
    assert [i.statement() for i in lazy_from] == ["from x import y"]
    assert lazy_from[0].module == "x"

    lazy_straight = imports_in_code("lazy import z\n")
    assert [i.statement() for i in lazy_straight] == ["import z"]
    assert lazy_straight[0].module == "z"


def test_lazy_prefix_is_not_reported_as_an_import() -> None:
    """The ``lazy`` keyword itself must not surface as an extra import."""
    assert len(imports_in_code("lazy import z\n")) == 1
    assert len(imports_in_code("lazy from x import y\n")) == 1
    assert len(imports_in_code("lazy import z\nlazy import os\n")) == 2
