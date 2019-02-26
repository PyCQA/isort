import copy
from typing import Any, Dict, List, Sequence, Tuple


def partition_comment(line: str) -> Tuple[str, str]:
    comment = ''
    comment_start = line.find("#")
    if comment_start != -1:
        comment = line[comment_start + 1:].strip()
        line = line[:comment_start]
    return line, comment


def strip_top_comments(lines: Sequence[str], line_separator: str) -> str:
    """Strips # comments that exist at the top of the given lines"""
    lines = copy.copy(lines)
    while lines and lines[0].startswith("#"):
        lines = lines[1:]
    return line_separator.join(lines)


def format_simplified(import_line: str) -> str:
    import_line = import_line.strip()
    if import_line.startswith("from "):
        import_line = import_line.replace("from ", "")
        import_line = import_line.replace(" import ", ".")
    elif import_line.startswith("import "):
        import_line = import_line.replace("import ", "")

    return import_line


def format_natural(import_line: str) -> str:
    import_line = import_line.strip()
    if not import_line.startswith("from ") and not import_line.startswith("import "):
        if "." not in import_line:
            return "import {0}".format(import_line)
        parts = import_line.split(".")
        end = parts.pop(-1)
        return "from {0} import {1}".format(".".join(parts), end)

    return import_line


class MultilineFormatter:
    def __init__(self, config: Dict[str, Any], line_separator: str) -> None:
        self.config = config
        self.line_separator = line_separator

    def reformat(self, import_start: str, from_imports: List[str], comments: Sequence[str]) -> str:
        output_mode = self.config['multi_line_output'].name.lower()
        formatter = getattr(self, "_output_" + output_mode, self._output_grid)
        dynamic_indent = " " * (len(import_start) + 1)
        indent = self.config['indent']
        line_length = self.config['wrap_length'] or self.config['line_length']
        import_statement = formatter(import_start, copy.copy(from_imports),
                                     dynamic_indent, indent, line_length, comments)
        if self.config['balanced_wrapping']:
            lines = import_statement.split(self.line_separator)
            line_count = len(lines)
            if len(lines) > 1:
                minimum_length = min(len(line) for line in lines[:-1])
            else:
                minimum_length = 0
            new_import_statement = import_statement
            while (len(lines[-1]) < minimum_length and
                   len(lines) == line_count and line_length > 10):
                import_statement = new_import_statement
                line_length -= 1
                new_import_statement = formatter(import_start, copy.copy(from_imports),
                                                 dynamic_indent, indent, line_length, comments)
                lines = new_import_statement.split(self.line_separator)
        return import_statement

    def _output_grid(
        self,
        statement: str,
        imports: List[str],
        white_space: str,
        indent: str,
        line_length: int,
        comments: Sequence[str]
    ) -> str:
        statement += "(" + imports.pop(0)
        while imports:
            next_import = imports.pop(0)
            next_statement = self._add_comments(comments, statement + ", " + next_import)
            if len(next_statement.split(self.line_separator)[-1]) + 1 > line_length:
                lines = ['{0}{1}'.format(white_space, next_import.split(" ")[0])]
                for part in next_import.split(" ")[1:]:
                    new_line = '{0} {1}'.format(lines[-1], part)
                    if len(new_line) + 1 > line_length:
                        lines.append('{0}{1}'.format(white_space, part))
                    else:
                        lines[-1] = new_line
                next_import = self.line_separator.join(lines)
                statement = (self._add_comments(comments, "{0},".format(statement)) +
                             "{0}{1}".format(self.line_separator, next_import))
                comments = None
            else:
                statement += ", " + next_import
        return statement + ("," if self.config['include_trailing_comma'] else "") + ")"

    def _output_vertical(
        self,
        statement: str,
        imports: List[str],
        white_space: str,
        indent: str,
        line_length: int,
        comments: Sequence[str]
    ) -> str:
        first_import = self._add_comments(comments, imports.pop(0) + ",") + self.line_separator + white_space
        return "{0}({1}{2}{3})".format(
            statement,
            first_import,
            ("," + self.line_separator + white_space).join(imports),
            "," if self.config['include_trailing_comma'] else "",
        )

    def _output_hanging_indent(
        self,
        statement: str,
        imports: List[str],
        white_space: str,
        indent: str,
        line_length: int,
        comments: Sequence[str]
    ) -> str:
        statement += imports.pop(0)
        while imports:
            next_import = imports.pop(0)
            next_statement = self._add_comments(comments, statement + ", " + next_import)
            if len(next_statement.split(self.line_separator)[-1]) + 3 > line_length:
                next_statement = (self._add_comments(comments, "{0}, \\".format(statement)) +
                                  "{0}{1}{2}".format(self.line_separator, indent, next_import))
                comments = None
            statement = next_statement
        return statement

    def _output_vertical_hanging_indent(
        self,
        statement: str,
        imports: List[str],
        white_space: str,
        indent: str,
        line_length: int,
        comments: Sequence[str]
    ) -> str:
        return "{0}({1}{2}{3}{4}{5}{2})".format(
            statement,
            self._add_comments(comments),
            self.line_separator,
            indent,
            ("," + self.line_separator + indent).join(imports),
            "," if self.config['include_trailing_comma'] else "",
        )

    def _output_vertical_grid_common(
        self,
        statement: str,
        imports: List[str],
        white_space: str,
        indent: str,
        line_length: int,
        comments: Sequence[str],
        need_trailing_char: bool
    ) -> str:
        statement += self._add_comments(comments, "(") + self.line_separator + indent + imports.pop(0)
        while imports:
            next_import = imports.pop(0)
            next_statement = "{0}, {1}".format(statement, next_import)
            current_line_length = len(next_statement.split(self.line_separator)[-1])
            if imports or need_trailing_char:
                # If we have more imports we need to account for a comma after this import
                # We might also need to account for a closing ) we're going to add.
                current_line_length += 1
            if current_line_length > line_length:
                next_statement = "{0},{1}{2}{3}".format(statement, self.line_separator, indent, next_import)
            statement = next_statement
        if self.config['include_trailing_comma']:
            statement += ','
        return statement

    def _output_vertical_grid(
        self,
        statement: str,
        imports: List[str],
        white_space: str,
        indent: str,
        line_length: int,
        comments: Sequence[str],
    ) -> str:
        return self._output_vertical_grid_common(statement, imports, white_space, indent, line_length, comments,
                                                 True) + ")"

    def _output_vertical_grid_grouped(
        self,
        statement: str,
        imports: List[str],
        white_space: str,
        indent: str,
        line_length: int,
        comments: Sequence[str],
    ) -> str:
        return self._output_vertical_grid_common(statement, imports, white_space, indent, line_length, comments,
                                                 True) + self.line_separator + ")"

    def _output_vertical_grid_grouped_no_comma(
        self,
        statement: str,
        imports: List[str],
        white_space: str,
        indent: str,
        line_length: int,
        comments: Sequence[str],
    ) -> str:
        return self._output_vertical_grid_common(statement, imports, white_space, indent, line_length, comments,
                                                 False) + self.line_separator + ")"

    def _output_noqa(
        self,
        statement: str,
        imports: List[str],
        white_space: str,
        indent: str,
        line_length: int,
        comments: Sequence[str],
    ) -> str:
        retval = '{0}{1}'.format(statement, ', '.join(imports))
        comment_str = ' '.join(comments)
        if comments:
            if len(retval) + len(self.config['comment_prefix']) + 1 + len(comment_str) <= line_length:
                return '{0}{1} {2}'.format(retval, self.config['comment_prefix'], comment_str)
        else:
            if len(retval) <= line_length:
                return retval
        if comments:
            if "NOQA" in comments:
                return '{0}{1} {2}'.format(retval, self.config['comment_prefix'], comment_str)
            else:
                return '{0}{1} NOQA {2}'.format(retval, self.config['comment_prefix'], comment_str)
        else:
            return '{0}{1} NOQA'.format(retval, self.config['comment_prefix'])

    def _add_comments(
        self,
        comments: Sequence[str],
        original_string: str = ""
    ) -> str:
        """
            Returns a string with comments added if ignore_comments is not set.
        """
        if self.config['ignore_comments']:
            return partition_comment(original_string)[0]

        if not comments:
            return original_string
        else:
            return "{0}{1} {2}".format(partition_comment(original_string)[0],
                                       self.config['comment_prefix'],
                                       "; ".join(comments))
