import itertools
from collections import OrderedDict, namedtuple
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from isort import formatter, utils
from isort.finders import FindersManager

if TYPE_CHECKING:
    from mypy_extensions import TypedDict

    CommentsAboveDict = TypedDict('CommentsAboveDict', {
        'straight': Dict[str, Any],
        'from': Dict[str, Any]
    })
    CommentsDict = TypedDict('CommentsDict', {
        'from': Dict[str, Any],
        'straight': Dict[str, Any],
        'nested': Dict[str, Any],
        'above': CommentsAboveDict
    })

_Config = Dict[str, Any]


def _remove_syntax_symbols(import_string: str) -> str:
    import_string = import_string.replace("_import", "[[i]]")

    syntactic_symbols_to_remove = ['\\', '(', ')', ',']
    for symbol in syntactic_symbols_to_remove:
        import_string = import_string.replace(symbol, " ")

    import_tokens = import_string.split()
    for key in ('from', 'import'):
        if key in import_tokens:
            import_tokens.remove(key)

    import_string = ' '.join(import_tokens)
    import_string = import_string.replace("[[i]]", "_import")
    return import_string.replace("{ ", "{|").replace(" }", "|}")


def _is_single_module_name(line: str) -> bool:
    return bool(line) and ' ' not in line


def _file_is_not_empty(source_lines: List[str]) -> bool:
    return len(source_lines) > 1 or source_lines[:1] not in ([], [""])


def _normalize_line(line: str) -> str:
    line = line.replace("from.import ", "from . import ")
    line = line.replace("\t", " ").replace('import*', 'import *')
    line = line.replace(" .import ", " . import ")
    return line


def _normalize_from_import_string(import_string: str) -> str:
    import_string = import_string.replace("import(", "import (")
    parts = import_string.split(" import ")
    from_import = parts[0].split(" ")
    return " import ".join([from_import[0] + " " + "".join(from_import[1:])] + parts[1:])


def _parse_manual_section_or_none(line: str) -> Optional[str]:
    section = None
    if "isort:imports-" in line and line.startswith("#"):
        section = line.split("isort:imports-")[-1].split()[0].upper()
    return section


def _has_semicolon_separated_non_imports_code(line: str) -> bool:
    if ";" in line:
        # ';' separated lines with non-import code inside are skipped
        for part in (part.strip() for part in line.split(";")):
            if part and utils.get_import_type_or_none(part) is None:
                return True
    return False


def parse(source_lines: List[str], line_separator: str, config: _Config) -> 'SourceFile':
    parser = _SourceFileParser(config)
    return parser.parse(source_lines, line_separator)


class Cursor:
    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines

        self.index = 0
        self.inside_top_comment = False
        self.import_index = -1
        self.top_comment_start_index = -1
        self.top_comment_end_index = -1
        self.wrapping_quotes = ''
        self.original_number_of_lines = len(source_lines)

    def reached_the_end_of_file(self) -> bool:
        return self.index == self.original_number_of_lines

    def consume_line(self) -> str:
        """Returns the current line from the file while incrementing the index."""
        line = self.source_lines[self.index]
        self.index += 1
        return line

    def _is_top_comment_start(self, line: str) -> bool:
        return self.index == 1 and line.startswith("#")

    def _is_top_comment_end(self, line: str) -> bool:
        return self.inside_top_comment and not line.startswith('#')

    def _line_starts_with_a_quote(self, line: str) -> bool:
        return line.startswith('"') or line.startswith("'")

    def line_should_be_skipped(self, line: str) -> bool:
        inside_multiline_string = bool(self.wrapping_quotes)

        # whether we are in the top comment section
        if self._is_top_comment_start(line):
            self.inside_top_comment = True
            return True
        elif self._is_top_comment_end(line):
            # quit top comment
            self.inside_top_comment = False
            self.top_comment_end_index = self.index - 1

        if '"' in line or "'" in line:
            col_ind = 0
            if self.top_comment_start_index == -1 and self._line_starts_with_a_quote(line):
                self.top_comment_start_index = self.index

            while col_ind < len(line):
                if line[col_ind] == "\\":
                    col_ind += 1

                elif self.wrapping_quotes:
                    # if in string expression, check whether next symbols are the end of expression
                    if line[col_ind:col_ind + len(self.wrapping_quotes)] == self.wrapping_quotes:
                        # end of string
                        self.wrapping_quotes = ''
                        if self.top_comment_end_index < self.top_comment_start_index:
                            self.top_comment_end_index = self.index

                elif line[col_ind] in ("'", '"'):
                    # start of string expression
                    long_quote = line[col_ind:col_ind + 3]
                    if long_quote in ('"""', "'''"):
                        self.wrapping_quotes = long_quote
                        col_ind += 2
                    else:
                        self.wrapping_quotes = line[col_ind]

                elif line[col_ind] == "#":
                    # start of comment
                    break

                col_ind += 1

        return inside_multiline_string or bool(self.wrapping_quotes) or self.inside_top_comment


class SourceFile:
    def __init__(self, config: _Config, cursor: Cursor):
        self.config = config
        self.cursor = cursor

        self.output_lines = []  # type: List[str]
        self.parsed_imports = OrderedDict()  # type: OrderedDict[str, Dict[str, Any]]
        self.as_map = {}  # type: Dict[str, str]
        self.specified_manual_sections = {}  # type: Dict[str, List[str]]
        self.line_to_manual_section_mapping = {}  # type: Dict[str, str]
        self.comments = {'from': {}, 'straight': {}, 'nested': {}, 'above': {'straight': {}, 'from': {}}}  # type: CommentsDict

        section_names = self.config['sections']
        self.sections = namedtuple('Sections', section_names)(*[name for name in section_names])
        for section in itertools.chain(self.sections, self.config['forced_separate']):
            self.parsed_imports[section] = {'straight': OrderedDict(), 'from': OrderedDict()}


class _SourceFileParser:
    def __init__(self, config: _Config):
        self.config = config
        self.section_header_comments = ["# " + value for key, value in self.config.items()
                                        if key.startswith('import_heading') and value]
        section_names = self.config['sections']
        sections = namedtuple('Sections', section_names)(*[name for name in section_names])
        self.finder = FindersManager(config=self.config, sections=sections)

    def parse(self, source_lines: List[str], line_separator: str) -> SourceFile:
        source_lines = source_lines[:]

        if _file_is_not_empty(source_lines) or self.config['force_adds']:
            imports_to_add = [formatter.format_natural(addition) for addition in self.config['add_imports']]
            for import_to_add in imports_to_add:
                source_lines.append(import_to_add)

        cursor = Cursor(source_lines)
        file = SourceFile(self.config, cursor)
        while not cursor.reached_the_end_of_file():
            raw_line = cursor.consume_line()
            line = _normalize_line(raw_line)

            # TODO: merge into consume_line()
            line_should_be_skipped = cursor.line_should_be_skipped(line)
            statement_index = cursor.index
            if line in self.section_header_comments and not line_should_be_skipped:
                if cursor.import_index == -1:
                    cursor.import_index = cursor.index - 1
                continue

            # manual placement of isort import sections
            isort_manual_import_section = _parse_manual_section_or_none(line)
            if isort_manual_import_section is not None:
                file.specified_manual_sections[isort_manual_import_section] = []
                file.line_to_manual_section_mapping[line] = isort_manual_import_section

            if _has_semicolon_separated_non_imports_code(line):
                line_should_be_skipped = True

            current_import_type = utils.get_import_type_or_none(line)
            if current_import_type is None or line_should_be_skipped:
                # not an import line or skipped
                file.output_lines.append(raw_line)
                continue

            for line in (line.strip() for line in line.split(';')):
                current_import_type = utils.get_import_type_or_none(line)
                if current_import_type is None:
                    file.output_lines.append(line)
                    continue

                if cursor.import_index == -1:
                    cursor.import_index = cursor.index - 1

                comments = []
                import_string, comment = formatter.partition_comment(line)
                if comment:
                    comments.append(comment)

                nested_comments = {}  # type: Dict[str, str]
                import_string_tokens = [part
                                        for part in _remove_syntax_symbols(import_string).strip().split(" ")
                                        if part]
                if current_import_type == "from" and len(import_string_tokens) == 2 \
                        and import_string_tokens[1] != "*" and comment:
                    # 'from PACKAGE import ATTRIBUTE' expression
                    nested_comments[import_string_tokens[-1]] = comment

                # parse lines wrapped with '(' ')'
                if "(" in line.split("#")[0] and not cursor.reached_the_end_of_file():
                    while not line.strip().endswith(")") and not cursor.reached_the_end_of_file():
                        line, comment = formatter.partition_comment(cursor.consume_line())
                        if comment:
                            comments.append(comment)

                        stripped_line = _remove_syntax_symbols(line).strip()
                        if current_import_type == "from" and _is_single_module_name(stripped_line) and comment:
                            nested_comments[stripped_line] = comment

                        import_string += line_separator + line

                else:
                    while line.strip().endswith("\\"):
                        line, comment = formatter.partition_comment(cursor.consume_line())
                        if comment:
                            comments.append(comment)

                        # Still need to check for parentheses after an escaped line
                        if "(" in line.split("#")[0] and ")" not in line.split("#")[0] and not cursor.reached_the_end_of_file():
                            stripped_line = _remove_syntax_symbols(line).strip()
                            if current_import_type == "from" and _is_single_module_name(stripped_line) and comment:
                                nested_comments[stripped_line] = comment

                            import_string += line_separator + line

                            while not line.strip().endswith(")") and not cursor.reached_the_end_of_file():
                                line, comment = formatter.partition_comment(cursor.consume_line())
                                if comment:
                                    comments.append(comment)

                                stripped_line = _remove_syntax_symbols(line).strip()
                                if current_import_type == "from" and _is_single_module_name(stripped_line) and comment:
                                    nested_comments[stripped_line] = comment
                                import_string += line_separator + line

                        stripped_line = _remove_syntax_symbols(line).strip()
                        if current_import_type == "from" and _is_single_module_name(stripped_line) and comment:
                            nested_comments[stripped_line] = comment

                        if import_string.strip().endswith(" import") or line.strip().startswith("import "):
                            import_string += line_separator + line
                        else:
                            import_string = import_string.rstrip().rstrip("\\") + " " + line.lstrip()

                if current_import_type == "from":
                    import_string = _normalize_from_import_string(import_string)

                import_items = [item.replace("{|", "{ ").replace("|}", " }")
                                for item in _remove_syntax_symbols(import_string).split()]

                if "as" in import_items and (import_items.index('as') + 1) < len(import_items):
                    while "as" in import_items:
                        # consume one 'module as module_alias' item
                        index = import_items.index('as')
                        if current_import_type == "from":
                            imported_module_name = import_items[0] + "." + import_items[index - 1]
                            file.as_map[imported_module_name] = import_items[index + 1]
                        else:
                            imported_module_name = import_items[index - 1]
                            file.as_map[imported_module_name] = import_items[index + 1]

                        if not self.config['combine_as_imports']:
                            file.comments['straight'][imported_module_name] = comments
                            comments = []
                        del import_items[index:index + 2]

                if current_import_type == "from":
                    imported_from = import_items.pop(0)
                    import_group = self.determine_import_group(imported_from)
                    if self.config['verbose']:
                        print("from-type place_module for %s returned %s" % (imported_from, import_group))

                    if import_group == '':
                        print(
                            "WARNING: could not place module {0} of line {1} --"
                            " Do you need to define a default section?".format(imported_from, line)
                        )

                    for imported_module_name in import_items:
                        # extract comments for 'from PACKAGE import ()' section
                        associated_comment = nested_comments.get(imported_module_name)
                        if associated_comment:
                            file.comments['nested'].setdefault(imported_from, {})[imported_module_name] = associated_comment
                            comments.pop(comments.index(associated_comment))

                    if comments:
                        # all nested comments are parsed by now, remaining are comments for 'from' itself
                        file.comments['from'].setdefault(imported_from, []).extend(comments)

                    if len(file.output_lines) > max(cursor.import_index, cursor.top_comment_end_index + 1, 1) - 1:
                        last = file.output_lines and file.output_lines[-1].rstrip() or ""
                        while (last.startswith("#") and not last.endswith('"""') and not last.endswith("'''") and
                               'isort:imports-' not in last):
                            file.comments['above']['from'].setdefault(imported_from, []).insert(0, file.output_lines.pop(-1))
                            if len(file.output_lines) > max(cursor.import_index - 1, cursor.top_comment_end_index + 1, 1) - 1:
                                last = file.output_lines[-1].rstrip()
                            else:
                                last = ""
                        if statement_index - 1 == cursor.import_index:
                            cursor.import_index -= len(file.comments['above']['from'].get(imported_from, []))

                    root = file.parsed_imports[import_group][current_import_type]
                    if imported_from not in root:
                        root[imported_from] = OrderedDict()

                    root[imported_from].update((module, None) for module in import_items)

                else:  # straight
                    for imported_module_name in import_items:
                        if comments:
                            file.comments['straight'][imported_module_name] = comments
                            comments = []

                        if len(file.output_lines) > max(cursor.import_index, cursor.top_comment_end_index + 1, 1) - 1:
                            last = file.output_lines and file.output_lines[-1].rstrip() or ""
                            while (last.startswith("#") and not last.endswith('"""') and not last.endswith("'''") and
                                   'isort:imports-' not in last):
                                file.comments['above']['straight'].setdefault(imported_module_name, []) \
                                    .insert(0, file.output_lines.pop(-1))

                                if len(file.output_lines) > 0:
                                    last = file.output_lines[-1].rstrip()
                                else:
                                    last = ""
                            if cursor.index - 1 == cursor.import_index:
                                cursor.import_index -= len(file.comments['above']['straight'].get(imported_module_name, []))
                        import_group = self.determine_import_group(imported_module_name)
                        if self.config['verbose']:
                            print("else-type place_module for %s returned %s" % (imported_module_name, import_group))

                        if import_group == '':
                            print(
                                "WARNING: could not place module {0} of line {1} --"
                                " Do you need to define a default section?".format(imported_module_name, line)
                            )
                        # add 'import {imported_module_name}' line to parsed imports
                        file.parsed_imports[import_group][current_import_type][imported_module_name] = None
        return file

    def determine_import_group(self, module_name: str) -> Optional[str]:
        """Tries to determine if a module is a python std import, third party import, or project code:

        if it can't determine - it assumes it is project code

        """
        return self.finder.find(module_name)
