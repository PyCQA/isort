""" Sorts Python import definitions, and groups them based on type (stdlib, third-party, local).

isort/isort_kate_plugin.py

Provides a simple kate plugin that enables the use of isort to sort Python imports
in the currently open kate file.

Copyright (C) 2013  Timothy Edmund Crosley

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

"""
import os

import kate

from isort import SortImports

try:
    from PySide import QtGui
except ImportError:
    from PyQt4 import QtGui


def sort_kate_imports(add_imports=(), remove_imports=()):
    """Sorts imports within Kate while maintaining cursor position and selection, even if length of file changes."""
    document = kate.activeDocument()
    view = document.activeView()
    position = view.cursorPosition()
    selection = view.selectionRange()
    sorter = SortImports(file_contents=document.text(), add_imports=add_imports, remove_imports=remove_imports,
                         settings_path=os.path.dirname(os.path.abspath(str(document.url().path()))))
    document.setText(sorter.output)
    position.setLine(position.line() + sorter.length_change)
    if selection:
        start = selection.start()
        start.setLine(start.line() + sorter.length_change)
        end = selection.end()
        end.setLine(end.line() + sorter.length_change)
        selection.setRange(start, end)
        view.setSelection(selection)
    view.setCursorPosition(position)


@kate.action
def sort_imports():
    """Sort Imports"""
    sort_kate_imports()


@kate.action
def add_imports():
    """Add Imports"""
    text, ok = QtGui.QInputDialog.getText(None,
                                          'Add Import',
                                          'Enter an import line to add (example: from os import path or os.path):')
    if ok:
        sort_kate_imports(add_imports=text.split(";"))


@kate.action
def remove_imports():
    """Remove Imports"""
    text, ok = QtGui.QInputDialog.getText(None,
                                          'Remove Import',
                                          'Enter an import line to remove (example: os.path or from os import path):')
    if ok:
        sort_kate_imports(remove_imports=text.split(";"))
