from isort.parso.parser import parse_code, remove_line


def test_remove_line_no_comments():
    code = """
import os
import sys
    """.lstrip('\n ').rstrip(' ')

    tree = parse_code(code)
    remove_line(tree, 2)

    assert tree.get_code() == """
import os
    """.lstrip('\n ').rstrip(' ')


def test_remove_line_with_a_comment():
    code = """
import os
# comment
    """.lstrip('\n ').rstrip(' ')

    tree = parse_code(code)
    remove_line(tree, 2)

    assert tree.get_code() == """
import os
    """.lstrip('\n ').rstrip(' ')
