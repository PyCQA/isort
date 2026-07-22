import copy
import itertools
from collections.abc import Iterable
from functools import partial
from typing import Any, Literal

from isort.format import format_simplified

from . import _parse_utils, parse, sorting, wrap, wrap_modes
from .comments import add_to_line as with_comments
from .identify import STATEMENT_DECLARATIONS
from .place import module_with_reason
from .settings import DEFAULT_CONFIG, Config


# Ignore DeepSource cyclomatic complexity check for this function.
# skipcq: PY-R1000
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

    formatted_output: list[str] = parsed.lines_without_imports.copy()
    remove_imports = [format_simplified(removal) for removal in config.remove_imports]

    sections: Iterable[str] = itertools.chain(parsed.sections, config.forced_separate)

    if config.no_sections:
        parsed.imports["no_sections"] = {
            "straight": {},
            "from": {},
            "lazy_straight": {},
            "lazy_from": {},
        }
        base_sections: tuple[str, ...] = ()
        for section in sections:
            if section == "FUTURE":
                base_sections = ("FUTURE",)
                continue
            parsed.imports["no_sections"]["straight"].update(parsed.imports[section]["straight"])
            parsed.imports["no_sections"]["from"].update(parsed.imports[section]["from"])
            parsed.imports["no_sections"]["lazy_straight"].update(
                parsed.imports[section]["lazy_straight"]
            )
            parsed.imports["no_sections"]["lazy_from"].update(parsed.imports[section]["lazy_from"])
        sections = (*base_sections, "no_sections")

    output: list[str] = []
    seen_headings: set[str] = set()
    pending_lines_before = False
    for section in sections:
        section_output = _build_import_group(
            parsed, config, section, remove_imports, import_type, is_lazy=False
        )

        # PEP 810 lazy imports always follow all eager imports within the section.
        lazy_section_output = _build_import_group(
            parsed, config, section, remove_imports, import_type, is_lazy=True
        )

        if lazy_section_output:
            if section_output:
                section_output += [""] * config.lines_between_types + lazy_section_output
            else:
                section_output = lazy_section_output

        section_name = section
        no_lines_before = section_name in config.no_lines_before

        if section_output:
            if section_name in parsed.place_imports:
                parsed.place_imports[section_name] = section_output
                continue

            section_title = config.import_headings.get(section_name.lower(), "")
            if section_title and section_title not in seen_headings:
                if config.dedup_headings:
                    seen_headings.add(section_title)
                section_comment = f"# {section_title}"
                if section_comment not in parsed.lines_without_imports[0:1]:  # pragma: no branch
                    section_output.insert(0, section_comment)

            section_footer = config.import_footers.get(section_name.lower(), "")
            if section_footer and section_footer not in seen_headings:
                if config.dedup_headings:
                    seen_headings.add(section_footer)
                section_comment_end = f"# {section_footer}"
                if (
                    section_comment_end not in parsed.lines_without_imports[-1:]
                ):  # pragma: no branch
                    section_output.append("")  # Empty line for black compatibility
                    section_output.append(section_comment_end)

            if section in config.separate_packages:
                section_output = _separate_packages(section_output, config)

            if pending_lines_before or not no_lines_before:
                output += [""] * config.lines_between_sections

            output += section_output

            pending_lines_before = False
        else:
            pending_lines_before = pending_lines_before or not no_lines_before

    if config.ensure_newline_before_comments:
        output = _ensure_newline_before_comment(output)

    while output and output[-1].strip() == "":
        output.pop()  # pragma: no cover
    while output and output[0].strip() == "":
        output.pop(0)

    if config.formatting_function:
        output = config.formatting_function(
            parsed.line_separator.join(output), extension, config
        ).splitlines()

    output_at = 0
    if parsed.import_index < parsed.original_line_count:
        output_at = parsed.import_index
    formatted_output[output_at:0] = output

    if output:
        imports_tail = output_at + len(output)
        while [
            character.strip() for character in formatted_output[imports_tail : imports_tail + 1]
        ] == [""]:
            formatted_output.pop(imports_tail)

        if config.lines_before_imports != -1:
            lines_before_imports = config.lines_before_imports
            if config.profile == "black" and extension == "pyi":  # special case for black
                lines_before_imports = 1
            formatted_output[:0] = ["" for line in range(lines_before_imports)]
            imports_tail += lines_before_imports

        if len(formatted_output) > imports_tail:
            next_construct = ""
            tail = formatted_output[imports_tail:]

            for index, line in enumerate(tail):  # pragma: no branch
                should_skip, in_quote = _parse_utils.skip_line(
                    line, in_quote="", needs_import=False
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
                if in_quote:  # pragma: no branch
                    next_construct = line
                    break

            if config.lines_after_imports != -1:
                lines_after_imports = config.lines_after_imports
                if config.profile == "black" and extension == "pyi":  # special case for black
                    lines_after_imports = 1
                formatted_output[imports_tail:0] = ["" for line in range(lines_after_imports)]
            elif extension != "pyi" and next_construct.startswith(STATEMENT_DECLARATIONS):
                formatted_output[imports_tail:0] = ["", ""]
            else:
                formatted_output[imports_tail:0] = [""]

    if parsed.place_imports:
        new_out_lines = []
        for index, line in enumerate(formatted_output):
            new_out_lines.append(line)
            if line in parsed.import_placements:
                new_out_lines.extend(parsed.place_imports[parsed.import_placements[line]])
                if (
                    len(formatted_output) <= (index + 1)
                    or formatted_output[index + 1].strip() != ""
                ):
                    new_out_lines.append("")
        formatted_output = new_out_lines

    return _output_as_string(formatted_output, parsed.line_separator)


# Ignore DeepSource cyclomatic complexity check for this function.
# skipcq: PY-R1000
def _build_import_group(
    parsed: parse.ParsedContent,
    config: Config,
    section: str,
    remove_imports: list[str],
    import_type: str,
    *,
    is_lazy: bool,
) -> list[str]:
    """Build the sorted import lines for one group (eager or lazy) within a section."""
    straight_key: Literal["lazy_straight", "straight"] = "lazy_straight" if is_lazy else "straight"
    from_key: Literal["lazy_from", "from"] = "lazy_from" if is_lazy else "from"

    straight_modules: Iterable[str] = parsed.imports[section][straight_key]
    if not config.only_sections:
        straight_modules = sorting.sort(
            config,
            straight_modules,
            key=lambda key: sorting.module_key(
                key, config, section_name=section, straight_import=True
            ),
            reverse=config.reverse_sort,
        )

    from_modules: Iterable[str] = parsed.imports[section][from_key]
    if not config.only_sections:
        from_modules = sorting.sort(
            config,
            from_modules,
            key=lambda key: sorting.module_key(key, config, section_name=section),
            reverse=config.reverse_sort,
        )

        if not is_lazy and config.star_first:
            star_modules = []
            other_modules = []
            for module in from_modules:
                if "*" in parsed.imports[section]["from"][module]:
                    star_modules.append(module)
                else:
                    other_modules.append(module)
            from_modules = star_modules + other_modules

    straight_imports = _with_straight_imports(
        parsed, config, straight_modules, section, remove_imports, import_type, is_lazy=is_lazy
    )
    from_imports = _with_from_imports(
        parsed, config, from_modules, section, remove_imports, import_type, is_lazy=is_lazy
    )

    lines_between = [""] * (config.lines_between_types if from_modules and straight_modules else 0)
    if config.from_first or section == "FUTURE":
        group_output = from_imports + lines_between + straight_imports
    else:
        group_output = straight_imports + lines_between + from_imports

    # #2455: merge plain from-import statements for the same module after emit.
    # Keeps mid-path logic simple (no defer_as bookkeeping).
    group_output = _merge_plain_from_imports(group_output, config)

    if config.force_sort_within_sections:
        # collapse comments
        comments_above: list[str] = []
        new_group_output: list[str] = []
        for line in group_output:
            if not line:
                continue
            if line.startswith("#"):
                comments_above.append(line)
            elif comments_above:
                new_group_output.append(_LineWithComments(line, comments_above))
                comments_above = []
            else:
                new_group_output.append(line)
        # only_sections option is not imposed if force_sort_within_sections is True
        new_group_output = sorting.sort(
            config,
            new_group_output,
            key=partial(sorting.section_key, config=config),
            reverse=config.reverse_sort,
        )
        # uncollapse comments
        group_output = []
        for line in new_group_output:
            line_comments = getattr(line, "comments", ())
            if line_comments:
                group_output.extend(line_comments)
            group_output.append(str(line))

    return group_output


# Ignore DeepSource cyclomatic complexity check for this function. It was
# already complex when this check was enabled.
# skipcq: PY-R1000
def _with_from_imports(
    parsed: parse.ParsedContent,
    config: Config,
    from_modules: Iterable[str],
    section: str,
    remove_imports: list[str],
    import_type: str,
    *,
    is_lazy: bool,
) -> list[str]:
    output: list[str] = []
    import_key: Literal["lazy_from", "from"] = "lazy_from" if is_lazy else "from"

    for module in from_modules:
        if module in remove_imports:
            continue

        import_start = f"from {module} {import_type} "
        if is_lazy:
            import_start = f"lazy {import_start}"
        from_imports = list(parsed.imports[section][import_key][module])

        if (
            not config.no_inline_sort
            or (config.force_single_line and module not in config.single_line_exclusions)
        ) and not config.only_sections:
            from_imports = sorting.sort(
                config,
                from_imports,
                key=lambda key: sorting.module_key(
                    key,
                    config,
                    True,
                    config.force_alphabetical_sort_within_sections,
                    section_name=section,
                ),
                reverse=config.reverse_sort,
            )
        if remove_imports:
            from_imports = [
                line for line in from_imports if f"{module}.{line}" not in remove_imports
            ]

        sub_modules = [f"{module}.{from_import}" for from_import in from_imports]
        as_imports = {
            from_import: [
                f"{from_import} as {as_module}" for as_module in parsed.as_map["from"][sub_module]
            ]
            for from_import, sub_module in zip(from_imports, sub_modules, strict=False)
            if sub_module in parsed.as_map["from"]
        }
        if config.combine_as_imports and not ("*" in from_imports and config.combine_star):
            if not config.no_inline_sort:
                for as_import in as_imports:
                    if not config.only_sections:
                        as_imports[as_import] = sorting.sort(config, as_imports[as_import])
            for from_import in copy.copy(from_imports):
                if from_import in as_imports:
                    idx = from_imports.index(from_import)
                    if parsed.imports[section][import_key][module][from_import]:
                        from_imports[(idx + 1) : (idx + 1)] = as_imports.pop(from_import)
                    else:
                        from_imports[idx : (idx + 1)] = as_imports.pop(from_import)

        only_show_as_imports = False
        comments: list[str] | None = parsed.categorized_comments["from"].pop(module, None)
        above_comments = parsed.categorized_comments["above"]["from"].pop(module, None)
        while from_imports:
            if above_comments:
                output.extend(above_comments)
                above_comments = None

            if "*" in from_imports and config.combine_star:
                import_statement = wrap.line(
                    with_comments(
                        _with_star_comments(parsed, module, list(comments or ())),
                        f"{import_start}*",
                        removed=config.ignore_comments,
                        comment_prefix=config.comment_prefix,
                    ),
                    parsed.line_separator,
                    config,
                )
                from_imports = [
                    from_import for from_import in from_imports if from_import in as_imports
                ]
                only_show_as_imports = True
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
                    if comment is not None:
                        comment_text = f" {comment}" if comment else ""
                        single_import_line += (
                            f"{(comments and ';') or config.comment_prefix}{comment_text}"
                        )
                    if from_import in as_imports:
                        if (
                            parsed.imports[section][import_key][module][from_import]
                            and not only_show_as_imports
                        ):
                            output.append(
                                wrap.line(single_import_line, parsed.line_separator, config)
                            )
                        from_comments = parsed.categorized_comments["straight"].get(
                            f"{module}.{from_import}"
                        )

                        if not config.only_sections:
                            output.extend(
                                wrap.line(
                                    with_comments(
                                        from_comments,
                                        import_start + as_import,
                                        removed=config.ignore_comments,
                                        comment_prefix=config.comment_prefix,
                                    ),
                                    parsed.line_separator,
                                    config,
                                )
                                for as_import in sorting.sort(config, as_imports[from_import])
                            )

                        else:
                            output.extend(
                                wrap.line(
                                    with_comments(
                                        from_comments,
                                        import_start + as_import,
                                        removed=config.ignore_comments,
                                        comment_prefix=config.comment_prefix,
                                    ),
                                    parsed.line_separator,
                                    config,
                                )
                                for as_import in as_imports[from_import]
                            )
                    else:
                        output.append(wrap.line(single_import_line, parsed.line_separator, config))
                    comments = None
            else:
                # Tracks whether any aliased imports were emitted before the grouped
                # non-aliased imports in this pass of the outer loop.  When True it
                # suppresses the split_on_trailing_comma explode behaviour for the
                # non-aliased group, because those imports are not the sole content
                # of the statement and forcing them onto individual lines would break
                # the intended output structure.
                processed_as_imports_this_iteration = False
                while from_imports and from_imports[0] in as_imports:
                    processed_as_imports_this_iteration = True
                    from_import = from_imports.pop(0)

                    if not config.only_sections:
                        as_imports[from_import] = sorting.sort(config, as_imports[from_import])
                    from_comments = (
                        parsed.categorized_comments["straight"].get(f"{module}.{from_import}") or []
                    )
                    if (
                        parsed.imports[section][import_key][module][from_import]
                        and not only_show_as_imports
                    ):
                        specific_comment = (
                            parsed.categorized_comments["nested"]
                            .get(module, {})
                            .pop(from_import, None)
                        )
                        if specific_comment is not None:
                            from_comments.append(specific_comment)
                        output.append(
                            wrap.line(
                                with_comments(
                                    from_comments,
                                    import_start + from_import,
                                    removed=config.ignore_comments,
                                    comment_prefix=config.comment_prefix,
                                ),
                                parsed.line_separator,
                                config,
                            )
                        )
                        from_comments = []

                    for as_import in as_imports[from_import]:
                        # `from_comments` at this point contains any comments that appeared on
                        # the *opening* "from X import" line. These are distinct from
                        # `specific_comment`, which is an inline comment on the attribute line
                        # itself. We snapshot `from_comments` here so that we can later distinguish
                        # the two types: opening-line comments must stay on the "import (" line
                        # when parentheses are used, while attribute-line comments stay on the
                        # import attribute line.
                        opening_line_comments = list(from_comments)
                        specific_comment = (
                            parsed.categorized_comments["nested"]
                            .get(module, {})
                            .pop(as_import, None)
                        )
                        # Collect the attribute-line comment (if any) separately so it can be
                        # embedded in the attribute line regardless of wrapping mode.
                        if specific_comment is not None:
                            from_comments.append(specific_comment)

                        import_line = import_start + as_import
                        if opening_line_comments and config.use_parentheses:
                            # When parentheses are used, opening-line comments (e.g. "# noqa") must
                            # remain on the "from X import (" line. If we naively embedded them in
                            # the attribute string and then called wrap.line(), the comment would
                            # end up inside the parentheses on the alias attribute line.
                            # Wrap the import with only the attribute-line comment. Afterwards, add
                            # the opening-line comment back to the first line of the wrapped import
                            # statement.
                            lines = wrap.line(
                                with_comments(
                                    [specific_comment] if specific_comment else [],
                                    import_line,
                                    removed=config.ignore_comments,
                                    comment_prefix=config.comment_prefix,
                                ),
                                parsed.line_separator,
                                config,
                            ).split(parsed.line_separator)

                            opening_comment = with_comments(
                                opening_line_comments,
                                "",
                                removed=config.ignore_comments,
                                comment_prefix=config.comment_prefix,
                            )
                            if opening_comment:
                                lines[0] += opening_comment
                                if config.multi_line_output == wrap_modes.WrapModes.NOQA:
                                    lines[0] = wrap.line(lines[0], parsed.line_separator, config)
                            output.append(parsed.line_separator.join(lines))
                        else:
                            output.append(
                                wrap.line(
                                    with_comments(
                                        from_comments,
                                        import_line,
                                        removed=config.ignore_comments,
                                        comment_prefix=config.comment_prefix,
                                    ),
                                    parsed.line_separator,
                                    config,
                                )
                            )

                        from_comments = []

                if "*" in from_imports:
                    output.append(
                        with_comments(
                            _with_star_comments(parsed, module, []),
                            f"{import_start}*",
                            removed=config.ignore_comments,
                            comment_prefix=config.comment_prefix,
                        )
                    )
                    from_imports.remove("*")

                for from_import in copy.copy(from_imports):
                    comment = (
                        parsed.categorized_comments["nested"].get(module, {}).pop(from_import, None)
                    )
                    if comment is not None:
                        # If the comment is a noqa and hanging indent wrapping is used,
                        # keep the name in the main list and hoist the comment to the statement.
                        if (
                            comment.lower().startswith("noqa")
                            and config.multi_line_output == wrap_modes.WrapModes.HANGING_INDENT
                        ):
                            comments = list(comments) if comments else []
                            comments.append(comment)
                            continue

                        from_imports.remove(from_import)
                        if from_imports:
                            use_comments: list[str] | None = []
                        else:
                            use_comments = comments
                            comments = None
                        single_import_line = with_comments(
                            use_comments,
                            import_start + from_import,
                            removed=config.ignore_comments,
                            comment_prefix=config.comment_prefix,
                        )
                        comment_text = f" {comment}" if comment else ""
                        single_import_line += (
                            f"{(use_comments and ';') or config.comment_prefix}{comment_text}"
                        )
                        output.append(wrap.line(single_import_line, parsed.line_separator, config))

                from_import_section = []
                while from_imports and (
                    from_imports[0] not in as_imports
                    or (
                        config.combine_as_imports
                        and parsed.imports[section][import_key][module][from_import]
                    )
                ):
                    from_import_section.append(from_imports.pop(0))
                if config.combine_as_imports:
                    comments = (comments or []) + list(
                        parsed.categorized_comments["from"].pop(f"{module}.__combined_as__", ())
                    )
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
                    not in (wrap_modes.WrapModes.GRID, wrap_modes.WrapModes.VERTICAL)
                ):
                    do_multiline_reformat = True

                # When ``include_trailing_comma`` is enabled isort always appends a
                # trailing comma to multi-line imports.  Combined with
                # ``split_on_trailing_comma`` that means any import wrapped across
                # multiple lines would gain a trailing comma and therefore be exploded
                # onto individual lines on the *next* run.  Treat such imports as if they
                # already carried a trailing comma so the explode happens on the first
                # pass too, keeping the output idempotent regardless of the requested
                # ``multi_line_output`` mode.
                explode_on_trailing_comma = config.split_on_trailing_comma and (
                    module in parsed.trailing_commas
                    or (config.include_trailing_comma and do_multiline_reformat)
                )

                if (
                    import_statement
                    and explode_on_trailing_comma
                    and not processed_as_imports_this_iteration
                ):
                    import_statement = wrap.import_statement(
                        import_start=import_start,
                        from_imports=from_import_section,
                        comments=comments,
                        line_separator=parsed.line_separator,
                        config=config,
                        explode=True,
                    )

                elif do_multiline_reformat:
                    import_statement = wrap.import_statement(
                        import_start=import_start,
                        from_imports=from_import_section,
                        comments=comments,
                        line_separator=parsed.line_separator,
                        config=config,
                    )
                    if config.multi_line_output == wrap_modes.WrapModes.GRID:
                        other_import_statement = wrap.import_statement(
                            import_start=import_start,
                            from_imports=from_import_section,
                            comments=comments,
                            line_separator=parsed.line_separator,
                            config=config,
                            multi_line_output=wrap_modes.WrapModes.VERTICAL_GRID,
                        )
                        if (
                            max(
                                len(import_line)
                                for import_line in import_statement.split(parsed.line_separator)
                            )
                            > config.line_length
                        ):
                            import_statement = other_import_statement
                elif len(import_statement) > config.line_length:
                    import_statement = wrap.line(import_statement, parsed.line_separator, config)
                comments = None

            if import_statement:
                output.append(import_statement)
    return output


# Ignore DeepSource cyclomatic complexity check for this function.
# skipcq: PY-R1000
def _with_straight_imports(
    parsed: parse.ParsedContent,
    config: Config,
    straight_modules: Iterable[str],
    section: str,
    remove_imports: list[str],
    import_type: str,
    *,
    is_lazy: bool,
) -> list[str]:
    output: list[str] = []

    import_type = f"lazy {import_type}" if is_lazy else import_type

    as_imports = any(module in parsed.as_map["straight"] for module in straight_modules)

    # combine_straight_imports only works for bare imports, 'as' imports not included
    if config.combine_straight_imports and not as_imports:
        if not straight_modules:
            return []

        above_comments: list[str] = []
        inline_comments: list[str] = []

        for module in straight_modules:
            if module in parsed.categorized_comments["above"]["straight"]:
                above_comments.extend(parsed.categorized_comments["above"]["straight"].pop(module))
            if module in parsed.categorized_comments["straight"]:
                inline_comments.extend(parsed.categorized_comments["straight"][module])

        combined_straight_imports = ", ".join(straight_modules)

        output.extend(above_comments)

        if inline_comments:
            combined_inline_comments = " ".join(c for c in inline_comments if c)
            if combined_inline_comments:
                line_content = (
                    f"{import_type} {combined_straight_imports}  # {combined_inline_comments}"
                )
            else:
                line_content = f"{import_type} {combined_straight_imports}  #"
        else:
            line_content = f"{import_type} {combined_straight_imports}"

        output.append(wrap.line(line_content, parsed.line_separator, config))

        return output

    for module in straight_modules:
        if module in remove_imports:
            continue

        import_definition = []
        if module in parsed.as_map["straight"]:
            if parsed.imports[section]["lazy_straight" if is_lazy else "straight"][module]:
                import_definition.append((f"{import_type} {module}", module))
            import_definition.extend(
                (f"{import_type} {module} as {as_import}", f"{module} as {as_import}")
                for as_import in parsed.as_map["straight"][module]
            )
        else:
            import_definition.append((f"{import_type} {module}", module))

        comments_above = parsed.categorized_comments["above"]["straight"].pop(module, None)
        if comments_above:
            output.extend(comments_above)
        for idef, imodule in import_definition:
            line_content = with_comments(
                parsed.categorized_comments["straight"].get(imodule),
                idef,
                removed=config.ignore_comments,
                comment_prefix=config.comment_prefix,
            )
            if config.multi_line_output == wrap_modes.WrapModes.NOQA:
                line_content = wrap.line(line_content, parsed.line_separator, config)
            output.append(line_content)

    return output


def _output_as_string(lines: list[str], line_separator: str) -> str:
    return line_separator.join(_normalize_empty_lines(lines))


def _normalize_empty_lines(lines: list[str]) -> list[str]:
    while lines and lines[-1].strip() == "":
        lines.pop(-1)

    lines.append("")
    return lines


class _LineWithComments(str):
    comments: list[str]

    def __new__(
        cls: type["_LineWithComments"], value: Any, comments: list[str]
    ) -> "_LineWithComments":
        instance = super().__new__(cls, value)
        instance.comments = comments
        return instance


def _ensure_newline_before_comment(output: list[str]) -> list[str]:
    new_output: list[str] = []

    def is_comment(line: str | None) -> bool:
        return line.startswith("#") if line else False

    for line, prev_line in zip(output, [None, *output], strict=False):
        if is_comment(line) and prev_line != "" and not is_comment(prev_line):
            new_output.append("")
        new_output.append(line)
    return new_output


def _with_star_comments(parsed: parse.ParsedContent, module: str, comments: list[str]) -> list[str]:
    star_comment = parsed.categorized_comments["nested"].get(module, {}).pop("*", None)
    if star_comment:
        return [*comments, star_comment]
    return comments


def _merge_plain_from_imports(group_output: list[str], config: Config) -> list[str]:
    """Post-emit preferred #2455 plain grouping (merge-at-end).

    After mid-path emit, for each module:
    - merge multiple comment-free plain from-import statements into one
    - if comment-free plains and comment-free aliases are mixed, put the plain
      group before the aliases

    Skips force_single_line / no_inline_sort / combine_as_imports so those paths
    keep established behaviour. Comment-bearing statements are never rewritten.
    """
    if (
        not group_output
        or config.force_single_line
        or config.no_inline_sort
        or config.combine_as_imports
    ):
        return group_output

    def _parse_from(line: str) -> dict | None:
        s = str(line)
        stripped = s.strip()
        if stripped.startswith("#"):
            return None
        lazy = False
        work = stripped
        if work.startswith("lazy "):
            lazy = True
            work = work[5:].lstrip()
        if not work.startswith("from ") or " import " not in work:
            return None
        module_part, names_part = work[5:].split(" import ", 1)
        module = module_part.strip()
        has_comment = "#" in stripped
        code_names = names_part.split("#", 1)[0]
        if "*" in code_names and code_names.strip().lstrip("(").startswith("*"):
            return None
        raw = code_names.replace("(", " ").replace(")", " ").replace("\n", " ")
        names: list[str] = []
        for part in raw.split(","):
            n = part.strip().rstrip(",")
            if n:
                names.append(n)
        if not names:
            return None
        kinds = [(" as " in n) for n in names]
        if any(kinds) and not all(kinds):
            return None
        kind = "alias" if any(kinds) else "plain"
        indent = s[: len(s) - len(s.lstrip())]
        return {
            "module": module,
            "kind": kind,
            "names": names,
            "has_comment": has_comment,
            "lazy": lazy,
            "indent": indent,
            "had_paren": "(" in names_part,
            "original": s,
        }

    from collections import OrderedDict

    by_module: OrderedDict[str, list[tuple[int, dict]]] = OrderedDict()
    for idx, line in enumerate(group_output):
        info = _parse_from(str(line))
        if info is None:
            continue
        by_module.setdefault(info["module"], []).append((idx, info))

    drop: set[int] = set()
    replacements: dict[int, list[str]] = {}

    for module, entries in by_module.items():
        free_plains = [
            (i, inf)
            for i, inf in entries
            if inf["kind"] == "plain" and not inf["has_comment"]
        ]
        free_aliases = [
            (i, inf)
            for i, inf in entries
            if inf["kind"] == "alias" and not inf["has_comment"]
        ]
        has_commented = any(inf["has_comment"] for _, inf in entries)
        if not free_plains:
            continue

        needs_merge = len(free_plains) > 1
        # Reorder only when the module has no comment-bearing statements, so we
        # do not disturb comment-local identity cases (e.g. issue #2282).
        needs_order = False
        if free_aliases and not has_commented:
            plain_idxs = [i for i, _ in free_plains]
            alias_idxs = [i for i, _ in free_aliases]
            if any(a < min(plain_idxs) for a in alias_idxs):
                needs_order = True
            elif min(plain_idxs) < max(alias_idxs) and max(plain_idxs) > min(alias_idxs):
                needs_order = True
        if not needs_merge and not needs_order:
            continue

        all_names: list[str] = []
        seen: set[str] = set()
        for _, inf in free_plains:
            for n in inf["names"]:
                if n not in seen:
                    seen.add(n)
                    all_names.append(n)
        if not config.only_sections:
            all_names = sorting.sort(
                config,
                all_names,
                key=lambda key: sorting.module_key(
                    key,
                    config,
                    True,
                    config.force_alphabetical_sort_within_sections,
                    section_name="",
                ),
                reverse=config.reverse_sort,
            )

        sample = free_plains[0][1]
        indent = sample["indent"]
        if sample["lazy"]:
            prefix = f"{indent}lazy from {module} import "
        else:
            prefix = f"{indent}from {module} import "
        use_paren = any(inf["had_paren"] for _, inf in free_plains) or (
            len(prefix) + len(", ".join(all_names)) > config.line_length
        )
        if use_paren and len(all_names) > 1:
            body = ",\n    ".join(all_names)
            plain_stmt = f"{prefix}(\n    {body},\n)"
        else:
            plain_stmt = prefix + ", ".join(all_names)

        if needs_order:
            # Rewrite free plains + free aliases as plain-then-aliases at first free idx.
            rewrite_idxs = [i for i, _ in free_plains] + [i for i, _ in free_aliases]
            first_idx = min(rewrite_idxs)
            new_lines = [plain_stmt]
            for _, inf in sorted(free_aliases, key=lambda x: x[0]):
                new_lines.append(inf["original"])
            for idx in rewrite_idxs:
                if idx != first_idx:
                    drop.add(idx)
            replacements[first_idx] = new_lines
        else:
            # Merge plains only; leave aliases where they are.
            first_idx = free_plains[0][0]
            replacements[first_idx] = [plain_stmt]
            for idx, _ in free_plains[1:]:
                drop.add(idx)

    if not drop and not replacements:
        return group_output

    out: list[str] = []
    for i, line in enumerate(group_output):
        if i in drop:
            continue
        if i in replacements:
            out.extend(replacements[i])
        else:
            out.append(line)
    return out



def _separate_packages(section_output: list[str], config: Config) -> list[str]:
    group_keys: set[str] = set()
    comments_above: list[str] = []
    processed_section_output: list[str] = []

    for section_line in section_output:
        if section_line.startswith("#"):
            comments_above.append(section_line)
            continue

        package_name: str = section_line.split(" ")[1]
        _, reason = module_with_reason(package_name, config)

        if "Matched configured known pattern" in reason:
            package_depth = len(reason.split(".")) - 1  # minus 1 for re.compile
            key = ".".join(package_name.split(".")[: package_depth + 1])
        else:
            key = package_name.split(".")[0]

        if key not in group_keys:
            if group_keys:
                processed_section_output.append("")

            group_keys.add(key)

        if comments_above:
            processed_section_output.extend(comments_above)
            comments_above = []

        processed_section_output.append(section_line)

    return processed_section_output
