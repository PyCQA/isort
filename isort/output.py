import copy
import itertools
from collections.abc import Iterable
from functools import partial
from typing import Any, Literal

from isort.format import format_simplified

from . import _parse_utils, parse, sorting, wrap
from .comments import add_to_line as with_comments
from .identify import STATEMENT_DECLARATIONS
from .place import module_with_reason
from .settings import DEFAULT_CONFIG, Config


def sorted_imports(
    parsed: parse.ParsedContent,
    config: Config = DEFAULT_CONFIG,
    extension: str = "py",
    import_type: str = "import",
) -> str:
    if parsed.import_index == -1:
        return _output_as_string(parsed.lines_without_imports, parsed.line_separator)

    formatted_output: list[str] = parsed.lines_without_imports.copy()
    remove_imports = {format_simplified(r) for r in config.remove_imports}

    sections: Iterable[str] = itertools.chain(parsed.sections, config.forced_separate)

    if config.no_sections:
        parsed.imports["no_sections"] = {
            "straight": {},
            "from": {},
            "lazy_straight": {},
            "lazy_from": {},
        }
        base_sections: tuple[str, ...] = ()
        for sec in sections:
            if sec == "FUTURE":
                base_sections = ("FUTURE",)
                continue
            parsed.imports["no_sections"]["straight"].update(parsed.imports[sec]["straight"])
            parsed.imports["no_sections"]["from"].update(parsed.imports[sec]["from"])
            parsed.imports["no_sections"]["lazy_straight"].update(
                parsed.imports[sec]["lazy_straight"]
            )
            parsed.imports["no_sections"]["lazy_from"].update(parsed.imports[sec]["lazy_from"])
        sections = (*base_sections, "no_sections")

    output: list[str] = []
    seen_headings: set[str] = set()
    pending_lines_before = False
    cfg = config
    for section in sections:
        sec_out = _build_import_group(
            parsed, cfg, section, list(remove_imports), import_type, is_lazy=False
        )
        lazy_sec_out = _build_import_group(
            parsed, cfg, section, list(remove_imports), import_type, is_lazy=True
        )
        if lazy_sec_out:
            sec_out = sec_out + [""] * cfg.lines_between_types + lazy_sec_out if sec_out else lazy_sec_out

        no_lines_before = section in cfg.no_lines_before
        if sec_out:
            if section in parsed.place_imports:
                parsed.place_imports[section] = sec_out
                continue

            title = cfg.import_headings.get(section.lower(), "")
            if title and title not in seen_headings:
                if cfg.dedup_headings:
                    seen_headings.add(title)
                comment = f"# {title}"
                if comment not in parsed.lines_without_imports[:1]:
                    sec_out.insert(0, comment)

            footer = cfg.import_footers.get(section.lower(), "")
            if footer and footer not in seen_headings:
                if cfg.dedup_headings:
                    seen_headings.add(footer)
                foot_comment = f"# {footer}"
                if foot_comment not in parsed.lines_without_imports[-1:]:
                    sec_out.append("")
                    sec_out.append(foot_comment)

            if section in cfg.separate_packages:
                sec_out = _separate_packages(sec_out, cfg)

            if pending_lines_before or not no_lines_before:
                output += [""] * cfg.lines_between_sections
            output += sec_out
            pending_lines_before = False
        else:
            pending_lines_before = pending_lines_before or not no_lines_before

    if cfg.ensure_newline_before_comments:
        output = _ensure_newline_before_comment(output)

    while output and output[-1].strip() == "":
        output.pop()
    while output and output[0].strip() == "":
        output.pop(0)

    if cfg.formatting_function:
        output = cfg.formatting_function(
            parsed.line_separator.join(output), extension, cfg
        ).splitlines()

    output_at = parsed.import_index if parsed.import_index < parsed.original_line_count else 0
    formatted_output[output_at:output_at] = output

    if output:
        imports_tail = output_at + len(output)
        while imports_tail < len(formatted_output) and formatted_output[imports_tail].strip() == "":
            formatted_output.pop(imports_tail)

        if cfg.lines_before_imports != -1:
            lines_before = cfg.lines_before_imports
            if cfg.profile == "black" and extension == "pyi":
                lines_before = 1
            formatted_output[:0] = ["" for _ in range(lines_before)]
            imports_tail += lines_before

        if len(formatted_output) > imports_tail:
            next_construct = ""
            tail = formatted_output[imports_tail:]
            for idx, line in enumerate(tail):
                should_skip, in_quote = _parse_utils.skip_line(
                    line, in_quote="", needs_import=False
                )
                if not should_skip and line.strip():
                    if line.strip().startswith("#") and idx + 1 < len(tail) and tail[idx + 1].strip():
                        continue
                    next_construct = line
                    break
                if in_quote:
                    next_construct = line
                    break

            if cfg.lines_after_imports != -1:
                lines_after = cfg.lines_after_imports
                if cfg.profile == "black" and extension == "pyi":
                    lines_after = 1
                formatted_output[imports_tail:imports_tail] = ["" for _ in range(lines_after)]
            elif extension != "pyi" and next_construct.startswith(STATEMENT_DECLARATIONS):
                formatted_output[imports_tail:imports_tail] = ["", ""]
            else:
                formatted_output[imports_tail:imports_tail] = [""]

    if parsed.place_imports:
        new_out = []
        for idx, line in enumerate(formatted_output):
            new_out.append(line)
            if line in parsed.import_placements:
                new_out.extend(parsed.place_imports[parsed.import_placements[line]])
                if idx + 1 >= len(formatted_output) or formatted_output[idx + 1].strip() != "":
                    new_out.append("")
        formatted_output = new_out

    return _output_as_string(formatted_output, parsed.line_separator)


def _build_import_group(
    parsed: parse.ParsedContent,
    config: Config,
    section: str,
    remove_imports: list[str],
    import_type: str,
    *,
    is_lazy: bool,
) -> list[str]:
    straight_key = "lazy_straight" if is_lazy else "straight"
    from_key = "lazy_from" if is_lazy else "from"

    straight_modules = parsed.imports[section][straight_key]
    if not config.only_sections:
        straight_modules = sorting.sort(
            config,
            straight_modules,
            key=lambda k: sorting.module_key(k, config, section_name=section, straight_import=True),
            reverse=config.reverse_sort,
        )

    from_modules = parsed.imports[section][from_key]
    if not config.only_sections:
        from_modules = sorting.sort(
            config,
            from_modules,
            key=lambda k: sorting.module_key(k, config, section_name=section),
            reverse=config.reverse_sort,
        )
        if not is_lazy and config.star_first:
            stars, others = [], []
            for mod in from_modules:
                (stars if "*" in parsed.imports[section]["from"][mod] else others).append(mod)
            from_modules = stars + others

    straight_imports = _with_straight_imports(
        parsed, config, straight_modules, section, remove_imports, import_type, is_lazy=is_lazy
    )
    from_imports = _with_from_imports(
        parsed, config, from_modules, section, remove_imports, import_type, is_lazy=is_lazy
    )

    lines_between = [""] * (config.lines_between_types if from_modules and straight_modules else 0)
    group_output = (
        from_imports + lines_between + straight_imports
        if config.from_first or section == "FUTURE"
        else straight_imports + lines_between + from_imports
    )

    if config.force_sort_within_sections:
        comments_buf: list[str] = []
        sortable: list[Any] = []
        for line in group_output:
            if not line:
                continue
            if line.startswith("#"):
                comments_buf.append(line)
            elif comments_buf:
                sortable.append(_LineWithComments(line, comments_buf))
                comments_buf = []
            else:
                sortable.append(line)
        sortable = sorting.sort(
            config,
            sortable,
            key=partial(sorting.section_key, config=config),
            reverse=config.reverse_sort,
        )
        group_output = []
        for item in sortable:
            if isinstance(item, _LineWithComments):
                group_output.extend(item.comments)
                group_output.append(str(item))
            else:
                group_output.append(item)

    return group_output


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
    import_key = "lazy_from" if is_lazy else "from"
    cfg = config
    rem_set = set(remove_imports)

    for module in from_modules:
        if module in rem_set:
            continue

        import_start = f"from {module} {import_type} "
        if is_lazy:
            import_start = f"lazy {import_start}"
        from_imports = list(parsed.imports[section][import_key][module])

        if (not cfg.no_inline_sort or (cfg.force_single_line and module not in cfg.single_line_exclusions)) and not cfg.only_sections:
            from_imports = sorting.sort(
                cfg,
                from_imports,
                key=lambda k: sorting.module_key(
                    k,
                    cfg,
                    True,
                    cfg.force_alphabetical_sort_within_sections,
                    section_name=section,
                ),
                reverse=cfg.reverse_sort,
            )
        if rem_set:
            from_imports = [ln for ln in from_imports if f"{module}.{ln}" not in rem_set]

        sub_modules = [f"{module}.{fi}" for fi in from_imports]
        as_imports = {
            fi: [f"{fi} as {as_mod}" for as_mod in parsed.as_map["from"][sub]]
            for fi, sub in zip(from_imports, sub_modules, strict=False)
            if sub in parsed.as_map["from"]
        }

        if cfg.combine_as_imports and not ("*" in from_imports and cfg.combine_star):
            if not cfg.no_inline_sort:
                for key in as_imports:
                    if not cfg.only_sections:
                        as_imports[key] = sorting.sort(cfg, as_imports[key])
            for fi in list(from_imports):
                if fi in as_imports:
                    idx = from_imports.index(fi)
                    if parsed.imports[section][import_key][module][fi]:
                        from_imports[idx + 1 : idx + 1] = as_imports.pop(fi)
                    else:
                        from_imports[idx : idx + 1] = as_imports.pop(fi)

        only_show_as = False
        comments = parsed.categorized_comments["from"].pop(module, None)
        above_comments = parsed.categorized_comments["above"]["from"].pop(module, None)

        while from_imports:
            if above_comments:
                output.extend(above_comments)
                above_comments = None

            if "*" in from_imports and cfg.combine_star:
                stmt = wrap.line(
                    with_comments(
                        _with_star_comments(parsed, module, list(comments or ())),
                        f"{import_start}*",
                        removed=cfg.ignore_comments,
                        comment_prefix=cfg.comment_prefix,
                    ),
                    parsed.line_separator,
                    cfg,
                )
                output.append(stmt)
                from_imports = [fi for fi in from_imports if fi in as_imports]
                only_show_as = True
                continue

            if cfg.force_single_line and module not in cfg.single_line_exclusions:
                while from_imports:
                    fi = from_imports.pop(0)
                    line = with_comments(
                        comments,
                        import_start + fi,
                        removed=cfg.ignore_comments,
                        comment_prefix=cfg.comment_prefix,
                    )
                    nested = parsed.categorized_comments["nested"].get(module, {}).pop(fi, None)
                    if nested is not None:
                        line += f"{(comments and ';') or cfg.comment_prefix} {nested}"
                    if fi in as_imports:
                        if parsed.imports[section][import_key][module][fi] and not only_show_as:
                            output.append(wrap.line(line, parsed.line_separator, cfg))
                        f_comments = parsed.categorized_comments["straight"].get(f"{module}.{fi}")
                        sorted_as = sorting.sort(cfg, as_imports[fi]) if not cfg.only_sections else as_imports[fi]
                        for as_imp in sorted_as:
                            output.append(
                                with_comments(
                                    f_comments,
                                    wrap.line(import_start + as_imp, parsed.line_separator, cfg),
                                    removed=cfg.ignore_comments,
                                    comment_prefix=cfg.comment_prefix,
                                )
                            )
                    else:
                        output.append(wrap.line(line, parsed.line_separator, cfg))
                    comments = None
                continue

            processed_as = False
            while from_imports and from_imports[0] in as_imports:
                processed_as = True
                fi = from_imports.pop(0)
                if not cfg.only_sections:
                    as_imports[fi] = sorting.sort(cfg, as_imports[fi])
                f_comments = parsed.categorized_comments["straight"].get(f"{module}.{fi}") or []
                if parsed.imports[section][import_key][module][fi] and not only_show_as:
                    spec_comm = parsed.categorized_comments["nested"].get(module, {}).pop(fi, None)
                    if spec_comm is not None:
                        f_comments.append(spec_comm)
                    output.append(
                        wrap.line(
                            with_comments(
                                f_comments,
                                import_start + fi,
                                removed=cfg.ignore_comments,
                                comment_prefix=cfg.comment_prefix,
                            ),
                            parsed.line_separator,
                            cfg,
                        )
                    )
                for as_imp in as_imports[fi]:
                    opening_comments = list(f_comments)
                    spec_comm = parsed.categorized_comments["nested"].get(module, {}).pop(as_imp, None)
                    if spec_comm is not None:
                        f_comments.append(spec_comm)
                    imp_line = import_start + as_imp
                    if opening_comments and cfg.use_parentheses:
                        lines = wrap.line(
                            with_comments(
                                [spec_comm] if spec_comm else [],
                                imp_line,
                                removed=cfg.ignore_comments,
                                comment_prefix=cfg.comment_prefix,
                            ),
                            parsed.line_separator,
                            cfg,
                        ).split(parsed.line_separator)
                        opening = with_comments(
                            opening_comments,
                            "",
                            removed=cfg.ignore_comments,
                            comment_prefix=cfg.comment_prefix,
                        )
                        if opening:
                            lines[0] += opening
                        output.append(parsed.line_separator.join(lines))
                    else:
                        output.append(
                            wrap.line(
                                with_comments(
                                    f_comments,
                                    imp_line,
                                    removed=cfg.ignore_comments,
                                    comment_prefix=cfg.comment_prefix,
                                ),
                                parsed.line_separator,
                                cfg,
                            )
                        )
                f_comments = []

            if "*" in from_imports:
                output.append(
                    with_comments(
                        _with_star_comments(parsed, module, []),
                        f"{import_start}*",
                        removed=cfg.ignore_comments,
                        comment_prefix=cfg.comment_prefix,
                    )
                )
                from_imports.remove("*")

            for fi in list(from_imports):
                nested_comm = parsed.categorized_comments["nested"].get(module, {}).pop(fi, None)
                if nested_comm is not None:
                    if nested_comm.lower().startswith("noqa") and cfg.multi_line_output == wrap.Modes.HANGING_INDENT:  # type: ignore[attr-defined]
                        comments = list(comments) if comments else []
                        comments.append(nested_comm)
                        continue
                    from_imports.remove(fi)
                    use_comm = [] if from_imports else comments
                    if not from_imports:
                        comments = None
                    line = with_comments(
                        use_comm,
                        import_start + fi,
                        removed=cfg.ignore_comments,
                        comment_prefix=cfg.comment_prefix,
                    )
                    line += f"{(use_comm and ';') or cfg.comment_prefix} {nested_comm}" if nested_comm else ""
                    output.append(wrap.line(line, parsed.line_separator, cfg))

            remaining = []
            while from_imports and (
                from_imports[0] not in as_imports
                or (cfg.combine_as_imports and parsed.imports[section][import_key][module][from_imports[0]])
            ):
                remaining.append(from_imports.pop(0))
            if cfg.combine_as_imports:
                comments = (comments or []) + list(
                    parsed.categorized_comments["from"].pop(f"{module}.__combined_as__", ())
                )
            stmt = with_comments(
                comments,
                import_start + (", ").join(remaining),
                removed=cfg.ignore_comments,
                comment_prefix=cfg.comment_prefix,
            )
            if not remaining:
                stmt = ""

            do_multi = False
            if cfg.force_grid_wrap and len(remaining) >= cfg.force_grid_wrap:
                do_multi = True
            if len(stmt) > cfg.line_length and len(remaining) > 1:
                do_multi = True
            if (
                len(stmt) > cfg.line_length
                and remaining
                and cfg.multi_line_output not in (wrap.Modes.GRID, wrap.Modes.VERTICAL)  # type: ignore
            ):
                do_multi = True

            if stmt and cfg.split_on_trailing_comma and module in parsed.trailing_commas and not processed_as:
                stmt = wrap.import_statement(
                    import_start=import_start,
                    from_imports=remaining,
                    comments=comments,
                    line_separator=parsed.line_separator,
                    config=cfg,
                    explode=True,
                )
            elif do_multi:
                stmt = wrap.import_statement(
                    import_start=import_start,
                    from_imports=remaining,
                    comments=comments,
                    line_separator=parsed.line_separator,
                    config=cfg,
                )
                if cfg.multi_line_output == wrap.Modes.GRID:  # type: ignore
                    alt = wrap.import_statement(
                        import_start=import_start,
                        from_imports=remaining,
                        comments=comments,
                        line_separator=parsed.line_separator,
                        config=cfg,
                        multi_line_output=wrap.Modes.VERTICAL_GRID,  # type: ignore
                    )
                    if max(len(l) for l in stmt.split(parsed.line_separator)) > cfg.line_length:
                        stmt = alt
            elif len(stmt) > cfg.line_length:
                stmt = wrap.line(stmt, parsed.line_separator, cfg)

            comments = None
            if stmt:
                output.append(stmt)

    return output


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
    rem_set = set(remove_imports)

    as_present = any(m in parsed.as_map["straight"] for m in straight_modules)

    if config.combine_straight_imports and not as_present:
        if not straight_modules:
            return []
        above: list[str] = []
        inline: list[str] = []
        for mod in straight_modules:
            if mod in parsed.categorized_comments["above"]["straight"]:
                above.extend(parsed.categorized_comments["above"]["straight"].pop(mod))
            if mod in parsed.categorized_comments["straight"]:
                inline.extend(parsed.categorized_comments["straight"][mod])
        combined = ", ".join(straight_modules)
        output.extend(above)
        if inline:
            inline_str = " ".join(c for c in inline if c)
            output.append(f"{import_type} {combined}  # {inline_str}" if inline_str else f"{import_type} {combined}  #")
        else:
            output.append(f"{import_type} {combined}")
        return output

    for mod in straight_modules:
        if mod in rem_set:
            continue
        definitions: list[tuple[str, str]] = []
        if mod in parsed.as_map["straight"]:
            if parsed.imports[section]["lazy_straight" if is_lazy else "straight"][mod]:
                definitions.append((f"{import_type} {mod}", mod))
            definitions.extend(
                (f"{import_type} {mod} as {as_imp}", f"{mod} as {as_imp}")
                for as_imp in parsed.as_map["straight"][mod]
            )
        else:
            definitions.append((f"{import_type} {mod}", mod))

        above = parsed.categorized_comments["above"]["straight"].pop(mod, None)
        if above:
            output.extend(above)
        for idef, imodule in definitions:
            output.append(
                with_comments(
                    parsed.categorized_comments["straight"].get(imodule),
                    idef,
                    removed=config.ignore_comments,
                    comment_prefix=config.comment_prefix,
                )
            )
    return output


def _output_as_string(lines: list[str], line_separator: str) -> str:
    return line_separator.join(_normalize_empty_lines(lines))


def _normalize_empty_lines(lines: list[str]) -> list[str]:
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines.append("")
    return lines


class _LineWithComments(str):
    comments: list[str]

    def __new__(cls: type["_LineWithComments"], value: Any, comments: list[str]) -> "_LineWithComments":
        instance = super().__new__(cls, value)
        instance.comments = comments
        return instance


def _ensure_newline_before_comment(output: list[str]) -> list[str]:
    new_output: list[str] = []

    def is_comment(line: str | None) -> bool:
        return bool(line and line.startswith("#"))

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


def _separate_packages(section_output: list[str], config: Config) -> list[str]:
    group_keys: set[str] = set()
    comments_above: list[str] = []
    processed: list[str] = []

    for line in section_output:
        if line.startswith("#"):
            comments_above.append(line)
            continue

        package_name = line.split(" ")[1]
        _, reason = module_with_reason(package_name, config)

        if "Matched configured known pattern" in reason:
            depth = len(reason.split(".")) - 1
            key = ".".join(package_name.split(".")[: depth + 1])
        else:
            key = package_name.split(".")[0]

        if key not in group_keys:
            if group_keys:
                processed.append("")
            group_keys.add(key)

        if comments_above:
            processed.extend(comments_above)
            comments_above = []

        processed.append(line)

    return processed