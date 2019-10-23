"""Exposes a simple library to sort through imports within Python code

usage:
    SortImports(file_name)
or:
    sorted = SortImports(file_contents=file_contents).output
"""
import copy
import itertools
import re
from collections import OrderedDict, defaultdict, namedtuple
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from isort import utils
from isort.format import format_simplified

from . import output, parse, settings
from .finders import FindersManager
from .natural import nsorted
from .settings import WrapModes


class _SortImports:
    _import_line_intro_re = re.compile("^(?:from|import) ")
    _import_line_midline_import_re = re.compile(" import ")

    def __init__(self, file_contents: str, config: Dict[str, Any], extension: str = "py") -> None:
        self.config = config
        self.extension = extension

        self.remove_imports = [
            format_simplified(removal) for removal in self.config["remove_imports"]
        ]
        self._section_comments = [
            "# " + value
            for key, value in self.config.items()
            if key.startswith("import_heading") and value
        ]
        section_names = self.config["sections"]
        self.sections = namedtuple("Sections", section_names)(
            *[name for name in section_names]
        )  # type: Any

        (
            self.in_lines,
            self.out_lines,
            self.import_index,
            self.place_imports,
            self.import_placements,
            self.as_map,
            self.imports,
            self.comments,
            self._first_comment_index_start,
            self._first_comment_index_end,
            self.length_change,
            self.original_num_of_lines,
            self.line_separator,
        ) = parse.file_contents(
            file_contents,
            sections=self.sections,
            section_comments=self._section_comments,
            config=self.config,
        )

        if self.import_index != -1:
            self._add_formatted_imports()
        while self.out_lines and self.out_lines[-1].strip() == "":
            self.out_lines.pop(-1)
        self.out_lines.append("")
        self.output = self.line_separator.join(self.out_lines)

    def remove_whitespaces(self, contents: str) -> str:
        contents = contents.replace(self.line_separator, "").replace(" ", "").replace("\x0c", "")
        return contents

    def get_out_lines_without_top_comment(self) -> str:
        return self._strip_top_comments(self.out_lines, self.line_separator)

    def get_in_lines_without_top_comment(self) -> str:
        return self._strip_top_comments(self.in_lines, self.line_separator)

    def check_if_input_already_sorted(
        self, output: str, check_against: str, *, logging_file_path: str
    ) -> bool:
        if output.strip() == check_against.strip():
            if self.config["verbose"]:
                print("SUCCESS: {} Everything Looks Good!".format(logging_file_path))
            return True

        print("ERROR: {} Imports are incorrectly sorted.".format(logging_file_path))
        return False

    @staticmethod
    def _strip_top_comments(lines: Sequence[str], line_separator: str) -> str:
        """Strips # comments that exist at the top of the given lines"""
        lines = copy.copy(lines)
        while lines and lines[0].startswith("#"):
            lines = lines[1:]
        return line_separator.join(lines)

    @staticmethod
    def _module_key(
        module_name: str,
        config: Mapping[str, Any],
        sub_imports: bool = False,
        ignore_case: bool = False,
        section_name: Optional[Any] = None,
    ) -> str:
        match = re.match(r"^(\.+)\s*(.*)", module_name)
        if match:
            sep = " " if config["reverse_relative"] else "_"
            module_name = sep.join(match.groups())

        prefix = ""
        if ignore_case:
            module_name = str(module_name).lower()
        else:
            module_name = str(module_name)

        if sub_imports and config["order_by_type"]:
            if module_name.isupper() and len(module_name) > 1:  # see issue #376
                prefix = "A"
            elif module_name[0:1].isupper():
                prefix = "B"
            else:
                prefix = "C"
        if not config["case_sensitive"]:
            module_name = module_name.lower()
        if section_name is None or "length_sort_" + str(section_name).lower() not in config:
            length_sort = config["length_sort"]
        else:
            length_sort = config["length_sort_" + str(section_name).lower()]
        return "{}{}{}".format(
            module_name in config["force_to_top"] and "A" or "B",
            prefix,
            length_sort and (str(len(module_name)) + ":" + module_name) or module_name,
        )

    def _wrap(self, line: str) -> str:
        """
            Returns an import wrapped to the specified line-length, if possible.
        """
        wrap_mode = self.config["multi_line_output"]
        if len(line) > self.config["line_length"] and wrap_mode != WrapModes.NOQA:
            line_without_comment = line
            comment = None
            if "#" in line:
                line_without_comment, comment = line.split("#", 1)
            for splitter in ("import ", ".", "as "):
                exp = r"\b" + re.escape(splitter) + r"\b"
                if re.search(
                    exp, line_without_comment
                ) and not line_without_comment.strip().startswith(splitter):
                    line_parts = re.split(exp, line_without_comment)
                    if comment:
                        line_parts[-1] = "{}{}  #{}".format(
                            line_parts[-1].strip(),
                            "," if self.config["include_trailing_comma"] else "",
                            comment,
                        )
                    next_line = []
                    while (len(line) + 2) > (
                        self.config["wrap_length"] or self.config["line_length"]
                    ) and line_parts:
                        next_line.append(line_parts.pop())
                        line = splitter.join(line_parts)
                    if not line:
                        line = next_line.pop()

                    cont_line = self._wrap(
                        self.config["indent"] + splitter.join(next_line).lstrip()
                    )
                    if self.config["use_parentheses"]:
                        if splitter == "as ":
                            output = "{}{}{}".format(line, splitter, cont_line.lstrip())
                        else:
                            output = "{}{}({}{}{}{})".format(
                                line,
                                splitter,
                                self.line_separator,
                                cont_line,
                                ","
                                if self.config["include_trailing_comma"] and not comment
                                else "",
                                self.line_separator
                                if wrap_mode
                                in {
                                    WrapModes.VERTICAL_HANGING_INDENT,
                                    WrapModes.VERTICAL_GRID_GROUPED,
                                }
                                else "",
                            )
                        lines = output.split(self.line_separator)
                        if self.config["comment_prefix"] in lines[-1] and lines[-1].endswith(")"):
                            line, comment = lines[-1].split(self.config["comment_prefix"], 1)
                            lines[-1] = line + ")" + self.config["comment_prefix"] + comment[:-1]
                        return self.line_separator.join(lines)
                    return "{}{}\\{}{}".format(line, splitter, self.line_separator, cont_line)
        elif len(line) > self.config["line_length"] and wrap_mode == settings.WrapModes.NOQA:
            if "# NOQA" not in line:
                return "{}{} NOQA".format(line, self.config["comment_prefix"])

        return line

    def _add_straight_imports(
        self, straight_modules: Iterable[str], section: str, section_output: List[str]
    ) -> None:
        for module in straight_modules:
            if module in self.remove_imports:
                continue

            import_definition = []
            if module in self.as_map:
                if (
                    self.config["keep_direct_and_as_imports"]
                    and self.imports[section]["straight"][module]
                ):
                    import_definition.append("import {}".format(module))
                import_definition.extend(
                    "import {} as {}".format(module, as_import) for as_import in self.as_map[module]
                )
            else:
                import_definition.append("import {}".format(module))

            comments_above = self.comments["above"]["straight"].pop(module, None)
            if comments_above:
                if section_output and self.config.get("ensure_newline_before_comments"):
                    section_output.append("")
                section_output.extend(comments_above)
            section_output.extend(
                output.with_comments(
                    self.comments["straight"].get(module),
                    idef,
                    removed=self.config["ignore_comments"],
                    comment_prefix=self.config["comment_prefix"],
                )
                for idef in import_definition
            )

    def _add_from_imports(
        self,
        from_modules: Iterable[str],
        section: str,
        section_output: List[str],
        ignore_case: bool,
    ) -> None:
        for module in from_modules:
            if module in self.remove_imports:
                continue

            import_start = "from {} import ".format(module)
            from_imports = list(self.imports[section]["from"][module])
            if not self.config["no_inline_sort"] or self.config["force_single_line"]:
                from_imports = nsorted(
                    from_imports,
                    key=lambda key: self._module_key(
                        key, self.config, True, ignore_case, section_name=section
                    ),
                )
            if self.remove_imports:
                from_imports = [
                    line
                    for line in from_imports
                    if not "{}.{}".format(module, line) in self.remove_imports
                ]

            sub_modules = ["{}.{}".format(module, from_import) for from_import in from_imports]
            as_imports = {
                from_import: [
                    "{} as {}".format(from_import, as_module)
                    for as_module in self.as_map[sub_module]
                ]
                for from_import, sub_module in zip(from_imports, sub_modules)
                if sub_module in self.as_map
            }
            if self.config["combine_as_imports"] and not (
                "*" in from_imports and self.config["combine_star"]
            ):
                if not self.config["no_inline_sort"]:
                    for as_import in as_imports:
                        as_imports[as_import] = nsorted(as_imports[as_import])
                for from_import in copy.copy(from_imports):
                    if from_import in as_imports:
                        idx = from_imports.index(from_import)
                        if (
                            self.config["keep_direct_and_as_imports"]
                            and self.imports[section]["from"][module][from_import]
                        ):
                            from_imports[(idx + 1) : (idx + 1)] = as_imports.pop(from_import)
                        else:
                            from_imports[idx : (idx + 1)] = as_imports.pop(from_import)

            while from_imports:
                comments = self.comments["from"].pop(module, ())
                if "*" in from_imports and self.config["combine_star"]:
                    import_statement = self._wrap(
                        output.with_comments(
                            comments,
                            "{}*".format(import_start),
                            removed=self.config["ignore_comments"],
                            comment_prefix=self.config["comment_prefix"],
                        )
                    )
                    from_imports = None
                elif self.config["force_single_line"]:
                    import_statement = None
                    while from_imports:
                        from_import = from_imports.pop(0)
                        single_import_line = output.with_comments(
                            comments,
                            import_start + from_import,
                            removed=self.config["ignore_comments"],
                            comment_prefix=self.config["comment_prefix"],
                        )
                        comment = self.comments["nested"].get(module, {}).pop(from_import, None)
                        if comment:
                            single_import_line += "{} {}".format(
                                comments and ";" or self.config["comment_prefix"], comment
                            )
                        if from_import in as_imports:
                            if (
                                self.config["keep_direct_and_as_imports"]
                                and self.imports[section]["from"][module][from_import]
                            ):
                                section_output.append(self._wrap(single_import_line))
                            from_comments = self.comments["straight"].get(
                                "{}.{}".format(module, from_import)
                            )
                            section_output.extend(
                                output.with_comments(
                                    from_comments,
                                    self._wrap(import_start + as_import),
                                    removed=self.config["ignore_comments"],
                                    comment_prefix=self.config["comment_prefix"],
                                )
                                for as_import in nsorted(as_imports[from_import])
                            )
                        else:
                            section_output.append(self._wrap(single_import_line))
                        comments = None
                else:
                    while from_imports and from_imports[0] in as_imports:
                        from_import = from_imports.pop(0)
                        as_imports[from_import] = nsorted(as_imports[from_import])
                        from_comments = self.comments["straight"].get(
                            "{}.{}".format(module, from_import)
                        )
                        above_comments = self.comments["above"]["from"].pop(module, None)
                        if above_comments:
                            if section_output and self.config.get("ensure_newline_before_comments"):
                                section_output.append("")
                            section_output.extend(above_comments)

                        if (
                            self.config["keep_direct_and_as_imports"]
                            and self.imports[section]["from"][module][from_import]
                        ):
                            section_output.append(
                                output.with_comments(
                                    from_comments,
                                    self._wrap(import_start + from_import),
                                    removed=self.config["ignore_comments"],
                                    comment_prefix=self.config["comment_prefix"],
                                )
                            )
                        section_output.extend(
                            output.with_comments(
                                from_comments,
                                self._wrap(import_start + as_import),
                                removed=self.config["ignore_comments"],
                                comment_prefix=self.config["comment_prefix"],
                            )
                            for as_import in as_imports[from_import]
                        )

                    star_import = False
                    if "*" in from_imports:
                        section_output.append(
                            output.with_comments(
                                comments,
                                "{}*".format(import_start),
                                removed=self.config["ignore_comments"],
                                comment_prefix=self.config["comment_prefix"],
                            )
                        )
                        from_imports.remove("*")
                        star_import = True
                        comments = None

                    for from_import in copy.copy(from_imports):
                        if (
                            from_import in as_imports
                            and not self.config["keep_direct_and_as_imports"]
                        ):
                            continue
                        comment = self.comments["nested"].get(module, {}).pop(from_import, None)
                        if comment:
                            single_import_line = output.with_comments(
                                comments,
                                import_start + from_import,
                                removed=self.config["ignore_comments"],
                                comment_prefix=self.config["comment_prefix"],
                            )
                            single_import_line += "{} {}".format(
                                comments and ";" or self.config["comment_prefix"], comment
                            )
                            above_comments = self.comments["above"]["from"].pop(module, None)
                            if above_comments:
                                if section_output and self.config.get(
                                    "ensure_newline_before_comments"
                                ):
                                    section_output.append("")
                                section_output.extend(above_comments)
                            section_output.append(self._wrap(single_import_line))
                            from_imports.remove(from_import)
                            comments = None

                    from_import_section = []
                    while from_imports and (
                        from_imports[0] not in as_imports
                        or (
                            self.config["keep_direct_and_as_imports"]
                            and self.config["combine_as_imports"]
                            and self.imports[section]["from"][module][from_import]
                        )
                    ):
                        from_import_section.append(from_imports.pop(0))
                    if star_import:
                        import_statement = import_start + (", ").join(from_import_section)
                    else:
                        import_statement = output.with_comments(
                            comments,
                            import_start + (", ").join(from_import_section),
                            removed=self.config["ignore_comments"],
                            comment_prefix=self.config["comment_prefix"],
                        )
                    if not from_import_section:
                        import_statement = ""

                    do_multiline_reformat = False

                    force_grid_wrap = self.config["force_grid_wrap"]
                    if force_grid_wrap and len(from_import_section) >= force_grid_wrap:
                        do_multiline_reformat = True

                    if (
                        len(import_statement) > self.config["line_length"]
                        and len(from_import_section) > 1
                    ):
                        do_multiline_reformat = True

                    # If line too long AND have imports AND we are
                    # NOT using GRID or VERTICAL wrap modes
                    if (
                        len(import_statement) > self.config["line_length"]
                        and len(from_import_section) > 0
                        and self.config["multi_line_output"]
                        not in (settings.WrapModes.GRID, settings.WrapModes.VERTICAL)
                    ):
                        do_multiline_reformat = True

                    if do_multiline_reformat:
                        import_statement = self._multi_line_reformat(
                            import_start, from_import_section, comments
                        )
                        if self.config["multi_line_output"] == settings.WrapModes.GRID:
                            self.config["multi_line_output"] = settings.WrapModes.VERTICAL_GRID
                            try:
                                other_import_statement = self._multi_line_reformat(
                                    import_start, from_import_section, comments
                                )
                                if (
                                    max(len(x) for x in import_statement.split("\n"))
                                    > self.config["line_length"]
                                ):
                                    import_statement = other_import_statement
                            finally:
                                self.config["multi_line_output"] = settings.WrapModes.GRID
                    if (
                        not do_multiline_reformat
                        and len(import_statement) > self.config["line_length"]
                    ):
                        import_statement = self._wrap(import_statement)

                if import_statement:
                    above_comments = self.comments["above"]["from"].pop(module, None)
                    if above_comments:
                        if section_output and self.config.get("ensure_newline_before_comments"):
                            section_output.append("")
                        section_output.extend(above_comments)
                    section_output.append(import_statement)

    def _multi_line_reformat(
        self, import_start: str, from_imports: List[str], comments: Sequence[str]
    ) -> str:
        output_mode = self.config["multi_line_output"].name.lower()
        formatter = getattr(output, output_mode, output.grid)
        dynamic_indent = " " * (len(import_start) + 1)
        indent = self.config["indent"]
        line_length = self.config["wrap_length"] or self.config["line_length"]
        import_statement = formatter(
            import_start,
            copy.copy(from_imports),
            dynamic_indent,
            indent,
            line_length,
            comments,
            line_separator=self.line_separator,
            comment_prefix=self.config["comment_prefix"],
            include_trailing_comma=self.config["include_trailing_comma"],
            remove_comments=self.config["ignore_comments"],
        )
        if self.config["balanced_wrapping"]:
            lines = import_statement.split(self.line_separator)
            line_count = len(lines)
            if len(lines) > 1:
                minimum_length = min(len(line) for line in lines[:-1])
            else:
                minimum_length = 0
            new_import_statement = import_statement
            while len(lines[-1]) < minimum_length and len(lines) == line_count and line_length > 10:
                import_statement = new_import_statement
                line_length -= 1
                new_import_statement = formatter(
                    import_start,
                    copy.copy(from_imports),
                    dynamic_indent,
                    indent,
                    line_length,
                    comments,
                    line_separator=self.line_separator,
                    comment_prefix=self.config["comment_prefix"],
                    include_trailing_comma=self.config["include_trailing_comma"],
                    remove_comments=self.config["ignore_comments"],
                )
                lines = new_import_statement.split(self.line_separator)
        if import_statement.count(self.line_separator) == 0:
            return self._wrap(import_statement)
        return import_statement

    def _add_formatted_imports(self) -> None:
        """Adds the imports back to the file.

        (at the index of the first import) sorted alphabetically and split between groups

        """
        sort_ignore_case = self.config["force_alphabetical_sort_within_sections"]
        sections = itertools.chain(
            self.sections, self.config["forced_separate"]
        )  # type: Iterable[str]

        if self.config["no_sections"]:
            self.imports["no_sections"] = {"straight": [], "from": {}}
            for section in sections:
                self.imports["no_sections"]["straight"].extend(
                    self.imports[section].get("straight", [])
                )
                self.imports["no_sections"]["from"].update(self.imports[section].get("from", {}))
            sections = ("no_sections",)

        output = []  # type: List[str]
        pending_lines_before = False
        for section in sections:
            straight_modules = self.imports[section]["straight"]
            straight_modules = nsorted(
                straight_modules,
                key=lambda key: self._module_key(key, self.config, section_name=section),
            )
            from_modules = self.imports[section]["from"]
            from_modules = nsorted(
                from_modules,
                key=lambda key: self._module_key(key, self.config, section_name=section),
            )

            if self.config["force_sort_within_sections"]:
                copied_comments = copy.deepcopy(self.comments)

            section_output = []  # type: List[str]
            if self.config["from_first"]:
                self._add_from_imports(from_modules, section, section_output, sort_ignore_case)
                if self.config["lines_between_types"] and from_modules and straight_modules:
                    section_output.extend([""] * self.config["lines_between_types"])
                self._add_straight_imports(straight_modules, section, section_output)
            else:
                self._add_straight_imports(straight_modules, section, section_output)
                if self.config["lines_between_types"] and from_modules and straight_modules:
                    section_output.extend([""] * self.config["lines_between_types"])
                self._add_from_imports(from_modules, section, section_output, sort_ignore_case)

            if self.config["force_sort_within_sections"]:

                def by_module(line: str) -> str:
                    section = "B"

                    line = self._import_line_intro_re.sub(
                        "", self._import_line_midline_import_re.sub(".", line)
                    )
                    if line.split(" ")[0] in self.config["force_to_top"]:
                        section = "A"
                    if not self.config["order_by_type"]:
                        line = line.lower()
                    return "{}{}".format(section, line)

                # Remove comments
                section_output = [line for line in section_output if not line.startswith("#")]

                section_output = nsorted(section_output, key=by_module)

                # Add comments back
                all_comments = copied_comments["above"]["from"]
                all_comments.update(copied_comments["above"]["straight"])
                comment_indexes = {}
                for module, comment_list in all_comments.items():
                    for idx, line in enumerate(section_output):
                        if module in line:
                            comment_indexes[idx] = comment_list
                added = 0
                for idx, comment_list in comment_indexes.items():
                    for comment in comment_list:
                        section_output.insert(idx + added, comment)
                        added += 1

            section_name = section
            no_lines_before = section_name in self.config["no_lines_before"]

            if section_output:
                if section_name in self.place_imports:
                    self.place_imports[section_name] = section_output
                    continue

                section_title = self.config.get("import_heading_" + str(section_name).lower(), "")
                if section_title:
                    section_comment = "# {}".format(section_title)
                    if (
                        section_comment not in self.out_lines[0:1]
                        and section_comment not in self.in_lines[0:1]
                    ):
                        section_output.insert(0, section_comment)

                if pending_lines_before or not no_lines_before:
                    output += [""] * self.config["lines_between_sections"]

                output += section_output

                pending_lines_before = False
            else:
                pending_lines_before = pending_lines_before or not no_lines_before

        while output and output[-1].strip() == "":
            output.pop()
        while output and output[0].strip() == "":
            output.pop(0)

        output_at = 0
        if self.import_index < self.original_num_of_lines:
            output_at = self.import_index
        elif self._first_comment_index_end != -1 and self._first_comment_index_start <= 2:
            output_at = self._first_comment_index_end
        self.out_lines[output_at:0] = output

        imports_tail = output_at + len(output)
        while [
            character.strip() for character in self.out_lines[imports_tail : imports_tail + 1]
        ] == [""]:
            self.out_lines.pop(imports_tail)

        if len(self.out_lines) > imports_tail:
            next_construct = ""
            self._in_quote = False  # type: Any
            tail = self.out_lines[imports_tail:]

            for index, line in enumerate(tail):
                in_quote = self._in_quote
                (
                    should_skip,
                    self._in_quote,
                    self.in_top_comment,
                    self._first_comment_index_start,
                    self._first_comment_index_end,
                ) = parse.skip_line(
                    line,
                    in_quote=self._in_quote,
                    in_top_comment=False,
                    index=len(self.out_lines),
                    section_comments=self._section_comments,
                    first_comment_index_start=self._first_comment_index_start,
                    first_comment_index_end=self._first_comment_index_end,
                )
                if not should_skip and line.strip():
                    if (
                        line.strip().startswith("#")
                        and len(tail) > (index + 1)
                        and tail[index + 1].strip()
                    ):
                        continue
                    next_construct = line
                    break
                elif not in_quote:
                    parts = line.split()
                    if (
                        len(parts) >= 3
                        and parts[1] == "="
                        and "'" not in parts[0]
                        and '"' not in parts[0]
                    ):
                        next_construct = line
                        break

            if self.config["lines_after_imports"] != -1:
                self.out_lines[imports_tail:0] = [
                    "" for line in range(self.config["lines_after_imports"])
                ]
            elif self.extension != "pyi" and (
                next_construct.startswith("def ")
                or next_construct.startswith("class ")
                or next_construct.startswith("@")
                or next_construct.startswith("async def")
            ):
                self.out_lines[imports_tail:0] = ["", ""]
            else:
                self.out_lines[imports_tail:0] = [""]

        if self.place_imports:
            new_out_lines = []
            for index, line in enumerate(self.out_lines):
                new_out_lines.append(line)
                if line in self.import_placements:
                    new_out_lines.extend(self.place_imports[self.import_placements[line]])
                    if len(self.out_lines) <= index or self.out_lines[index + 1].strip() != "":
                        new_out_lines.append("")
            self.out_lines = new_out_lines
