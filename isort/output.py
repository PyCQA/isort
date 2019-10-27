from typing import List, Optional

from . import parse, sorting


_import_line_intro_re = re.compile("^(?:from|import) ")
_import_line_midline_import_re = re.compile(" import ")

def with_comments(
    comments: Optional[List[str]],
    original_string: str = "",
    removed: bool = False,
    comment_prefix: str = "",
) -> str:
    """Returns a string with comments added if removed is not set."""
    if removed:
        return parse.import_comment(original_string)[0]

    if not comments:
        return original_string
    else:
        return "{}{} {}".format(
            parse.import_comment(original_string)[0], comment_prefix, "; ".join(comments)
        )



class ParsedContent(NamedTuple):
    in_lines: List[str]
    lines_without_imports: List[str]
    import_index: int
    place_imports: Dict[str, List[str]]
    import_placements: Dict[str, str]
    as_map: Dict[str, List[str]]
    imports: Dict[str, Dict[str, Any]]
    categorized_comments: "CommentsDict"
    first_comment_index_start: int
    first_comment_index_end: int
    change_count: int
    original_line_count: int
    line_separator: str
    sections: Any
    section_comments: List[str]




def with_formatted_imports(parsed: parse.ParsedContent, config: Dict[str, Any], extension: str="py"):
        """Adds the imports back to the file.

        (at the index of the first import) sorted alphabetically and split between groups

        """
        sort_ignore_case = config["force_alphabetical_sort_within_sections"]
        sections: Iterable[str] = itertools.chain(parsed.sections, config["forced_separate"])

        if config["no_sections"]:
            parsed.imports["no_sections"] = {"straight": [], "from": {}}
            for section in sections:
                parsed.imports["no_sections"]["straight"].extend(
                    parsed.imports[section].get("straight", [])
                )
                parsed.imports["no_sections"]["from"].update(parsed.imports[section].get("from", {}))
            sections = ("no_sections",)

        output: List[str] = []
        pending_lines_before = False
        for section in sections:
            straight_modules = parsed.imports[section]["straight"]
            straight_modules = nsorted(
                straight_modules,
                key=lambda key: sorting.module_key(key, config, section_name=section),
            )
            from_modules = parsed.imports[section]["from"]
            from_modules = nsorted(
                from_modules,
                key=lambda key: sorting.module_key(key, config, section_name=section),
            )

            if config["force_sort_within_sections"]:
                copied_comments = copy.deepcopy(parsed.categorized_comments)

            section_output: List[str] = []
            if config["from_first"]:
                self._add_from_imports(from_modules, section, section_output, sort_ignore_case)
                if config["lines_between_types"] and from_modules and straight_modules:
                    section_output.extend([""] * config["lines_between_types"])
                self._add_straight_imports(straight_modules, section, section_output)
            else:
                self._add_straight_imports(straight_modules, section, section_output)
                if config["lines_between_types"] and from_modules and straight_modules:
                    section_output.extend([""] * config["lines_between_types"])
                self._add_from_imports(from_modules, section, section_output, sort_ignore_case)

            if config["force_sort_within_sections"]:

                def by_module(line: str) -> str:
                    section = "B"

                    line = _import_line_intro_re.sub(
                        "", _import_line_midline_import_re.sub(".", line)
                    )
                    if line.split(" ")[0] in config["force_to_top"]:
                        section = "A"
                    if not config["order_by_type"]:
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
            no_lines_before = section_name in config["no_lines_before"]

            if section_output:
                if section_name in parsed.place_imports:
                    parsed.place_imports[section_name] = section_output
                    continue

                section_title = config.get("import_heading_" + str(section_name).lower(), "")
                if section_title:
                    section_comment = "# {}".format(section_title)
                    if (
                        section_comment not in parsed.lines_without_imports[0:1]
                        and section_comment not in parsed.in_lines[0:1]
                    ):
                        section_output.insert(0, section_comment)

                if pending_lines_before or not no_lines_before:
                    output += [""] * config["lines_between_sections"]

                output += section_output

                pending_lines_before = False
            else:
                pending_lines_before = pending_lines_before or not no_lines_before

        while output and output[-1].strip() == "":
            output.pop()
        while output and output[0].strip() == "":
            output.pop(0)

        output_at = 0
        if parsed.import_index < parsed.original_line_count:
            output_at = parsed.import_index
        elif parsed.first_comment_index_end != -1 and parsed.first_comment_index_start <= 2:
            output_at = parsed.first_comment_index_end
        parsed.lines_without_imports[output_at:0] = output

        imports_tail = output_at + len(output)
        while [
            character.strip() for character in parsed.lines_without_imports[imports_tail : imports_tail + 1]
        ] == [""]:
            parsed.lines_without_imports.pop(imports_tail)

        if len(parsed.lines_without_imports) > imports_tail:
            next_construct = ""
            _in_quote: str = ""
            tail = parsed.lines_without_imports[imports_tail:]

            for index, line in enumerate(tail):
                in_quote = _in_quote
                (
                    should_skip,
                    _in_quote,
                    _in_top_comment,
                    _first_comment_index_start,
                    self._first_comment_index_end,
                ) = parse.skip_line(
                    line,
                    in_quote=self._in_quote,
                    in_top_comment=False,
                    index=len(parsed.lines_without_imports),
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

            if config["lines_after_imports"] != -1:
                parsed.lines_without_imports[imports_tail:0] = [
                    "" for line in range(config["lines_after_imports"])
                ]
            elif self.extension != "pyi" and (
                next_construct.startswith("def ")
                or next_construct.startswith("class ")
                or next_construct.startswith("@")
                or next_construct.startswith("async def")
            ):
                parsed.lines_without_imports[imports_tail:0] = ["", ""]
            else:
                parsed.lines_without_imports[imports_tail:0] = [""]

        if parsed.place_imports:
            new_out_lines = []
            for index, line in enumerate(parsed.lines_without_imports):
                new_out_lines.append(line)
                if line in parsed.import_placements:
                    new_out_lines.extend(parsed.place_imports[parsed.import_placements[line]])
                    if len(parsed.lines_without_imports) <= index or parsed.lines_without_imports[index + 1].strip() != "":
                        new_out_lines.append("")
            parsed.lines_without_imports = new_out_lines
