""""VERY Abstract Syntax Tree (VAST)

An abstract syntax tree that only recognizes the syntax features important for import sorting.
This allows isort to support every version of Python, including future versions, independent of
the version it is installed on.
"""
from isort.vast import Parser

__all__ = ["Parser"]
