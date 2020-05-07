import copy
import itertools
from functools import partial
from typing import Iterable, List, Tuple

from isort.format import format_simplified

from . import parse, sorting, wrap
from .comments import add_to_line as with_comments
from .settings import DEFAULT_CONFIG, Config

STATEMENT_DECLERATIONS: Tuple[str, ...] = ("def ", "cdef ", "cpdef ", "class ", "@", "async def")


def sorted_imports(
    parsed: parse.ParsedContent,
    config: Config = DEFAULT_CONFIG,
    extension: str = "py",
    import_type: str = "import",
) -> str:
    """Adds the imports back to the file.

    (at the index of the first import) sorted alphabetically and split between groups

    """
    if parsed.import_index == -1:
        return _output_as_string(parsed.lines_without_imports, parsed.line_separator)

    formatted_output: List[str] = parsed.lines_without_imports.copy()
    remove_imports = [format_simplified(removal) for removal in config.remove_imports]

    sort_ignore_case = config.force_alphabetical_sort_within_sections
    sections: Iterable[str] = itertools.chain(parsed.sections, config.forced_separate)

    if config.no_sections:
        parsed.imports["no_sections"] = {"straight": {}, "from": {}}
        base_sections: Tuple[str, ...] = ()
        for section in sections:
            if section == "FUTURE":
                base_sections = ("FUTURE",)
                continue
            parsed.imports["no_sections"]["straight"].update(
                parsed.imports[section].get("straight", {})
            )
            parsed.imports["no_sections"]["from"].update(parsed.imports[section].get("from", {}))
        sections = base_sections + ("no_sections",)

    output: List[str] = []
    pending_lines_before = False
    for section in sections:
        straight_modules = parsed.imports[section]["straight"]
        straight_modules = sorting.naturally(
            straight_modules, key=lambda key: sorting.module_key(key, config, section_name=section)
        )
        from_modules = parsed.imports[section]["from"]
        from_modules = sorting.naturally(
            from_modules, key=lambda key: sorting.module_key(key, config, section_name=section)
        )

        if config.force_sort_within_sections:
            copied_comments = copy.deepcopy(parsed.categorized_comments)

        section_output: List[str] = []
        if config.from_first:
            section_output = _with_from_imports(
                parsed,
                config,
                from_modules,
                section,
                section_output,
                sort_ignore_case,
                remove_imports,
                import_type,
            )
            if config.lines_between_types and from_modules and straight_modules:
                section_output.extend([""] * config.lines_between_types)
            section_output = _with_straight_imports(
                parsed,
                config,
                straight_modules,
                section,
                section_output,
                remove_imports,
                import_type,
            )
        else:
            section_output = _with_straight_imports(
                parsed,
                config,
                straight_modules,
                section,
                section_output,
                remove_imports,
                import_type,
            )
            if config.lines_between_types and from_modules and straight_modules:
                section_output.extend([""] * config.lines_between_types)
            section_output = _with_from_imports(
                parsed,
                config,
                from_modules,
                section,
                section_output,
                sort_ignore_case,
                remove_imports,
                import_type,
            )

        if config.force_sort_within_sections:
            # Remove comments
            section_output = [line for line in section_output if not line.startswith("#")]

            section_output = sorting.naturally(
                section_output,
                key=partial(
                    sorting.section_key,
                    order_by_type=config.order_by_type,
                    force_to_top=config.force_to_top,
                    lexicographical=config.lexicographical,
                    length_sort=config.length_sort,
                ),
            )

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
        no_lines_before = section_name in config.no_lines_before

        if section_output:
            if section_name in parsed.place_imports:
                parsed.place_imports[section_name] = section_output
                continue

            section_title = config.import_headings.get(section_name.lower(), "")
            if section_title:
                section_comment = f"# {section_title}"
                if section_comment not in parsed.lines_without_imports[0:1]:
                    section_output.insert(0, section_comment)

            if pending_lines_before or not no_lines_before:
                output += [""] * config.lines_between_sections

            output += section_output

            pending_lines_before = False
        else:
            pending_lines_before = pending_lines_before or not no_lines_before

    while output and output[-1].strip() == "":
        output.pop()  # pragma: no cover
    while output and output[0].strip() == "":
        output.pop(0)

    output_at = 0
    if parsed.import_index < parsed.original_line_count:
        output_at = parsed.import_index
    formatted_output[output_at:0] = output

    imports_tail = output_at + len(output)
    while [
        character.strip() for character in formatted_output[imports_tail : imports_tail + 1]
    ] == [""]:
        formatted_output.pop(imports_tail)

    if len(formatted_output) > imports_tail:
        next_construct = ""
        _in_quote: str = ""
        tail = formatted_output[imports_tail:]

        for index, line in enumerate(tail):
            in_quote = _in_quote
            should_skip, _in_quote, *_ = parse.skip_line(
                line,
                in_quote=_in_quote,
                index=len(formatted_output),
                section_comments=parsed.section_comments,
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

        if config.lines_after_imports != -1:
            formatted_output[imports_tail:0] = ["" for line in range(config.lines_after_imports)]
        elif extension != "pyi" and next_construct.startswith(STATEMENT_DECLERATIONS):
            formatted_output[imports_tail:0] = ["", ""]
        else:
            formatted_output[imports_tail:0] = [""]

    if parsed.place_imports:
        new_out_lines = []
        for index, line in enumerate(formatted_output):
            new_out_lines.append(line)
            if line in parsed.import_placements:
                new_out_lines.extend(parsed.place_imports[parsed.import_placements[line]])
                if len(formatted_output) <= index or formatted_output[index + 1].strip() != "":
                    new_out_lines.append("")
        formatted_output = new_out_lines

    return _output_as_string(formatted_output, parsed.line_separator)


def _with_from_imports(
    parsed: parse.ParsedContent,
    config: Config,
    from_modules: Iterable[str],
    section: str,
    section_output: List[str],
    ignore_case: bool,
    remove_imports: List[str],
    import_type: str,
) -> List[str]:
    new_section_output = section_output.copy()
    for module in from_modules:
        if module in remove_imports:
            continue

        import_start = f"from {module} {import_type} "
        from_imports = list(parsed.imports[section]["from"][module])
        if not config.no_inline_sort or (
            config.force_single_line and module not in config.single_line_exclusions
        ):
            from_imports = sorting.naturally(
                from_imports,
                key=lambda key: sorting.module_key(
                    key, config, True, ignore_case, section_name=section
                ),
            )
        if remove_imports:
            from_imports = [
                line for line in from_imports if f"{module}.{line}" not in remove_imports
            ]

        sub_modules = [f"{module}.{from_import}" for from_import in from_imports]
        as_imports = {}
        for from_import, sub_module in zip(from_imports, sub_modules):
            if sub_module not in parsed.as_map:
                continue
            as_import = []
            for as_module in parsed.as_map[sub_module]:
                if from_import == as_module:
                    if config.keep_direct_and_as_imports:
                        parsed.imports[section]["from"][module][as_module] = True
                    else:
                        as_import.append(as_module)
                else:
                    as_import.append(f"{from_import} as {as_module}")
            as_imports[from_import] = as_import
        if config.combine_as_imports and not ("*" in from_imports and config.combine_star):
            if not config.no_inline_sort:
                for as_import in as_imports:
                    as_imports[as_import] = sorting.naturally(as_imports[as_import])
            for from_import in copy.copy(from_imports):
                if from_import in as_imports:
                    idx = from_imports.index(from_import)
                    if (
                        config.keep_direct_and_as_imports
                        and parsed.imports[section]["from"][module][from_import]
                    ):
                        from_imports[(idx + 1) : (idx + 1)] = as_imports.pop(from_import)
                    else:
                        from_imports[idx : (idx + 1)] = as_imports.pop(from_import)

        while from_imports:
            comments = parsed.categorized_comments["from"].pop(module, ())
            if "*" in from_imports and config.combine_star:
                import_statement = wrap.line(
                    with_comments(
                        comments,
                        f"{import_start}*",
                        removed=config.ignore_comments,
                        comment_prefix=config.comment_prefix,
                    ),
                    parsed.line_separator,
                    config,
                )
                from_imports = []
            elif config.force_single_line and module not in config.single_line_exclusions:
                import_statement = ""
                while from_imports:
                    from_import = from_imports.pop(0)
                    single_import_line = with_comments(
                        comments,
                        import_start + from_import,
                        removed=config.ignore_comments,
                        comment_prefix=config.comment_prefix,
                    )
                    comment = (
                        parsed.categorized_comments["nested"].get(module, {}).pop(from_import, None)
                    )
                    if comment:
                        single_import_line += (
                            f"{comments and ';' or config.comment_prefix} " f"{comment}"
                        )
                    if from_import in as_imports:
                        if (
                            config.keep_direct_and_as_imports
                            and parsed.imports[section]["from"][module][from_import]
                        ):
                            new_section_output.append(
                                wrap.line(single_import_line, parsed.line_separator, config)
                            )
                        from_comments = parsed.categorized_comments["straight"].get(
                            f"{module}.{from_import}"
                        )
                        new_section_output.extend(
                            with_comments(
                                from_comments,
                                wrap.line(import_start + as_import, parsed.line_separator, config),
                                removed=config.ignore_comments,
                                comment_prefix=config.comment_prefix,
                            )
                            for as_import in sorting.naturally(as_imports[from_import])
                        )
                    else:
                        new_section_output.append(
                            wrap.line(single_import_line, parsed.line_separator, config)
                        )
                    comments = None
            else:
                above_comments = parsed.categorized_comments["above"]["from"].pop(module, None)
                if above_comments:
                    if new_section_output and config.ensure_newline_before_comments:
                        new_section_output.append("")
                    new_section_output.extend(above_comments)

                while from_imports and from_imports[0] in as_imports:
                    from_import = from_imports.pop(0)
                    as_imports[from_import] = sorting.naturally(as_imports[from_import])
                    from_comments = parsed.categorized_comments["straight"].get(
                        f"{module}.{from_import}"
                    )
                    if (
                        config.keep_direct_and_as_imports
                        and parsed.imports[section]["from"][module][from_import]
                    ):
                        new_section_output.append(
                            with_comments(
                                from_comments,
                                wrap.line(
                                    import_start + from_import, parsed.line_separator, config
                                ),
                                removed=config.ignore_comments,
                                comment_prefix=config.comment_prefix,
                            )
                        )
                    new_section_output.extend(
                        with_comments(
                            from_comments,
                            wrap.line(import_start + as_import, parsed.line_separator, config),
                            removed=config.ignore_comments,
                            comment_prefix=config.comment_prefix,
                        )
                        for as_import in as_imports[from_import]
                    )

                star_import = False
                if "*" in from_imports:
                    new_section_output.append(
                        with_comments(
                            comments,
                            f"{import_start}*",
                            removed=config.ignore_comments,
                            comment_prefix=config.comment_prefix,
                        )
                    )
                    from_imports.remove("*")
                    star_import = True
                    comments = None

                for from_import in copy.copy(from_imports):
                    if from_import in as_imports and not config.keep_direct_and_as_imports:
                        continue
                    comment = (
                        parsed.categorized_comments["nested"].get(module, {}).pop(from_import, None)
                    )
                    if comment:
                        single_import_line = with_comments(
                            comments,
                            import_start + from_import,
                            removed=config.ignore_comments,
                            comment_prefix=config.comment_prefix,
                        )
                        single_import_line += (
                            f"{comments and ';' or config.comment_prefix} " f"{comment}"
                        )
                        new_section_output.append(
                            wrap.line(single_import_line, parsed.line_separator, config)
                        )
                        from_imports.remove(from_import)
                        comments = None

                from_import_section = []
                while from_imports and (
                    from_imports[0] not in as_imports
                    or (
                        config.keep_direct_and_as_imports
                        and config.combine_as_imports
                        and parsed.imports[section]["from"][module][from_import]
                    )
                ):
                    from_import_section.append(from_imports.pop(0))
                if star_import:
                    import_statement = import_start + (", ").join(from_import_section)
                else:
                    import_statement = with_comments(
                        comments,
                        import_start + (", ").join(from_import_section),
                        removed=config.ignore_comments,
                        comment_prefix=config.comment_prefix,
                    )
                if not from_import_section:
                    import_statement = ""

                do_multiline_reformat = False

                force_grid_wrap = config.force_grid_wrap
                if force_grid_wrap and len(from_import_section) >= force_grid_wrap:
                    do_multiline_reformat = True

                if len(import_statement) > config.line_length and len(from_import_section) > 1:
                    do_multiline_reformat = True

                # If line too long AND have imports AND we are
                # NOT using GRID or VERTICAL wrap modes
                if (
                    len(import_statement) > config.line_length
                    and len(from_import_section) > 0
                    and config.multi_line_output
                    not in (wrap.Modes.GRID, wrap.Modes.VERTICAL)  # type: ignore
                ):
                    do_multiline_reformat = True

                if do_multiline_reformat:
                    import_statement = wrap.import_statement(
                        import_start=import_start,
                        from_imports=from_import_section,
                        comments=comments,
                        line_separator=parsed.line_separator,
                        config=config,
                    )
                    if config.multi_line_output == wrap.Modes.GRID:  # type: ignore
                        other_import_statement = wrap.import_statement(
                            import_start=import_start,
                            from_imports=from_import_section,
                            comments=comments,
                            line_separator=parsed.line_separator,
                            config=config,
                            multi_line_output=wrap.Modes.VERTICAL_GRID,  # type: ignore
                        )
                        if max(len(x) for x in import_statement.split("\n")) > config.line_length:
                            import_statement = other_import_statement
                if not do_multiline_reformat and len(import_statement) > config.line_length:
                    import_statement = wrap.line(import_statement, parsed.line_separator, config)

            if import_statement:
                above_comments = parsed.categorized_comments["above"]["from"].pop(module, None)
                if above_comments:
                    if new_section_output and config.ensure_newline_before_comments:
                        new_section_output.append("")
                    new_section_output.extend(above_comments)
                new_section_output.append(import_statement)
    return new_section_output


def _with_straight_imports(
    parsed: parse.ParsedContent,
    config: Config,
    straight_modules: Iterable[str],
    section: str,
    section_output: List[str],
    remove_imports: List[str],
    import_type: str,
) -> List[str]:
    new_section_output = section_output.copy()
    for module in straight_modules:
        if module in remove_imports:
            continue

        import_definition = []
        if module in parsed.as_map:
            if config.keep_direct_and_as_imports and parsed.imports[section]["straight"][module]:
                import_definition.append(f"{import_type} {module}")
            for as_import in parsed.as_map[module]:
                if module == as_import:
                    if not config.keep_direct_and_as_imports or not (
                        as_import in parsed.imports[section]["straight"]
                        and parsed.imports[section]["straight"][as_import]
                    ):
                        import_definition.append(f"{import_type} {module}")
                else:
                    import_definition.append(f"{import_type} {module} as {as_import}")
        else:
            import_definition.append(f"{import_type} {module}")

        comments_above = parsed.categorized_comments["above"]["straight"].pop(module, None)
        if comments_above:
            if new_section_output and config.ensure_newline_before_comments:
                new_section_output.append("")
            new_section_output.extend(comments_above)
        new_section_output.extend(
            with_comments(
                parsed.categorized_comments["straight"].get(module),
                idef,
                removed=config.ignore_comments,
                comment_prefix=config.comment_prefix,
            )
            for idef in import_definition
        )

    return new_section_output


def _output_as_string(lines: List[str], line_separator: str) -> str:
    return line_separator.join(_normalize_empty_lines(lines))


def _normalize_empty_lines(lines: List[str]) -> List[str]:
    while lines and lines[-1].strip() == "":
        lines.pop(-1)

    lines.append("")
    return lines
