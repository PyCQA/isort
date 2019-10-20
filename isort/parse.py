"""Defines parsing functions used by isort for parsing import definitions"""
from typing import Tuple, List, Generator, Iterator


def import_comment(line: str) -> Tuple[str, str]:
    """Parses import lines for comments and returns back the
    import statement and the associated comment.
    """
    comment_start = line.find("#")
    if comment_start != -1:
        return (line[:comment_start], line[comment_start + 1 :].strip())

    return (line, "")


def skip_line(line: str, in_quote: str, in_top_comment: bool, index: int,
              section_comments: Iterator[str], first_comment_index_start: int,
              first_comment_index_end: int) -> (bool, str, bool, int, int):
    skip_line = bool(in_quote)
    if index == 1 and line.startswith("#"):
        in_top_comment = True
        return True
    elif in_top_comment:
        if not line.startswith("#") or line in section_comments:
            in_top_comment = False
            first_comment_index_end = index - 1

    if '"' in line or "'" in line:
        index = 0
        if first_comment_index_start == -1 and (
            line.startswith('"') or line.startswith("'")
        ):
            first_comment_index_start = index
        while char_index < len(line):
            if line[char_index] == "\\":
                char_index += 1
            elif in_quote:
                if line[char_index : char_index + len(in_quote)] == in_quote:
                    in_quote = ""
                    if first_comment_index_end < first_comment_index_start:
                        first_comment_index_end = index
            elif line[char_index] in ("'", '"'):
                long_quote = line[char_index : char_index + 3]
                if long_quote in ('"""', "'''"):
                    in_quote = long_quote
                    char_index += 2
                else:
                    in_quote = line[char_index]
            elif line[char_index] == "#":
                break
            char_index += 1

    return (bool(skip_line or in_quote or in_top_comment), in_quote,
            in_top_comment, first_comment_index_start, first_comment_index_end)


def file_contents(contents: str, line_separator: str, add_imports: Iterator[str], force_adds: bool) -> dict:
    """Parses a python file taking out and categorizing imports."""
    in_lines = contents.split(line_separator)
    original_line_count = len(in_lines)

    if original_line_count > 1 or in_lines[:1] not in ([], [""]) or force_adds:
        in_lines.extend(add_imports)

    line_count = len(in_lines)



    self._in_quote = False
    self._in_top_comment = False
    while not self._at_end():
        raw_line = line = self._get_line()
        line = line.replace("from.import ", "from . import ")
        line = line.replace("\t", " ").replace("import*", "import *")
        line = line.replace(" .import ", " . import ")
        statement_index = self.index
        skip_line = self._skip_line(line)

        if line in self._section_comments and not skip_line:
            if self.import_index == -1:
                self.import_index = self.index - 1
            continue

        if "isort:imports-" in line and line.startswith("#"):
            section = line.split("isort:imports-")[-1].split()[0].upper()
            self.place_imports[section] = []
            self.import_placements[line] = section

        if ";" in line:
            for part in (part.strip() for part in line.split(";")):
                if part and not part.startswith("from ") and not part.startswith("import "):
                    skip_line = True

        import_type = self._import_type(line)
        if not import_type or skip_line:
            self.out_lines.append(raw_line)
            continue

        for line in (line.strip() for line in line.split(";")):
            import_type = self._import_type(line)
            if not import_type:
                self.out_lines.append(line)
                continue

            if self.import_index == -1:
                self.import_index = self.index - 1
            nested_comments = {}
            import_string, comment = parse.import_comment(line)
            comments = [comment] if comment else []
            line_parts = [
                part for part in self._strip_syntax(import_string).strip().split(" ") if part
            ]
            if (
                import_type == "from"
                and len(line_parts) == 2
                and line_parts[1] != "*"
                and comments
            ):
                nested_comments[line_parts[-1]] = comments[0]

            if "(" in line.split("#")[0] and not self._at_end():
                while not line.strip().endswith(")") and not self._at_end():
                    line, new_comment = parse.import_comment(self._get_line())
                    if new_comment:
                        comments.append(new_comment)
                    stripped_line = self._strip_syntax(line).strip()
                    if (
                        import_type == "from"
                        and stripped_line
                        and " " not in stripped_line
                        and new_comment
                    ):
                        nested_comments[stripped_line] = comments[-1]
                    import_string += self.line_separator + line
            else:
                while line.strip().endswith("\\"):
                    line, new_comment = parse.import_comment(self._get_line())
                    if new_comment:
                        comments.append(new_comment)

                    # Still need to check for parentheses after an escaped line
                    if (
                        "(" in line.split("#")[0]
                        and ")" not in line.split("#")[0]
                        and not self._at_end()
                    ):
                        stripped_line = self._strip_syntax(line).strip()
                        if (
                            import_type == "from"
                            and stripped_line
                            and " " not in stripped_line
                            and new_comment
                        ):
                            nested_comments[stripped_line] = comments[-1]
                        import_string += self.line_separator + line

                        while not line.strip().endswith(")") and not self._at_end():
                            line, new_comment = parse.import_comment(self._get_line())
                            if new_comment:
                                comments.append(new_comment)
                            stripped_line = self._strip_syntax(line).strip()
                            if (
                                import_type == "from"
                                and stripped_line
                                and " " not in stripped_line
                                and new_comment
                            ):
                                nested_comments[stripped_line] = comments[-1]
                            import_string += self.line_separator + line

                    stripped_line = self._strip_syntax(line).strip()
                    if (
                        import_type == "from"
                        and stripped_line
                        and " " not in stripped_line
                        and new_comment
                    ):
                        nested_comments[stripped_line] = comments[-1]
                    if import_string.strip().endswith(" import") or line.strip().startswith(
                        "import "
                    ):
                        import_string += self.line_separator + line
                    else:
                        import_string = (
                            import_string.rstrip().rstrip("\\") + " " + line.lstrip()
                        )

            if import_type == "from":
                import_string = import_string.replace("import(", "import (")
                parts = import_string.split(" import ")
                from_import = parts[0].split(" ")
                import_string = " import ".join(
                    [from_import[0] + " " + "".join(from_import[1:])] + parts[1:]
                )

            imports = [
                item.replace("{|", "{ ").replace("|}", " }")
                for item in self._strip_syntax(import_string).split()
            ]
            straight_import = True
            if "as" in imports and (imports.index("as") + 1) < len(imports):
                straight_import = False
                while "as" in imports:
                    index = imports.index("as")
                    if import_type == "from":
                        module = imports[0] + "." + imports[index - 1]
                        self.as_map[module].append(imports[index + 1])
                    else:
                        module = imports[index - 1]
                        self.as_map[module].append(imports[index + 1])
                    if not self.config["combine_as_imports"]:
                        self.comments["straight"][module] = comments
                        comments = []
                    del imports[index : index + 2]
            if import_type == "from":
                import_from = imports.pop(0)
                placed_module = self.place_module(import_from)
                if self.config["verbose"]:
                    print(
                        "from-type place_module for {} returned {}".format(
                            import_from, placed_module
                        )
                    )
                if placed_module == "":
                    print(
                        "WARNING: could not place module {} of line {} --"
                        " Do you need to define a default section?".format(import_from, line)
                    )
                root = self.imports[placed_module][import_type]
                for import_name in imports:
                    associated_comment = nested_comments.get(import_name)
                    if associated_comment:
                        self.comments["nested"].setdefault(import_from, {})[
                            import_name
                        ] = associated_comment
                        comments.pop(comments.index(associated_comment))
                if comments:
                    self.comments["from"].setdefault(import_from, []).extend(comments)

                if (
                    len(self.out_lines)
                    > max(self.import_index, self._first_comment_index_end + 1, 1) - 1
                ):
                    last = self.out_lines and self.out_lines[-1].rstrip() or ""
                    while (
                        last.startswith("#")
                        and not last.endswith('"""')
                        and not last.endswith("'''")
                        and "isort:imports-" not in last
                    ):
                        self.comments["above"]["from"].setdefault(import_from, []).insert(
                            0, self.out_lines.pop(-1)
                        )
                        if (
                            len(self.out_lines)
                            > max(self.import_index - 1, self._first_comment_index_end + 1, 1)
                            - 1
                        ):
                            last = self.out_lines[-1].rstrip()
                        else:
                            last = ""
                    if statement_index - 1 == self.import_index:
                        self.import_index -= len(
                            self.comments["above"]["from"].get(import_from, [])
                        )

                if import_from not in root:
                    root[import_from] = OrderedDict(
                        (module, straight_import) for module in imports
                    )
                else:
                    root[import_from].update(
                        (module, straight_import | root[import_from].get(module, False))
                        for module in imports
                    )
            else:
                for module in imports:
                    if comments:
                        self.comments["straight"][module] = comments
                        comments = None

                    if (
                        len(self.out_lines)
                        > max(self.import_index, self._first_comment_index_end + 1, 1) - 1
                    ):

                        last = self.out_lines and self.out_lines[-1].rstrip() or ""
                        while (
                            last.startswith("#")
                            and not last.endswith('"""')
                            and not last.endswith("'''")
                            and "isort:imports-" not in last
                        ):
                            self.comments["above"]["straight"].setdefault(module, []).insert(
                                0, self.out_lines.pop(-1)
                            )
                            if (
                                len(self.out_lines) > 0
                                and len(self.out_lines) != self._first_comment_index_end
                            ):
                                last = self.out_lines[-1].rstrip()
                            else:
                                last = ""
                        if self.index - 1 == self.import_index:
                            self.import_index -= len(
                                self.comments["above"]["straight"].get(module, [])
                            )
                    placed_module = self.place_module(module)
                    if self.config["verbose"]:
                        print(
                            "else-type place_module for {} returned {}".format(
                                module, placed_module
                            )
                        )
                    if placed_module == "":
                        print(
                            "WARNING: could not place module {} of line {} --"
                            " Do you need to define a default section?".format(
                                import_from, line
                            )
                        )
                    straight_import |= self.imports[placed_module][import_type].get(
                        module, False
                    )
                    self.imports[placed_module][import_type][module] = straight_import
