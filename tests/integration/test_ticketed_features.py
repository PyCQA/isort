"""Tests that need installation of other packages."""

# TODO: find a way to install example-isort-formatting-plugin to pass tests
# from io import StringIO

# import pytest

# import isort
# from isort import api, exceptions


# def test_isort_supports_formatting_plugins():
#     """Test to ensure isort provides a way to create and share formatting plugins.
#     See: https://github.com/pycqa/isort/issues/1353.
#     """
#     # formatting plugin
#     assert isort.code("import a", formatter="example") == "import a\n"
#     # non-existent plugin
#     with pytest.raises(exceptions.FormattingPluginDoesNotExist):
#         assert isort.code("import a", formatter="madeupfake") == "import a\n"


# def test_isort_literals_issue_1358():
#     assert (
#         isort.code(
#             """
# import x
# import a


# # isort: list
# __all__ = ["b", "a", "b"]

# # isort: unique-list
# __all__ = ["b", "a", "b"]

# # isort: tuple
# __all__ = ("b", "a", "b")

# # isort: unique-tuple
# __all__ = ("b", "a", "b")

# # isort: set
# __all__ = {"b", "a", "b"}


# def method():
#     # isort: list
#     x = ["b", "a"]


# # isort: dict
# y = {"z": "z", "b": "b", "b": "c"}"""
#         )
#         == """
# import a
# import x

# # isort: list
# __all__ = ['a', 'b', 'b']

# # isort: unique-list
# __all__ = ['a', 'b']

# # isort: tuple
# __all__ = ('a', 'b', 'b')

# # isort: unique-tuple
# __all__ = ('a', 'b')

# # isort: set
# __all__ = {'a', 'b'}


# def method():
#     # isort: list
#     x = ['a', 'b']


# # isort: dict
# y = {'b': 'c', 'z': 'z'}"""
#     )
#     assert (
#         isort.code(
#             """
# import x
# import a


# # isort: list
# __all__ = ["b", "a", "b"]

# # isort: unique-list
# __all__ = ["b", "a", "b"]

# # isort: tuple
# __all__ = ("b", "a", "b")

# # isort: unique-tuple
# __all__ = ("b", "a", "b")

# # isort: set
# __all__ = {"b", "a", "b"}


# def method():
#     # isort: list
#     x = ["b", "a"]


# # isort: assignments
# d = 1
# b = 2
# a = 3

# # isort: dict
# y = {"z": "z", "b": "b", "b": "c"}""",
#             formatter="example",
#         )
#         == """
# import a
# import x

# # isort: list
# __all__ = ["a", "b", "b"]

# # isort: unique-list
# __all__ = ["a", "b"]

# # isort: tuple
# __all__ = ("a", "b", "b")

# # isort: unique-tuple
# __all__ = ("a", "b")

# # isort: set
# __all__ = {"a", "b"}


# def method():
#     # isort: list
#     x = ["a", "b"]


# # isort: assignments
# a = 3
# b = 2
# d = 1

# # isort: dict
# y = {"b": "c", "z": "z"}"""
#     )
#     assert api.sort_stream(
#         input_stream=StringIO(
#             """
# import a
# import x

# # isort: list
# __all__ = ["b", "a", "b"]

# # isort: unique-list
# __all__ = ["b", "a", "b"]

# # isort: tuple
# __all__ = ("b", "a", "b")

# # isort: unique-tuple
# __all__ = ("b", "a", "b")

# # isort: set
# __all__ = {"b", "a", "b"}


# def method():
#     # isort: list
#     x = ["b", "a"]


# # isort: assignments
# d = 1
# b = 2
# a = 3

# # isort: dict
# y = {"z": "z", "b": "b", "b": "c"}""",
#         ),
#         output_stream=StringIO(),
#     )
