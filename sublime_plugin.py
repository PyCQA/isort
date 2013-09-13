"""
    isort/sublime_plugin.py

    Provides a simple sublime plugin that enables the use of isort to sort Python imports
    in the currently selections in open sublime text file.

    Copyright (C) 2013  GuoJing

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

import sublime_plugin

from isort import SortImports


class IsortCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        contents = []
        selections = self.view.sel()
        for selection in selections:
            contents.append(self.view.substr(selection))
        contents = ''.join(contents)
        contents = contents + '\n'
        new_contents = SortImports(file_contents=contents).output
        if self.view.sel():
            lines = self.view.line(self.view.sel()[0])
            self.view.replace(edit, lines, new_contents)

