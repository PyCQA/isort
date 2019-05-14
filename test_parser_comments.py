from isort.parso import fst
from isort.parso.parser import parse_code


def assert_roundtrip_invariant(code: str) -> None:
    tree = parse_code(code)
    fst._print(tree)
    assert tree.get_code() == code


def test_no_comments_found():
    assert_roundtrip_invariant('')
    assert_roundtrip_invariant('import os')
    assert_roundtrip_invariant('def func(): pass')
    code = """
import os
import sys    
"""
    assert_roundtrip_invariant(code)


def test_parse_one_comment():
    code = 'import os#hello'
    assert_roundtrip_invariant(code)


def test_parse_comment_inside_comment():
    code = 'import os#hello # not a second comment'
    assert_roundtrip_invariant(code)


def test_parse_two_comments_on_two_imports():
    code = """
import os  # hello
import sys  # world
    """
    assert_roundtrip_invariant(code)


def test_imports_under_functions():
    code = """
def func():
    # comment
    import os  # comment
"""
    assert_roundtrip_invariant(code)


def test_multiline_imports():
    code = """
from os import (  # hello
    pkg1, pkg2  # multiline
)  # main
    """
    assert_roundtrip_invariant(code)


def test_whitespaces_before_newline():
    code = """
# main  \n#hello \n\n
    """
    assert_roundtrip_invariant(code)


def test_different_comment_indents():
    code = """
#comment # not really second comment
#third comment
    # fourth comment
import django
    """.strip()
    assert_roundtrip_invariant(code)


def test_comments_only():
    code = """
# comment
    """.strip()

    assert_roundtrip_invariant(code)


def test_comment_import_comment():
    code = """
# comment
import os
# comment
""".lstrip()

    assert_roundtrip_invariant(code)
