"""
    isort/kate_plugin.py

    Provides a simple kate plugin that enables the use of isort to sort Python imports
    in the currently open kate file.

    Copyright (C) 2013  Timothy Edmund Crosley

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from isort import SortImports

import kate

try:
    from PySide import QtGui
except ImportError:
    from PyQt4 import QtGui


@kate.action(text="Sort Imports", shortcut="Ctrl+[", menu="Python")
def sort_imports():
    document = kate.activeDocument()
    view = document.activeView()
    position = view.cursorPosition()
    document.setText(SortImports(file_contents=document.text()).output)
    view.setCursorPosition(position)


@kate.action(text="Add Import", shortcut="Ctrl+]", menu="Python")
def add_imports():
    text, ok = QtGui.QInputDialog.getText(None,
                                          'Add Import',
                                          'Enter an import line to add (example: from os import path):')
    if ok:
        document = kate.activeDocument()
        view = document.activeView()
        position = view.cursorPosition()
        document.setText(SortImports(file_contents=document.text(), add_imports=text.split(";")).output)
        view.setCursorPosition(position)


@kate.action(text="Remove Import", shortcut="Ctrl+Shift+]", menu="Python")
def remove_imports():
    text, ok = QtGui.QInputDialog.getText(None,
                                          'Remove Import',
                                          'Enter an import line to remove (example: os.path):')
    if ok:
        document = kate.activeDocument()
        view = document.activeView()
        position = view.cursorPosition()
        document.setText(SortImports(file_contents=document.text(), remove_imports=text.split(";")).output)
        view.setCursorPosition(position)
