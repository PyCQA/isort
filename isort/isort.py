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

from . import output, parse, settings, wrap, sorting, output
from .finders import FindersManager
from .natural import nsorted


class _SortImports:

    def __init__(self, file_contents: str, config: Dict[str, Any], extension: str = "py") -> None:
        self.config = config
        self.extension = extension

        self.remove_imports = [
            format_simplified(removal) for removal in self.config["remove_imports"]
        ]

        parsed = parse.file_contents(file_contents, config=self.config)
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
            self.sections,
            self._section_comments,
        ) = parsed

        if self.import_index != -1:
            output.with_formatted_imports(parsed, self.config, self.extension)
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
                    key=lambda key: sorting.module_key(
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
                    import_statement = wrap.line(
                        output.with_comments(
                            comments,
                            "{}*".format(import_start),
                            removed=self.config["ignore_comments"],
                            comment_prefix=self.config["comment_prefix"],
                        ),
                        self.line_separator,
                        self.config,
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
                                section_output.append(
                                    wrap.line(single_import_line, self.line_separator, self.config)
                                )
                            from_comments = self.comments["straight"].get(
                                "{}.{}".format(module, from_import)
                            )
                            section_output.extend(
                                output.with_comments(
                                    from_comments,
                                    wrap.line(
                                        import_start + as_import, self.line_separator, self.config
                                    ),
                                    removed=self.config["ignore_comments"],
                                    comment_prefix=self.config["comment_prefix"],
                                )
                                for as_import in nsorted(as_imports[from_import])
                            )
                        else:
                            section_output.append(
                                wrap.line(single_import_line, self.line_separator, self.config)
                            )
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
                                    wrap.line(
                                        import_start + from_import, self.line_separator, self.config
                                    ),
                                    removed=self.config["ignore_comments"],
                                    comment_prefix=self.config["comment_prefix"],
                                )
                            )
                        section_output.extend(
                            output.with_comments(
                                from_comments,
                                wrap.line(
                                    import_start + as_import, self.line_separator, self.config
                                ),
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
                            section_output.append(
                                wrap.line(single_import_line, self.line_separator, self.config)
                            )
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
                        not in (
                            wrap.Modes.GRID,  # type: ignore
                            wrap.Modes.VERTICAL,  # type: ignore
                        )
                    ):
                        do_multiline_reformat = True

                    if do_multiline_reformat:
                        import_statement = wrap.import_statement(
                            import_start,
                            from_import_section,
                            comments,
                            self.config,
                            self.line_separator,
                        )
                        if (
                            self.config["multi_line_output"] == wrap.Modes.GRID  # type: ignore
                        ):  # type: ignore
                            self.config[
                                "multi_line_output"
                            ] = wrap.Modes.VERTICAL_GRID  # type: ignore
                            try:
                                other_import_statement = wrap.import_statement(
                                    import_start,
                                    from_import_section,
                                    comments,
                                    self.config,
                                    self.line_separator,
                                )
                                if (
                                    max(len(x) for x in import_statement.split("\n"))
                                    > self.config["line_length"]
                                ):
                                    import_statement = other_import_statement
                            finally:
                                self.config["multi_line_output"] = wrap.Modes.GRID  # type: ignore
                    if (
                        not do_multiline_reformat
                        and len(import_statement) > self.config["line_length"]
                    ):
                        import_statement = wrap.line(
                            import_statement, self.line_separator, self.config
                        )

                if import_statement:
                    above_comments = self.comments["above"]["from"].pop(module, None)
                    if above_comments:
                        if section_output and self.config.get("ensure_newline_before_comments"):
                            section_output.append("")
                        section_output.extend(above_comments)
                    section_output.append(import_statement)
