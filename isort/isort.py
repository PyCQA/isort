"""
    isort.py

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

import copy
import os
from sys import path as PYTHONPATH, stderr

from natsort import natsorted
from pies import *

from . import settings


class Sections(object):
    FUTURE = 1
    STDLIB = 2
    THIRDPARTY = 3
    FIRSTPARTY = 4
    ALL = (FUTURE, STDLIB, THIRDPARTY, FIRSTPARTY)


class SortImports(object):
    config = settings.default

    def __init__(self, file_path=None, file_contents=None, **setting_overrides):
        if setting_overrides:
            self.config = settings.default.copy()
            self.config.update(setting_overrides)

        file_name = file_path
        if file_path:
            if "/" in file_name:
                file_name = file_name[file_name.rfind('/') + 1:]
            if file_name in self.config['skip']:
                print(file_path + ": refusing to proceed, listed in 'skip' setting.", file=stderr)
                sys.exit(1)
            self.file_path = file_path
            with open(file_path) as file:
                file_contents = file.read()

        if file_contents is None:
            return

        self.in_lines = file_contents.split("\n")
        self.number_of_lines = len(self.in_lines)

        self.out_lines = []
        self.imports = {}
        self.as_map = {}
        for section in Sections.ALL:
            self.imports[section] = {'straight':set(), 'from':{}}

        self.index = 0
        self.import_index = -1
        self._parse()
        if self.import_index != -1:
            self._add_formatted_imports()

        self.output = "\n".join(self.out_lines)
        if file_name:
            with open(file_name, "w") as outputFile:
                outputFile.write(self.output)

    def place_module(self, moduleName):
        """Trys to determine if a module is a python std import,
           third party import, or project code:
           if it can't determine - it assumes it is project code
        """
        index = moduleName.find('.')
        if index:
            firstPart = moduleName[:index]
        else:
            firstPart = None

        if moduleName == "__future__" or (firstPart == "__future__"):
            return Sections.FUTURE
        elif moduleName in self.config['known_standard_library'] or \
                (firstPart in self.config['known_standard_library']):
            return Sections.STDLIB
        elif moduleName in self.config['known_third_party'] or (firstPart in self.config['known_third_party']):
            return Sections.THIRDPARTY
        elif moduleName in self.config['known_first_party'] or (firstPart in self.config['known_first_party']):
            return Sections.FIRSTPARTY

        for prefix in PYTHONPATH:
            fixed_module_name = moduleName.replace('.', '/')
            base_path = prefix + "/" + fixed_module_name
            if os.path.exists(base_path + ".py") or os.path.exists(base_path) or os.path.exists(base_path + ".so"):
                if "site-packages" in prefix or "dist-packages" in prefix:
                    return Sections.THIRDPARTY
                elif "python2" in prefix.lower() or "python3" in prefix.lower():
                    return Sections.STDLIB
                else:
                    return Sections.FIRSTPARTY

        return Sections.FIRSTPARTY

    def _get_line(self):
        """ Returns the current line from the file while
            incrementing the index
        """
        line = self.in_lines[self.index]
        self.index += 1
        return line

    @staticmethod
    def _import_type(line):
        """ If the current line is an import line it will
            return its type (from or straight)
        """
        if line.startswith('import '):
            return "straight"
        if line.startswith('from ') and "import" in line:
            return "from"

    def _at_end(self):
        """ returns True if we are at the end of the file """
        return self.index == self.number_of_lines

    @staticmethod
    def _module_key(module_name, config):
        module_name = str(module_name).lower()
        return "{0}{1}".format(module_name in config['force_to_top'] and "A" or "B",
                               config['length_sort'] and len(module_name) or module_name)

    def _add_formatted_imports(self):
        """ Adds the imports back to the file
            (at the index of the first import)
            sorted alphabetically and split between groups
        """
        output = []
        for section in Sections.ALL:
            straight_modules = list(self.imports[section]['straight'])
            straight_modules.sort(key=lambda key: self._module_key(key, self.config))

            for module in straight_modules:
                if module in self.as_map:
                    output.append("import {0} as {1}".format(module, self.as_map[module]))
                else:
                    output.append("import {0}".format(module))

            from_modules = list(self.imports[section]['from'].keys())
            from_modules = natsorted(from_modules, key=lambda key: self._module_key(key, self.config))
            for module in from_modules:
                import_start = "from {0} import ".format(module)
                from_imports = list(self.imports[section]['from'][module])
                from_imports = natsorted(from_imports, key=lambda key: self._module_key(key, self.config))
                for from_import in copy.copy(from_imports):
                    import_as = self.as_map.get(module + "." + from_import, False)
                    if import_as:
                        output.append(import_start + "{0} as {1}".format(from_import, import_as))
                        from_imports.remove(from_import)

                if from_imports:
                    if "*" in from_imports:
                        import_statement = "{0}*".format(import_start)
                    else:
                        import_statement = import_start + (", ").join(from_imports)
                        if len(import_statement) > self.config['line_length'] and len(from_imports) > 1:
                            import_statement = import_start
                            if self.config['multi_line_output'] != settings.MultiLineOutput.HANGING_INDENT:
                                import_statement += "("
                                white_space = " " * len(import_statement)
                            if self.config['multi_line_output'] == settings.MultiLineOutput.GRID:
                                import_statement += from_imports.pop(0)
                                while from_imports:
                                    next_import = from_imports.pop(0)
                                    next_statement = import_statement + ", " + next_import
                                    if len(next_statement.split("\n")[-1]) + 1 > self.config['line_length']:
                                        next_statement = "{0},\n{1}{2}".format(import_statement, white_space,
                                                                               next_import)
                                    import_statement = next_statement
                                import_statement += ")"
                            elif self.config['multi_line_output'] == settings.MultiLineOutput.VERTICAL:
                                import_statement += (",\n" + white_space).join(from_imports)
                                import_statement += ")"
                            elif self.config['multi_line_output'] == settings.MultiLineOutput.VERTICAL_HANGING_INDENT:
                                import_statement += "\n" + self.config['indent']
                                import_statement += (",\n" + self.config['indent']).join(from_imports)
                                import_statement += "\n)"
                            elif self.config['multi_line_output'] == settings.MultiLineOutput.HANGING_INDENT:
                                import_statement += " " + from_imports.pop(0)
                                while from_imports:
                                    next_import = from_imports.pop(0)
                                    next_statement = import_statement + ", " + next_import
                                    if len(next_statement.split("\n")[-1]) + 3 > self.config['line_length']:
                                        next_statement = "{0}, \\\n{1}{2}".format(import_statement,
                                                                                  self.config['indent'],
                                                                                  next_import)
                                    import_statement = next_statement

                    output.append(import_statement)

            if straight_modules or from_modules:
                output.append("")

        while output[-1:] == [""]:
            output.pop()

        while self.import_index + 2 < len(self.out_lines) and self.out_lines[self.import_index + 1] == "":
            self.out_lines.pop(self.import_index + 1)

        if len(self.out_lines) > self.import_index + 1:
            next_construct = self.out_lines[self.import_index + 1]
            if next_construct.startswith("def") or next_construct.startswith("class") or \
               next_construct.startswith("@"):
                output += ["", ""]
            else:
                output += [""]

        self.out_lines[self.import_index:1] = output

    @staticmethod
    def _strip_comments(line):
        """
            Removes comments from import line.
        """
        comment_start = line.find("#")
        if comment_start != -1:
            print("Removing comment(%s) so imports can be sorted correctly" % line[comment_start:], file=stderr)
            line = line[:comment_start]

        return line

    def _parse(self):
        """
            Parses a python file taking out and categorizing imports
        """
        while True:
            if self._at_end():
                return None

            line = self._get_line()
            import_type = self._import_type(line)
            if import_type:
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
                if "as" in imports and import_type != 'from':
                    while True:
                        try:
                            index = imports.index('as')
                        except:
                            break
                        self.as_map[imports[index - 1]] = imports[index + 1]
                        from_import = imports[index - 1]
                        module_placment = self.place_module(from_import)
                        self.imports[module_placment][import_type].update([from_import])
                        del imports[index -1:index + 2]
                elif import_type == 'from' and "as" in imports:
                    while True:
                        try:
                            index = imports.index('as')
                        except:
                            break
                        from_import = imports[0]
                        self.as_map[from_import] = imports[index + 1]
                        module_placment = self.place_module(from_import)
                        imports = ["{0} as {1}".format(imports[index - 1], imports[index + 1])]
                        self.imports[module_placment][import_type].setdefault(from_import, set()).update(imports)
                        del imports[index -1:index + 1]
                if import_type == "from":
                    impot_from = imports.pop(0)
                    root = self.imports[self.place_module(impot_from)][import_type]
                    if root.get(impot_from, False):
                        root[impot_from].update(imports)
                    else:
                        root[impot_from] = set(imports)
                else:
                    for module in imports:
                        self.imports[self.place_module(module)][import_type].add(module)

                if self._at_end():
                    print(self.file_path + ": Either you have an import at the end of your file, or something"
                                           " went horribly wrong!",
                          file=stderr)
                    sys.exit(1)

            else:
                self.out_lines.append(line)
