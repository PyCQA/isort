"""Defines parsing functions used by isort for parsing import definitions"""
from collections import OrderedDict, defaultdict, namedtuple
from itertools import chain
from typing import TYPE_CHECKING, Any, Dict, Generator, Iterator, List, NamedTuple, Optional, Tuple
from warnings import warn

from isort.format import format_natural

from .comments import parse as parse_comments
from .finders import FindersManager

if TYPE_CHECKING:
    from mypy_extensions import TypedDict

    CommentsAboveDict = TypedDict(
        "CommentsAboveDict", {"straight": Dict[str, Any], "from": Dict[str, Any]}
    )

    CommentsDict = TypedDict(
        "CommentsDict",
        {
            "from": Dict[str, Any],
            "straight": Dict[str, Any],
            "nested": Dict[str, Any],
            "above": CommentsAboveDict,
        },
    )


def _infer_line_separator(file_contents: str) -> str:
    if "\r\n" in file_contents:
        return "\r\n"
    elif "\r" in file_contents:
        return "\r"
    else:
        return "\n"


def import_type(line: str) -> Optional[str]:
    """If the current line is an import line it will return its type (from or straight)"""
    if "isort:skip" in line or "NOQA" in line:
        return None
    elif line.startswith("import "):
        return "straight"
    elif line.startswith("from "):
        return "from"
    return None


def _strip_syntax(import_string: str) -> str:
    import_string = import_string.replace("_import", "[[i]]")
    for remove_syntax in ["\\", "(", ")", ","]:
        import_string = import_string.replace(remove_syntax, " ")
    import_list = import_string.split()
    for key in ("from", "import"):
        if key in import_list:
            import_list.remove(key)
    import_string = " ".join(import_list)
    import_string = import_string.replace("[[i]]", "_import")
    return import_string.replace("{ ", "{|").replace(" }", "|}")


def skip_line(
    line: str,
    in_quote: str,
    in_top_comment: bool,
    index: int,
    section_comments: List[str],
    first_comment_index_start: int,
    first_comment_index_end: int,
) -> Tuple[bool, str, bool, int, int]:
    """Determine if a given line should be skipped.

    Returns back a tuple containing:

    (skip_line: bool,
     in_quote: str,
     in_top_comment: bool,
     first_comment_index_start: int,
     first_comment_index_end: int)
    """
    skip_line = bool(in_quote)
    if index == 1 and line.startswith("#"):
        in_top_comment = True
        return (True, in_quote, in_top_comment, first_comment_index_start, first_comment_index_end)
    elif in_top_comment:
        if not line.startswith("#") or line in section_comments:
            in_top_comment = False
            first_comment_index_end = index - 1

    if '"' in line or "'" in line:
        char_index = 0
        if first_comment_index_start == -1 and (line.startswith('"') or line.startswith("'")):
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

    return (
        bool(skip_line or in_quote or in_top_comment),
        in_quote,
        in_top_comment,
        first_comment_index_start,
        first_comment_index_end,
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


def file_contents(contents: str, config: Dict[str, Any]) -> ParsedContent:
    """Parses a python file taking out and categorizing imports."""
    line_separator: str = config["line_ending"] or _infer_line_separator(contents)
    add_imports = (format_natural(addition) for addition in config["add_imports"])
    in_lines = contents.split(line_separator)
    out_lines = []
    original_line_count = len(in_lines)

    sections: Any = namedtuple("Sections", config["sections"])(*config["sections"])
    section_comments = [
        "# " + value for key, value in config.items() if key.startswith("import_heading") and value
    ]
    finder = FindersManager(config=config, sections=sections)

    if original_line_count > 1 or in_lines[:1] not in ([], [""]) or config["force_adds"]:
        in_lines.extend(add_imports)

    line_count = len(in_lines)

    place_imports: Dict[str, List[str]] = {}
    import_placements: Dict[str, str] = {}
    as_map: Dict[str, List[str]] = defaultdict(list)
    imports: OrderedDict[str, Dict[str, Any]] = OrderedDict()
    for section in chain(sections, config["forced_separate"]):
        imports[section] = {"straight": OrderedDict(), "from": OrderedDict()}
    categorized_comments: CommentsDict = {
        "from": {},
        "straight": {},
        "nested": {},
        "above": {"straight": {}, "from": {}},
    }

    index = 0
    import_index = -1
    in_quote = ""
    in_top_comment = False
    first_comment_index_start = -1
    first_comment_index_end = -1
    while index < line_count:
        raw_line = line = in_lines[index]
        line = line.replace("from.import ", "from . import ")
        line = line.replace("\t", " ").replace("import*", "import *")
        line = line.replace(" .import ", " . import ")
        index += 1
        statement_index = index

        (
            skipping_line,
            in_quote,
            in_top_comment,
            first_comment_index_start,
            first_comment_index_end,
        ) = skip_line(
            line,
            in_quote=in_quote,
            in_top_comment=in_top_comment,
            index=index,
            section_comments=section_comments,
            first_comment_index_start=first_comment_index_start,
            first_comment_index_end=first_comment_index_end,
        )

        if line in section_comments and not skipping_line:
            if import_index == -1:
                import_index = index - 1
            continue

        if "isort:imports-" in line and line.startswith("#"):
            section = line.split("isort:imports-")[-1].split()[0].upper()
            place_imports[section] = []
            import_placements[line] = section

        if ";" in line:
            for part in (part.strip() for part in line.split(";")):
                if part and not part.startswith("from ") and not part.startswith("import "):
                    skipping_line = True

        type_of_import: str = import_type(line) or ""
        if not type_of_import or skipping_line:
            out_lines.append(raw_line)
            continue

        for line in (line.strip() for line in line.split(";")):
            type_of_import = import_type(line) or ""
            if not type_of_import:
                out_lines.append(line)
                continue

            if import_index == -1:
                import_index = index - 1
            nested_comments = {}
            import_string, comment = parse_comments(line)
            comments = [comment] if comment else []
            line_parts = [part for part in _strip_syntax(import_string).strip().split(" ") if part]
            if (
                type_of_import == "from"
                and len(line_parts) == 2
                and line_parts[1] != "*"
                and comments
            ):
                nested_comments[line_parts[-1]] = comments[0]

            if "(" in line.split("#")[0] and index < line_count:
                while not line.strip().endswith(")") and index < line_count:
                    line, new_comment = parse_comments(in_lines[index])
                    index += 1
                    if new_comment:
                        comments.append(new_comment)
                    stripped_line = _strip_syntax(line).strip()
                    if (
                        type_of_import == "from"
                        and stripped_line
                        and " " not in stripped_line
                        and new_comment
                    ):
                        nested_comments[stripped_line] = comments[-1]
                    import_string += line_separator + line
            else:
                while line.strip().endswith("\\"):
                    line, new_comment = parse_comments(in_lines[index])
                    index += 1
                    if new_comment:
                        comments.append(new_comment)

                    # Still need to check for parentheses after an escaped line
                    if (
                        "(" in line.split("#")[0]
                        and ")" not in line.split("#")[0]
                        and index < line_count
                    ):
                        stripped_line = _strip_syntax(line).strip()
                        if (
                            type_of_import == "from"
                            and stripped_line
                            and " " not in stripped_line
                            and new_comment
                        ):
                            nested_comments[stripped_line] = comments[-1]
                        import_string += line_separator + line

                        while not line.strip().endswith(")") and index < line_count:
                            line, new_comment = parse_comments(in_lines[index])
                            index += 1
                            if new_comment:
                                comments.append(new_comment)
                            stripped_line = _strip_syntax(line).strip()
                            if (
                                type_of_import == "from"
                                and stripped_line
                                and " " not in stripped_line
                                and new_comment
                            ):
                                nested_comments[stripped_line] = comments[-1]
                            import_string += line_separator + line

                    stripped_line = _strip_syntax(line).strip()
                    if (
                        type_of_import == "from"
                        and stripped_line
                        and " " not in stripped_line
                        and new_comment
                    ):
                        nested_comments[stripped_line] = comments[-1]
                    if import_string.strip().endswith(" import") or line.strip().startswith(
                        "import "
                    ):
                        import_string += line_separator + line
                    else:
                        import_string = import_string.rstrip().rstrip("\\") + " " + line.lstrip()

            if type_of_import == "from":
                import_string = import_string.replace("import(", "import (")
                parts = import_string.split(" import ")
                from_import = parts[0].split(" ")
                import_string = " import ".join(
                    [from_import[0] + " " + "".join(from_import[1:])] + parts[1:]
                )

            just_imports = [
                item.replace("{|", "{ ").replace("|}", " }")
                for item in _strip_syntax(import_string).split()
            ]
            straight_import = True
            if "as" in just_imports and (just_imports.index("as") + 1) < len(just_imports):
                straight_import = False
                while "as" in just_imports:
                    as_index = just_imports.index("as")
                    if type_of_import == "from":
                        module = just_imports[0] + "." + just_imports[as_index - 1]
                        as_map[module].append(just_imports[as_index + 1])
                    else:
                        module = just_imports[as_index - 1]
                        as_map[module].append(just_imports[as_index + 1])
                    if not config["combine_as_imports"]:
                        categorized_comments["straight"][module] = comments
                        comments = []
                    del just_imports[as_index : as_index + 2]
            if type_of_import == "from":
                import_from = just_imports.pop(0)
                placed_module = finder.find(import_from)
                if config["verbose"]:
                    print(
                        "from-type place_module for {} returned {}".format(
                            import_from, placed_module
                        )
                    )
                if placed_module == "":
                    warn(
                        "could not place module {} of line {} --"
                        " Do you need to define a default section?".format(import_from, line)
                    )
                root = imports[placed_module][type_of_import]  # type: ignore
                for import_name in just_imports:
                    associated_comment = nested_comments.get(import_name)
                    if associated_comment:
                        categorized_comments["nested"].setdefault(import_from, {})[
                            import_name
                        ] = associated_comment
                        comments.pop(comments.index(associated_comment))
                if comments:
                    categorized_comments["from"].setdefault(import_from, []).extend(comments)

                if len(out_lines) > max(import_index, first_comment_index_end + 1, 1) - 1:
                    last = out_lines and out_lines[-1].rstrip() or ""
                    while (
                        last.startswith("#")
                        and not last.endswith('"""')
                        and not last.endswith("'''")
                        and "isort:imports-" not in last
                    ):
                        categorized_comments["above"]["from"].setdefault(import_from, []).insert(
                            0, out_lines.pop(-1)
                        )
                        if (
                            len(out_lines)
                            > max(import_index - 1, first_comment_index_end + 1, 1) - 1
                        ):
                            last = out_lines[-1].rstrip()
                        else:
                            last = ""
                    if statement_index - 1 == import_index:
                        import_index -= len(
                            categorized_comments["above"]["from"].get(import_from, [])
                        )

                if import_from not in root:
                    root[import_from] = OrderedDict(
                        (module, straight_import) for module in just_imports
                    )
                else:
                    root[import_from].update(
                        (module, straight_import | root[import_from].get(module, False))
                        for module in just_imports
                    )
            else:
                for module in just_imports:
                    if comments:
                        categorized_comments["straight"][module] = comments
                        comments = []

                    if len(out_lines) > max(import_index, first_comment_index_end + 1, 1) - 1:

                        last = out_lines and out_lines[-1].rstrip() or ""
                        while (
                            last.startswith("#")
                            and not last.endswith('"""')
                            and not last.endswith("'''")
                            and "isort:imports-" not in last
                        ):
                            categorized_comments["above"]["straight"].setdefault(module, []).insert(
                                0, out_lines.pop(-1)
                            )
                            if len(out_lines) > 0 and len(out_lines) != first_comment_index_end:
                                last = out_lines[-1].rstrip()
                            else:
                                last = ""
                        if index - 1 == import_index:
                            import_index -= len(
                                categorized_comments["above"]["straight"].get(module, [])
                            )
                    placed_module = finder.find(module)
                    if config["verbose"]:
                        print(
                            "else-type place_module for {} returned {}".format(
                                module, placed_module
                            )
                        )
                    if placed_module == "":
                        warn(
                            "could not place module {} of line {} --"
                            " Do you need to define a default section?".format(import_from, line)
                        )
                    straight_import |= imports[placed_module][type_of_import].get(  # type: ignore
                        module, False
                    )
                    imports[placed_module][type_of_import][module] = straight_import  # type: ignore

    change_count = len(out_lines) - original_line_count

    return ParsedContent(
        in_lines=in_lines,
        lines_without_imports=out_lines,
        import_index=import_index,
        place_imports=place_imports,
        import_placements=import_placements,
        as_map=as_map,
        imports=imports,
        categorized_comments=categorized_comments,
        first_comment_index_start=first_comment_index_start,
        first_comment_index_end=first_comment_index_end,
        change_count=change_count,
        original_line_count=original_line_count,
        line_separator=line_separator,
        sections=sections,
        section_comments=section_comments,
    )
