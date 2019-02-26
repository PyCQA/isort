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
import copy
import itertools
import os
import re
import sys
from datetime import datetime
from difflib import unified_diff
from typing import Any, Dict, Iterable, List, Optional, Sequence

from isort import files, formatter, utils

from . import settings
from .natural import get_naturally_sortable_module_name, nsorted
from .settings import WrapModes


class SortImports(object):
    incorrectly_sorted = False
    skipped = False

    def __init__(
        self,
        file_path: Optional[str] = None,
        file_contents: Optional[str] = None,
        write_to_stdout: bool = False,
        check: bool = False,
        show_diff: bool = False,
        settings_path: Optional[str] = None,
        ask_to_apply: bool = False,
        **setting_overrides: Any
    ) -> None:
        if not settings_path and file_path:
            settings_path = os.path.dirname(os.path.abspath(file_path))
        settings_path = settings_path or os.getcwd()

        self.config = settings.prepare_config(settings_path, **setting_overrides)

        self.specified_manual_sections = {}  # type: Dict[str, List[str]]
        self.line_to_manual_section_mapping = {}  # type: Dict[str, str]

        self.remove_imports = [formatter.format_simplified(removal) for removal in self.config['remove_imports']]
        self.add_imports = [formatter.format_natural(addition) for addition in self.config['add_imports']]
        self._section_header_comments = ["# " + value for key, value in self.config.items()
                                         if key.startswith('import_heading') and value]

        self.file_encoding = 'utf-8'
        file_name = file_path
        self.file_path = file_path or ""
        if file_path:
            file_path = os.path.abspath(file_path)
            if settings.file_should_be_skipped(file_path, self.config):
                self.skipped = True
                if self.config['verbose']:
                    print("WARNING: {0} was skipped as it's listed in 'skip' setting"
                          " or matches a glob in 'skip_glob' setting".format(file_path))
                file_contents = None
            elif not file_contents:
                self.file_path = file_path
                self.file_encoding = utils.coding_check(file_path)
                with open(file_path, encoding=self.file_encoding, newline='') as file_to_import_sort:
                    file_contents = file_to_import_sort.read()

        if file_contents is None or ("isort:" + "skip_file") in file_contents:
            self.skipped = True
            self.output = None
            if write_to_stdout and file_contents:
                sys.stdout.write(file_contents)
            return

        if self.config['line_ending']:
            self.line_separator = self.config['line_ending']
        else:
            self.line_separator = utils.infer_line_separator(file_contents)

        self.in_lines = file_contents.split(self.line_separator)
        self.original_num_of_lines = len(self.in_lines)
        if (self.original_num_of_lines > 1 or self.in_lines[:1] not in ([], [""])) or self.config['force_adds']:
            for add_import in self.add_imports:
                self.in_lines.append(add_import)
        self.number_of_lines = len(self.in_lines)

        file = files.parse(source_lines=self.in_lines,
                           line_separator=self.line_separator,
                           config=self.config)

        self.import_index = file.cursor.import_index
        self.index = file.cursor.index
        self._top_comment_start_index = file.cursor.top_comment_start_index
        self._top_comment_end_index = file.cursor.top_comment_end_index
        self._wrapping_quotes = file.cursor.wrapping_quotes
        self._in_top_comment = file.cursor.inside_top_comment
        self.sections = file.sections

        self.out_lines = file.output_lines
        self.parsed_imports = file.parsed_imports
        self.as_map = file.as_map
        self.comments = file.comments

        self.specified_manual_sections = file.specified_manual_sections
        self.line_to_manual_section_mapping = file.line_to_manual_section_mapping

        # self._parse()
        if self.import_index != -1:
            self._add_formatted_imports()

        self.length_change = len(self.out_lines) - self.original_num_of_lines
        while self.out_lines and self.out_lines[-1].strip() == "":
            self.out_lines.pop(-1)
        self.out_lines.append("")
        self.output = self.line_separator.join(self.out_lines)

        if self.config['atomic']:
            try:
                compile(formatter.strip_top_comments(self.out_lines, self.line_separator), self.file_path, 'exec', 0, 1)
            except SyntaxError:
                self.output = file_contents
                self.incorrectly_sorted = True
                try:
                    compile(formatter.strip_top_comments(self.in_lines, self.line_separator), self.file_path, 'exec', 0, 1)
                    print("ERROR: {0} isort would have introduced syntax errors, please report to the project!".
                          format(self.file_path))
                except SyntaxError:
                    print("ERROR: {0} File contains syntax errors.".format(self.file_path))
                return

        if check:
            check_output = self.output
            check_against = file_contents
            if self.config['ignore_whitespace']:
                check_output = check_output.replace(self.line_separator, "").replace(" ", "")
                check_against = check_against.replace(self.line_separator, "").replace(" ", "")

            if check_output.strip() == check_against.strip():
                if self.config['verbose']:
                    print("SUCCESS: {0} Everything Looks Good!".format(self.file_path))
                return

            print("ERROR: {0} Imports are incorrectly sorted.".format(self.file_path))
            self.incorrectly_sorted = True
        if show_diff or self.config['show_diff']:
            self._show_diff(file_contents)
        elif write_to_stdout:
            sys.stdout.write(self.output)
        elif file_name and not check:
            if self.output == file_contents:
                return

            if ask_to_apply:
                self._show_diff(file_contents)
                answer = None
                while answer not in ('yes', 'y', 'no', 'n', 'quit', 'q'):
                    answer = input("Apply suggested changes to '{0}' [y/n/q]? ".format(self.file_path)).lower()
                    if answer in ('no', 'n'):
                        return
                    if answer in ('quit', 'q'):
                        sys.exit(1)
            with open(self.file_path, 'w', encoding=self.file_encoding, newline='') as output_file:
                print("Fixing {0}".format(self.file_path))
                output_file.write(self.output)

    @property
    def correctly_sorted(self) -> bool:
        return not self.incorrectly_sorted

    def _show_diff(self, file_contents: str) -> None:
        for line in unified_diff(
            file_contents.splitlines(keepends=True),
            self.output.splitlines(keepends=True),
            fromfile=self.file_path + ':before',
            tofile=self.file_path + ':after',
            fromfiledate=str(datetime.fromtimestamp(os.path.getmtime(self.file_path))
                             if self.file_path else datetime.now()),
            tofiledate=str(datetime.now())
        ):
            sys.stdout.write(line)

    def _consume_line(self) -> str:
        """Returns the current line from the file while incrementing the index."""
        line = self.in_lines[self.index]
        self.index += 1
        return line

    def _reached_the_end_of_file(self) -> bool:
        """returns True if we are at the end of the file."""
        return self.index == self.number_of_lines

    def _add_comments(
        self,
        comments: Sequence[str],
        original_string: str = ""
    ) -> str:
        """
            Returns a string with comments added if ignore_comments is not set.
        """
        if self.config['ignore_comments']:
            return formatter.partition_comment(original_string)[0]

        if not comments:
            return original_string
        else:
            return "{0}{1} {2}".format(formatter.partition_comment(original_string)[0],
                                       self.config['comment_prefix'],
                                       "; ".join(comments))

    def _wrap(self, line: str) -> str:
        """
            Returns an import wrapped to the specified line-length, if possible.
        """
        wrap_mode = self.config['multi_line_output']
        if len(line) > self.config['line_length'] and wrap_mode != WrapModes.NOQA:
            line_without_comment = line
            comment = None
            if '#' in line:
                line_without_comment, comment = line.split('#', 1)
            for splitter in ("import ", ".", "as "):
                exp = r"\b" + re.escape(splitter) + r"\b"
                if re.search(exp, line_without_comment) and not line_without_comment.strip().startswith(splitter):
                    line_parts = re.split(exp, line_without_comment)
                    if comment:
                        line_parts[-1] = '{0}#{1}'.format(line_parts[-1], comment)
                    next_line = []
                    while (len(line) + 2) > (self.config['wrap_length'] or self.config['line_length']) and line_parts:
                        next_line.append(line_parts.pop())
                        line = splitter.join(line_parts)
                    if not line:
                        line = next_line.pop()

                    cont_line = self._wrap(self.config['indent'] + splitter.join(next_line).lstrip())
                    if self.config['use_parentheses']:
                        output = "{0}{1}({2}{3}{4}{5})".format(
                            line, splitter, self.line_separator, cont_line,
                            "," if self.config['include_trailing_comma'] else "",
                            self.line_separator if wrap_mode in {WrapModes.VERTICAL_HANGING_INDENT,
                                                                 WrapModes.VERTICAL_GRID_GROUPED}
                            else "")
                        lines = output.split(self.line_separator)
                        if self.config['comment_prefix'] in lines[-1] and lines[-1].endswith(')'):
                            line, comment = lines[-1].split(self.config['comment_prefix'], 1)
                            lines[-1] = line + ')' + self.config['comment_prefix'] + comment[:-1]
                        return self.line_separator.join(lines)
                    return "{0}{1}\\{2}{3}".format(line, splitter, self.line_separator, cont_line)
        elif len(line) > self.config['line_length'] and wrap_mode == settings.WrapModes.NOQA:
            if "# NOQA" not in line:
                return "{0}{1} NOQA".format(line, self.config['comment_prefix'])

        return line

    def _add_straight_imports(self, straight_modules: Iterable[str], section: str, section_output: List[str]) -> None:
        for module in straight_modules:
            if module in self.remove_imports:
                continue

            if module in self.as_map:
                import_definition = ''
                if self.config['keep_direct_and_as_imports']:
                    import_definition = "import {0}\n".format(module)
                import_definition += "import {0} as {1}".format(module, self.as_map[module])
            else:
                import_definition = "import {0}".format(module)

            comments_above = self.comments['above']['straight'].pop(module, None)
            if comments_above:
                section_output.extend(comments_above)
            section_output.append(self._add_comments(self.comments['straight'].get(module), import_definition))

    def _add_from_imports(self, from_modules: Iterable[str], section: str, section_output: List[str],
                          ignore_case: bool) -> None:
        for module in from_modules:
            if module in self.remove_imports:
                continue

            import_start = "from {0} import ".format(module)
            from_imports = list(self.parsed_imports[section]['from'][module])
            if not self.config['no_inline_sort'] or self.config['force_single_line']:
                from_imports = nsorted(from_imports,
                                       key=lambda key: get_naturally_sortable_module_name(key, self.config, True, ignore_case,
                                                                                          section_name=section))
            if self.remove_imports:
                from_imports = [line for line in from_imports if not "{0}.{1}".format(module, line) in
                                                                     self.remove_imports]

            sub_modules = ['{0}.{1}'.format(module, from_import) for from_import in from_imports]
            as_imports = {
                from_import: "{0} as {1}".format(from_import, self.as_map[sub_module])
                for from_import, sub_module in zip(from_imports, sub_modules)
                if sub_module in self.as_map
            }
            if self.config['combine_as_imports'] and not ("*" in from_imports and self.config['combine_star']):
                for from_import in copy.copy(from_imports):
                    if from_import in as_imports:
                        from_imports[from_imports.index(from_import)] = as_imports.pop(from_import)

            while from_imports:
                comments = self.comments['from'].pop(module, ())
                if "*" in from_imports and self.config['combine_star']:
                    import_statement = self._wrap(self._add_comments(comments, "{0}*".format(import_start)))
                    from_imports = None
                elif self.config['force_single_line']:
                    import_statements = []
                    while from_imports:
                        from_import = from_imports.pop(0)
                        if from_import in as_imports:
                            from_comments = self.comments['straight'].get('{}.{}'.format(module, from_import))
                            import_statements.append(self._add_comments(from_comments,
                                                                        self._wrap(import_start + as_imports[from_import])))
                            continue
                        single_import_line = self._add_comments(comments, import_start + from_import)
                        comment = self.comments['nested'].get(module, {}).pop(from_import, None)
                        if comment:
                            single_import_line += "{0} {1}".format(comments and ";" or self.config['comment_prefix'],
                                                                   comment)
                        import_statements.append(self._wrap(single_import_line))
                        comments = None
                    import_statement = self.line_separator.join(import_statements)
                else:
                    while from_imports and from_imports[0] in as_imports:
                        from_import = from_imports.pop(0)
                        from_comments = self.comments['straight'].get('{}.{}'.format(module, from_import))
                        above_comments = self.comments['above']['from'].pop(module, None)
                        if above_comments:
                            section_output.extend(above_comments)

                        section_output.append(self._add_comments(from_comments,
                                                                 self._wrap(import_start + as_imports[from_import])))

                    star_import = False
                    if "*" in from_imports:
                        section_output.append(self._add_comments(comments, "{0}*".format(import_start)))
                        from_imports.remove('*')
                        star_import = True
                        comments = None

                    for from_import in copy.copy(from_imports):
                        if from_import in as_imports:
                            continue
                        comment = self.comments['nested'].get(module, {}).pop(from_import, None)
                        if comment:
                            single_import_line = self._add_comments(comments, import_start + from_import)
                            single_import_line += "{0} {1}".format(comments and ";" or self.config['comment_prefix'],
                                                                   comment)
                            above_comments = self.comments['above']['from'].pop(module, None)
                            if above_comments:
                                section_output.extend(above_comments)
                            section_output.append(self._wrap(single_import_line))
                            from_imports.remove(from_import)
                            comments = None

                    from_import_section = []
                    while from_imports and from_imports[0] not in as_imports:
                        from_import_section.append(from_imports.pop(0))
                    if star_import:
                        import_statement = import_start + (", ").join(from_import_section)
                    else:
                        import_statement = self._add_comments(comments, import_start + (", ").join(from_import_section))
                    if not from_import_section:
                        import_statement = ""

                    do_multiline_reformat = False

                    force_grid_wrap = self.config['force_grid_wrap']
                    if force_grid_wrap and len(from_import_section) >= force_grid_wrap:
                        do_multiline_reformat = True

                    if len(import_statement) > self.config['line_length'] and len(from_import_section) > 1:
                        do_multiline_reformat = True

                    # If line too long AND have imports AND we are NOT using GRID or VERTICAL wrap modes
                    if (len(import_statement) > self.config['line_length'] and len(from_import_section) > 0 and
                            self.config['multi_line_output'] not in (settings.WrapModes.GRID, settings.WrapModes.VERTICAL)):
                        do_multiline_reformat = True

                    if do_multiline_reformat:
                        import_statement = self._multi_line_reformat(import_start, from_import_section, comments)
                        if self.config['multi_line_output'] == settings.WrapModes.GRID:
                            self.config['multi_line_output'] = settings.WrapModes.VERTICAL_GRID
                            try:
                                other_import_statement = self._multi_line_reformat(import_start, from_import_section, comments)
                                if (max(len(x)
                                        for x in import_statement.split('\n')) > self.config['line_length']):
                                    import_statement = other_import_statement
                            finally:
                                self.config['multi_line_output'] = settings.WrapModes.GRID
                    if not do_multiline_reformat and len(import_statement) > self.config['line_length']:
                        import_statement = self._wrap(import_statement)

                if import_statement:
                    above_comments = self.comments['above']['from'].pop(module, None)
                    if above_comments:
                        section_output.extend(above_comments)
                    section_output.append(import_statement)

    def _multi_line_reformat(self, import_start: str, from_imports: List[str], comments: Sequence[str]) -> str:
        reformatter = formatter.MultilineFormatter(self.config, self.line_separator)
        import_statement = reformatter.reformat(import_start, from_imports, comments)

        if import_statement.count(self.line_separator) == 0:
            return self._wrap(import_statement)
        return import_statement

    def _add_formatted_imports(self) -> None:
        """Adds the imports back to the file.

        (at the index of the first import) sorted alphabetically and split between groups

        """
        sort_ignore_case = self.config['force_alphabetical_sort_within_sections']
        sections = itertools.chain(self.sections, self.config['forced_separate'])  # type: Iterable[str]

        if self.config['no_sections']:
            self.parsed_imports['no_sections'] = {'straight': [], 'from': {}}
            for section in sections:
                self.parsed_imports['no_sections']['straight'].extend(self.parsed_imports[section].get('straight', []))
                self.parsed_imports['no_sections']['from'].update(self.parsed_imports[section].get('from', {}))
            sections = ('no_sections',)

        output = []  # type: List[str]
        prev_section_has_imports = False
        for section in sections:
            straight_modules = self.parsed_imports[section]['straight']
            straight_modules = nsorted(straight_modules,
                                       key=lambda key: get_naturally_sortable_module_name(key, self.config,
                                                                                          section_name=section))
            from_modules = self.parsed_imports[section]['from']
            from_modules = nsorted(from_modules,
                                   key=lambda key: get_naturally_sortable_module_name(key, self.config,
                                                                                      section_name=section))

            section_output = []  # type: List[str]
            if self.config['from_first']:
                self._add_from_imports(from_modules, section, section_output, sort_ignore_case)
                if self.config['lines_between_types'] and from_modules and straight_modules:
                    section_output.extend([''] * self.config['lines_between_types'])
                self._add_straight_imports(straight_modules, section, section_output)
            else:
                self._add_straight_imports(straight_modules, section, section_output)
                if self.config['lines_between_types'] and from_modules and straight_modules:
                    section_output.extend([''] * self.config['lines_between_types'])
                self._add_from_imports(from_modules, section, section_output, sort_ignore_case)

            if self.config['force_sort_within_sections']:
                def by_module(line: str) -> str:
                    section = 'B'
                    if line.startswith('#'):
                        return 'AA'

                    line = re.sub('^from ', '', line)
                    line = re.sub('^import ', '', line)
                    if line.split(' ')[0] in self.config['force_to_top']:
                        section = 'A'
                    if not self.config['order_by_type']:
                        line = line.lower()
                    return '{0}{1}'.format(section, line)

                section_output = nsorted(section_output, key=by_module)

            if section_output:
                section_name = section
                if section_name in self.specified_manual_sections:
                    self.specified_manual_sections[section_name] = section_output
                    continue

                section_title = self.config.get('import_heading_' + str(section_name).lower(), '')
                if section_title:
                    section_comment = "# {0}".format(section_title)
                    if section_comment not in self.out_lines[0:1] and section_comment not in self.in_lines[0:1]:
                        section_output.insert(0, section_comment)
                if prev_section_has_imports and section_name in self.config['no_lines_before']:
                    while output and output[-1].strip() == '':
                        output.pop()
                output += section_output + ([''] * self.config['lines_between_sections'])
            prev_section_has_imports = bool(section_output)
        while output and output[-1].strip() == '':
            output.pop()
        while output and output[0].strip() == '':
            output.pop(0)

        output_at = 0
        if self.import_index < self.original_num_of_lines:
            output_at = self.import_index
        elif self._top_comment_end_index != -1 and self._top_comment_start_index <= 2:
            output_at = self._top_comment_end_index
        self.out_lines[output_at:0] = output

        imports_tail = output_at + len(output)
        while [character.strip() for character in self.out_lines[imports_tail: imports_tail + 1]] == [""]:
            self.out_lines.pop(imports_tail)

        if len(self.out_lines) > imports_tail:
            next_construct = ""
            tail = self.out_lines[imports_tail:]

            for index, line in enumerate(tail):
                in_quote = ''
                if not self._line_should_be_skipped(line) and line.strip():
                    if line.strip().startswith("#") and len(tail) > (index + 1) and tail[index + 1].strip():
                        continue
                    next_construct = line
                    break
                elif not in_quote:
                    parts = line.split()
                    if len(parts) >= 3 and parts[1] == '=' and "'" not in parts[0] and '"' not in parts[0]:
                        next_construct = line
                        break

            if self.config['lines_after_imports'] != -1:
                self.out_lines[imports_tail:0] = ["" for line in range(self.config['lines_after_imports'])]
            elif next_construct.startswith("def ") or next_construct.startswith("class ") or \
                    next_construct.startswith("@") or next_construct.startswith("async def"):
                self.out_lines[imports_tail:0] = ["", ""]
            else:
                self.out_lines[imports_tail:0] = [""]

        if self.specified_manual_sections:
            new_out_lines = []
            for index, line in enumerate(self.out_lines):
                new_out_lines.append(line)

                manual_section_for_line = self.line_to_manual_section_mapping.get(line)
                if manual_section_for_line is not None:
                    new_out_lines.extend(self.specified_manual_sections[manual_section_for_line])
                    if len(self.out_lines) <= index or self.out_lines[index + 1].strip() != "":
                        new_out_lines.append("")

            self.out_lines = new_out_lines

    def is_top_comment_start(self, line: str) -> bool:
        return self.index == 1 and line.startswith("#")

    def is_top_comment_end(self, line: str) -> bool:
        return self._in_top_comment and not line.startswith('#')

    def _line_should_be_skipped(self, line: str) -> bool:
        inside_multiline_string = bool(self._wrapping_quotes)

        # whether we are in the top comment section
        if self.is_top_comment_start(line):
            self._in_top_comment = True
            return True
        elif self.is_top_comment_end(line):
            # quit top comment
            self._in_top_comment = False
            self._top_comment_end_index = self.index - 1

        if '"' in line or "'" in line:
            col_ind = 0
            if self._top_comment_start_index == -1 and (line.startswith('"') or line.startswith("'")):
                # string at top of the file
                self._top_comment_start_index = self.index

            while col_ind < len(line):
                if line[col_ind] == "\\":
                    col_ind += 1

                elif self._wrapping_quotes:
                    # if in string expression, check whether next symbols are the end of expression
                    if line[col_ind:col_ind + len(self._wrapping_quotes)] == self._wrapping_quotes:
                        # end of string
                        self._wrapping_quotes = ''
                        if self._top_comment_end_index < self._top_comment_start_index:
                            self._top_comment_end_index = self.index

                elif line[col_ind] in ("'", '"'):
                    # start of string expression
                    long_quote = line[col_ind:col_ind + 3]
                    if long_quote in ('"""', "'''"):
                        self._wrapping_quotes = long_quote
                        col_ind += 2
                    else:
                        self._wrapping_quotes = line[col_ind]

                elif line[col_ind] == "#":
                    # start of comment
                    break

                col_ind += 1

        return inside_multiline_string or bool(self._wrapping_quotes) or self._in_top_comment
