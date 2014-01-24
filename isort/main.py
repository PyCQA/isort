#! /usr/bin/env python
'''  Tool for sorting imports alphabetically, and automatically separated into sections.

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

'''
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import os
import sys

from pies.overrides import *

from isort import __version__, SECTION_NAMES, SortImports


def iter_source_code(paths):
    """Iterate over all Python source files defined in paths."""
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.py'):
                        yield os.path.join(dirpath, filename)
        else:
            yield path


def main():
    parser = argparse.ArgumentParser(description='Sort Python import definitions alphabetically '
                                                 'within logical sections.')
    parser.add_argument('files', nargs='+', help='One or more Python source files that need their imports sorted.')
    parser.add_argument('-l', '--lines', help='The max length of an import line (used for wrapping long imports).',
                        dest='line_length', type=int)
    parser.add_argument('-s', '--skip', help='Files that sort imports should skip over.', dest='skip', action='append')
    parser.add_argument('-t', '--top', help='Force specific imports to the top of their appropriate section.',
                        dest='force_to_top', action='append')
    parser.add_argument('-b', '--builtin', dest='known_standard_library', action='append',
                        help='Force sortImports to recognize a module as part of the python standard library.')
    parser.add_argument('-o', '--thirdparty', dest='known_third_party', action='append',
                        help='Force sortImports to recognize a module as being part of a third party library.')
    parser.add_argument('-p', '--project', dest='known_first_party', action='append',
                        help='Force sortImports to recognize a module as being part of the current python project.')
    parser.add_argument('-m', '--multi_line', dest='multi_line_output', type=int, choices=[0, 1, 2, 3, 4, 5],
                        help='Multi line output (0-grid, 1-vertical, 2-hanging, 3-vert-hanging, 4-vert-grid, '
                            '5-vert-grid-grouped).')
    parser.add_argument('-i', '--indent', help='String to place for indents defaults to "    " (4 spaces).',
                        dest='indent', type=str)
    parser.add_argument('-a', '--add_import', dest='add_imports', action='append',
                        help='Adds the specified import line to all files, '
                             'automatically determining correct placement.')
    parser.add_argument('-r', '--remove_import', dest='remove_imports', action='append',
                        help='Removes the specified import from all files.')
    parser.add_argument('-ls', '--length_sort', help='Sort imports by their string length.',
                        dest='length_sort', action='store_true', default=False)
    parser.add_argument('-d', '--stdout', help='Force resulting output to stdout, instead of in-place.',
                        dest='write_to_stdout', action='store_true')
    parser.add_argument('-c', '--check-only', action='store_true', default=False, dest="check",
                        help='Checks the file for unsorted imports and prints them to the '
                             'command line without modifying the file.')
    parser.add_argument('-sl', '--force_single_line_imports', dest='force_single_line', action='store_true',
                        help='Forces all from imports to appear on their own line')
    parser.add_argument('-sd', '--section-default', dest='default_section',
                        help='Sets the default section for imports (by default FIRSTPARTY) options: ' +
                        str(SECTION_NAMES))
    parser.add_argument('-df', '--diff', dest='show_diff', default=False, action='store_true',
                        help="Prints a diff of all the changes isort would make to a file, instead of "
                             "changing it in place")
    parser.add_argument('-e', '--balanced', dest='balanced_wrapping', action='store_true',
                        help='Balances wrapping to produce the most consistent line length possible')
    parser.add_argument('-rc', '--recursive', dest='recursive', action='store_true',
                        help='Recursively look for Python files of which to sort imports')
    parser.add_argument('-v', '--version', action='version', version='isort {0}'.format(__version__))

    arguments = dict((key, value) for (key, value) in itemsview(vars(parser.parse_args())) if value)
    file_names = arguments.pop('files', [])

    if file_names == ['-']:
        SortImports(file_contents=sys.stdin.read(), write_to_stdout=True, **arguments)
    else:
        wrong_sorted_files = False
        if arguments.get('recursive', False):
            file_names = iter_source_code(file_names)
        for file_name in file_names:
            try:
                incorrectly_sorted = SortImports(file_name, **arguments).incorrectly_sorted
                if arguments.get('check', False) and incorrectly_sorted:
                    wrong_sorted_files = True
            except IOError as e:
                print("WARNING: Unable to parse file {0} due to {1}".format(file_name, e))
        if wrong_sorted_files:
            exit(1)


if __name__ == "__main__":
    main()
