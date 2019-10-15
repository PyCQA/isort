""""Very Abstract Syntax Tree

An abstract syntax tree that only recognizes the syntax features important for import sorting.
This allows isort to support every version of Python, including future versions, independent to
the version it is installed on.
"""
from isort.vast import Parser

__all__ = ["Parser"]
