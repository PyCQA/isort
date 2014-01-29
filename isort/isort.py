"""isort.py.

Exposes a simple library to sort through imports within Python code

usage:
    SortImports(file_name)
or:
    sorted = SortImports(file_contents=file_contents).output

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
from __future__ import absolute_import, division, print_function, unicode_literals

import codecs
import copy
import itertools
import os
from collections import namedtuple
from difflib import unified_diff
from sys import path as PYTHONPATH
from sys import stderr, stdout

from natsort import natsorted
from pies.overrides import *

from . import settings

SECTION_NAMES = ("FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER")
SECTIONS = namedtuple('Sections', SECTION_NAMES)(*range(len(SECTION_NAMES)))


class SortImports(object):
    incorrectly_sorted = False

    def __init__(self, file_path=None, file_contents=None, write_to_stdout=False, check=False,
                 show_diff=False, settings_path=None, **setting_overrides):

        if not settings_path and file_path:
            settings_path = os.path.dirname(os.path.abspath(file_path))
        settings_path = settings_path or os.getcwd()

        self.config = settings.from_path(settings_path).copy()
        self.config.update(setting_overrides)

        indent = str(self.config['indent'])
        if indent.isdigit():
            indent = " " * int(indent)
        else:
            indent = indent.strip("'").strip('"')
            if indent.lower() == "tab":
                indent = "\t"
        self.config['indent'] = indent

        self.remove_imports = [self._format_simplified(removal) for removal in self.config.get('remove_imports', [])]
        self.add_imports = [self._format_natural(addition) for addition in self.config.get('add_imports', [])]
        self._section_comments = ["# " + value for key, value in itemsview(self.config) if
                                  key.startswith('import_heading') and value]

        file_name = file_path
        self.file_path = file_path or ""
        if file_path:
            file_path = os.path.abspath(file_path)
            if self._should_skip(file_path):
                print("WARNING: {0} was skipped as it's listed in 'skip' setting".format(file_path), file=stderr)
                file_contents = None
            else:
                self.file_path = file_path
                with open(file_path) as file_to_import_sort:
                    file_contents = file_to_import_sort.read()
                    file_contents = PY2 and file_contents.decode('utf8') or file_contents

        if file_contents is None or ("isort:" + "skip_file") in file_contents:
            return

        self.in_lines = file_contents.split("\n")
        self.original_length = len(self.in_lines)
        for add_import in self.add_imports:
            self.in_lines.append(add_import)
        self.number_of_lines = len(self.in_lines)

        self.out_lines = []
        self.imports = {}
        self.as_map = {}
        for section in itertools.chain(SECTIONS, self.config['forced_separate']):
            self.imports[section] = {'straight': set(), 'from': {}}

        self.index = 0
        self.import_index = -1
        self._first_comment_index_start = -1
        self._first_comment_index_end = -1
        self._parse()
        if self.import_index != -1:
            self._add_formatted_imports()

        self.length_change = len(self.out_lines) - self.original_length
        while self.out_lines and self.out_lines[-1].strip() == "":
            self.out_lines.pop(-1)
        self.out_lines.append("")

        self.output = "\n".join(self.out_lines)
        if check:
            if self.output == file_contents:
                print("SUCCESS: {0} Everything Looks Good!".format(self.file_path))
            else:
                print("ERROR: {0} Imports are incorrectly sorted.".format(self.file_path), file=stderr)
                self.incorrectly_sorted = True
            return

        if show_diff:
            for line in unified_diff(file_contents.splitlines(1), self.output.splitlines(1),
                                     fromfile=self.file_path + ':before', tofile=self.file_path + ':after'):
                stdout.write(line)
        elif write_to_stdout:
            stdout.write(self.output)
        elif file_name:
            with codecs.open(self.file_path, encoding='utf-8', mode='w') as output_file:
                output_file.write(self.output)

    def _should_skip(self, filename):
        """Returns True if the file should be skipped based on the loaded settings."""
        if filename in self.config['skip']:
            return True

        position = os.path.split(filename)
        while position[1]:
            if position[1] in self.config['skip']:
                return True
            position = os.path.split(position[0])

    def place_module(self, moduleName):
        """Tries to determine if a module is a python std import, third party import, or project code:

        if it can't determine - it assumes it is project code

        """
        if moduleName.startswith("."):
            return SECTIONS.LOCALFOLDER

        index = moduleName.find('.')
        if index:
            firstPart = moduleName[:index]
        else:
            firstPart = None

        for forced_separate in self.config['forced_separate']:
            if moduleName.startswith(forced_separate):
                return forced_separate

        if moduleName == "__future__" or (firstPart == "__future__"):
            return SECTIONS.FUTURE
        elif moduleName in self.config['known_standard_library'] or \
                (firstPart in self.config['known_standard_library']):
            return SECTIONS.STDLIB
        elif moduleName in self.config['known_third_party'] or (firstPart in self.config['known_third_party']):
            return SECTIONS.THIRDPARTY
        elif moduleName in self.config['known_first_party'] or (firstPart in self.config['known_first_party']):
            return SECTIONS.FIRSTPARTY

        for prefix in PYTHONPATH:
            module_path = "/".join((prefix, moduleName.replace(".", "/")))
            package_path = "/".join((prefix, moduleName.split(".")[0]))
            if (os.path.exists(module_path + ".py") or os.path.exists(module_path + ".so") or
               (os.path.exists(package_path) and os.path.isdir(package_path))):
                if "site-packages" in prefix or "dist-packages" in prefix:
                    return SECTIONS.THIRDPARTY
                elif "python2" in prefix.lower() or "python3" in prefix.lower():
                    return SECTIONS.STDLIB
                else:
                    return SECTIONS.FIRSTPARTY

        return SECTION_NAMES.index(self.config['default_section'])

    def _get_line(self):
        """Returns the current line from the file while incrementing the index."""
        line = self.in_lines[self.index]
        self.index += 1
        return line

    @staticmethod
    def _import_type(line):
        """If the current line is an import line it will return its type (from or straight)"""
        if "isort:skip" in line:
            return
        elif line.startswith('import '):
            return "straight"
        elif line.startswith('from ') and "import" in line:
            return "from"

    def _at_end(self):
        """returns True if we are at the end of the file."""
        return self.index == self.number_of_lines

    @staticmethod
    def _module_key(module_name, config):
        module_name = str(module_name).lower()
        return "{0}{1}".format(module_name in config['force_to_top'] and "A" or "B",
                               config['length_sort'] and (str(len(module_name)) + ":" + module_name) or module_name)

    def _add_formatted_imports(self):
        """Adds the imports back to the file.

        (at the index of the first import) sorted alphabetically and split between groups

        """
        output = []
        for section in itertools.chain(SECTIONS, self.config['forced_separate']):
            straight_modules = list(self.imports[section]['straight'])
            straight_modules = natsorted(straight_modules, key=lambda key: self._module_key(key, self.config))
            section_output = []

            for module in straight_modules:
                if module in self.remove_imports:
                    continue

                if module in self.as_map:
                    section_output.append("import {0} as {1}".format(module, self.as_map[module]))
                else:
                    section_output.append("import {0}".format(module))

            from_modules = list(self.imports[section]['from'].keys())
            from_modules = natsorted(from_modules, key=lambda key: self._module_key(key, self.config))
            for module in from_modules:
                if module in self.remove_imports:
                    continue

                import_start = "from {0} import ".format(module)
                from_imports = list(self.imports[section]['from'][module])
                from_imports = natsorted(from_imports, key=lambda key: self._module_key(key, self.config))
                if self.remove_imports:
                    from_imports = [line for line in from_imports if not "{0}.{1}".format(module, line) in
                                    self.remove_imports]

                for from_import in copy.copy(from_imports):
                    import_as = self.as_map.get(module + "." + from_import, False)
                    if import_as:
                        section_output.append(import_start + "{0} as {1}".format(from_import, import_as))
                        from_imports.remove(from_import)

                if from_imports:
                    if "*" in from_imports:
                        import_statement = "{0}*".format(import_start)
                    elif self.config['force_single_line']:
                        import_statement = import_start + from_imports.pop(0)
                        for from_import in from_imports:
                            import_statement += "\n{0}{1}".format(import_start, from_import)
                    else:
                        import_statement = import_start + (", ").join(from_imports)
                        if len(import_statement) > self.config['line_length'] and len(from_imports) > 1:
                            output_mode = settings.WrapModes._fields[self.config.get('multi_line_output', 0)].lower()
                            formatter = getattr(self, "_output_" + output_mode, self._output_grid)
                            dynamic_indent = " " * (len(import_start) + 1)
                            indent = self.config['indent']
                            line_length = self.config['line_length']
                            import_statement = formatter(import_start, copy.copy(from_imports),
                                                         dynamic_indent, indent, line_length)
                            if self.config['balanced_wrapping']:
                                lines = import_statement.split("\n")
                                line_count = len(lines)
                                minimum_length = min([len(line) for line in lines[:-1]])
                                new_import_statement = import_statement
                                while len(lines[-1]) < minimum_length and len(lines) == line_count and line_length > 10:
                                    import_statement = new_import_statement
                                    line_length -= 1
                                    new_import_statement = formatter(import_start, copy.copy(from_imports),
                                                                     dynamic_indent, indent, line_length)
                                    lines = new_import_statement.split("\n")

                    section_output.append(import_statement)

            if section_output:
                section_name = section
                if section in SECTIONS:
                    section_name = SECTION_NAMES[section]
                section_title = self.config.get('import_heading_' + str(section_name).lower(), '')
                if section_title:
                    section_output.insert(0, "# " + section_title)
                output += section_output + ['']

        while [character.strip() for character in output[-1:]] == [""]:
            output.pop()

        output_at = 0
        if self.import_index < self.original_length:
            output_at = self.import_index
        elif self._first_comment_index_end != -1 and self._first_comment_index_start <= 2:
            output_at = self._first_comment_index_end
        self.out_lines[output_at:0] = output

        imports_tail = output_at + len(output)
        while [character.strip() for character in self.out_lines[imports_tail: imports_tail + 1]] == [""]:
            self.out_lines.pop(imports_tail)

        if len(self.out_lines) > imports_tail:
            next_construct = self.out_lines[imports_tail]
            if next_construct.startswith("def") or next_construct.startswith("class") or \
               next_construct.startswith("@"):
                self.out_lines[imports_tail:0] = ["", ""]
            else:
                self.out_lines[imports_tail:0] = [""]

    @staticmethod
    def _output_grid(statement, imports, white_space, indent, line_length):
        statement += "(" + imports.pop(0)
        while imports:
            next_import = imports.pop(0)
            next_statement = statement + ", " + next_import
            if len(next_statement.split("\n")[-1]) + 1 > line_length:
                next_statement = "{0},\n{1}{2}".format(statement, white_space, next_import)
            statement = next_statement
        return statement + ")"

    @staticmethod
    def _output_vertical(statement, imports, white_space, indent, line_length):
        return "{0}({1})".format(statement, (",\n" + white_space).join(imports))

    @staticmethod
    def _output_hanging_indent(statement, imports, white_space, indent, line_length):
        statement += imports.pop(0)
        while imports:
            next_import = imports.pop(0)
            next_statement = statement + ", " + next_import
            if len(next_statement.split("\n")[-1]) + 3 > line_length:
                next_statement = "{0}, \\\n{1}{2}".format(statement, indent, next_import)
            statement = next_statement
        return statement

    @staticmethod
    def _output_vertical_hanging_indent(statement, imports, white_space, indent, line_length):
        return "{0}(\n{1}{2}\n)".format(statement, indent, (",\n" + indent).join(imports))

    @staticmethod
    def _output_vertical_grid_common(statement, imports, white_space, indent, line_length):
        statement += "(\n" + indent + imports.pop(0)
        while imports:
            next_import = imports.pop(0)
            next_statement = "{0}, {1}".format(statement, next_import)
            if len(next_statement.split("\n")[-1]) + 1 > line_length:
                next_statement = "{0},\n{1}{2}".format(statement, indent, next_import)
            statement = next_statement
        return statement

    @classmethod
    def _output_vertical_grid(cls, statement, imports, white_space, indent, line_length):
        return cls._output_vertical_grid_common(statement, imports, white_space, indent, line_length) + ")"

    @classmethod
    def _output_vertical_grid_grouped(cls, statement, imports, white_space, indent, line_length):
        return cls._output_vertical_grid_common(statement, imports, white_space, indent, line_length) + "\n)"

    @staticmethod
    def _strip_comments(line):
        """Removes comments from import line."""
        comment_start = line.find("#")
        if comment_start != -1:
            print("Removing comment(%s) so imports can be sorted correctly" % line[comment_start:], file=stderr)
            line = line[:comment_start]

        return line

    @staticmethod
    def _format_simplified(import_line):
        import_line = import_line.strip()
        if import_line.startswith("from "):
            import_line = import_line.replace("from ", "")
            import_line = import_line.replace(" import ", ".")
        elif import_line.startswith("import "):
            import_line = import_line.replace("import ", "")

        return import_line

    @staticmethod
    def _format_natural(import_line):
        import_line = import_line.strip()
        if not import_line.startswith("from ") and not import_line.startswith("import "):
            if not "." in import_line:
                return "import {0}".format(import_line)
            parts = import_line.split(".")
            end = parts.pop(-1)
            return "from {0} import {1}".format(".".join(parts), end)

        return import_line

    def _parse(self):
        """Parses a python file taking out and categorizing imports."""
        in_quote = False
        while not self._at_end():
            line = self._get_line()
            skip_line = in_quote
            if '"' in line or "'" in line:
                index = 0
                if self._first_comment_index_start == -1:
                    self._first_comment_index_start = self.index
                while index < len(line):
                    if line[index] == "\\":
                        index += 1
                    elif in_quote:
                        if line[index:index + len(in_quote)] == in_quote:
                            in_quote = False
                            if self._first_comment_index_end == -1:
                                self._first_comment_index_end = self.index
                    elif line[index] in ("'", '"'):
                        long_quote = line[index:index + 3]
                        if long_quote in ('"""', "'''"):
                            in_quote = long_quote
                            index += 2
                        else:
                            in_quote = line[index]
                    elif line[index] == "#":
                        break
                    index += 1

            if line in self._section_comments and not skip_line:
                if self.import_index == -1:
                    self.import_index = self.index - 1
                continue

            import_type = self._import_type(line)
            if not import_type or skip_line:
                self.out_lines.append(line)
                continue

            if self.import_index == -1:
                self.import_index = self.index - 1

            import_string = self._strip_comments(line)
            if "(" in line and not self._at_end():
                while not line.strip().endswith(")") and not self._at_end():
                    line = self._strip_comments(self._get_line())
                    import_string += "\n" + line
            else:
                while line.strip().endswith("\\"):
                    line = self._strip_comments(self._get_line())
                    import_string += "\n" + line

            import_string = import_string.replace("_import", "[[i]]")
            for remove_syntax in ['\\', '(', ')', ",", 'from ', 'import ']:
                import_string = import_string.replace(remove_syntax, " ")
            import_string = import_string.replace("[[i]]", "_import")

            imports = import_string.split()
            if "as" in imports and (imports.index('as') + 1) < len(imports):
                while "as" in imports:
                    index = imports.index('as')
                    if import_type == "from":
                        self.as_map[imports[0] + "." + imports[index - 1]] = imports[index + 1]
                    else:
                        self.as_map[imports[index - 1]] = imports[index + 1]
                    del imports[index:index + 2]
            if import_type == "from":
                import_from = imports.pop(0)
                root = self.imports[self.place_module(import_from)][import_type]
                if root.get(import_from, False):
                    root[import_from].update(imports)
                else:
                    root[import_from] = set(imports)
            else:
                for module in imports:
                    self.imports[self.place_module(module)][import_type].add(module)
