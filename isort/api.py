import shutil
import sys
import textwrap
from io import StringIO
from itertools import chain
from pathlib import Path
from typing import List, Optional, TextIO, Union
from warnings import warn

from . import io, output, parse
from .exceptions import (
    ExistingSyntaxErrors,
    FileSkipComment,
    FileSkipSetting,
    IntroducedSyntaxErrors,
)
from .format import (
    ask_whether_to_apply_changes_to_file,
    format_natural,
    remove_whitespace,
    show_unified_diff,
)
from .io import Empty
from .place import module as place_module  # skipcq: PYL-W0611 (intended export of public API)
from .place import module_with_reason as place_module_with_reason  # skipcq: PYL-W0611 (^)
from .settings import DEFAULT_CONFIG, FILE_SKIP_COMMENTS, Config

CIMPORT_IDENTIFIERS = ("cimport ", "cimport*", "from.cimport")
IMPORT_START_IDENTIFIERS = ("from ", "from.import", "import ", "import*") + CIMPORT_IDENTIFIERS
COMMENT_INDICATORS = ('"""', "'''", "'", '"', "#")


def sort_code_string(
    code: str,
    extension: Optional[str] = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Optional[Path] = None,
    disregard_skip: bool = False,
    **config_kwargs,
):
    """Sorts any imports within the provided code string, returning a new string with them sorted.

    - **code**: The string of code with imports that need to be sorted.
    - **extension**: The file extension that contains imports. Defaults to filename extension or py.
    - **config**: The config object to use when sorting imports.
    - **file_path**: The disk location where the code string was pulled from.
    - **disregard_skip**: set to `True` if you want to ignore a skip set in config for this file.
    - ****config_kwargs**: Any config modifications.
    """
    input_stream = StringIO(code)
    output_stream = StringIO()
    config = _config(path=file_path, config=config, **config_kwargs)
    sort_stream(
        input_stream,
        output_stream,
        extension=extension,
        config=config,
        file_path=file_path,
        disregard_skip=disregard_skip,
    )
    output_stream.seek(0)
    return output_stream.read()


def check_code_string(
    code: str,
    show_diff: bool = False,
    extension: Optional[str] = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Optional[Path] = None,
    disregard_skip: bool = False,
    **config_kwargs,
) -> bool:
    """Checks the order, format, and categorization of imports within the provided code string.
    Returns `True` if everything is correct, otherwise `False`.

    - **code**: The string of code with imports that need to be sorted.
    - **show_diff**: If `True` the changes that need to be done will be printed to stdout.
    - **extension**: The file extension that contains imports. Defaults to filename extension or py.
    - **config**: The config object to use when sorting imports.
    - **file_path**: The disk location where the code string was pulled from.
    - **disregard_skip**: set to `True` if you want to ignore a skip set in config for this file.
    - ****config_kwargs**: Any config modifications.
    """
    config = _config(path=file_path, config=config, **config_kwargs)
    return check_stream(
        StringIO(code),
        show_diff=show_diff,
        extension=extension,
        config=config,
        file_path=file_path,
        disregard_skip=disregard_skip,
    )


def sort_stream(
    input_stream: TextIO,
    output_stream: TextIO,
    extension: Optional[str] = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Optional[Path] = None,
    disregard_skip: bool = False,
    **config_kwargs,
):
    """Sorts any imports within the provided code stream, outputs to the provided output stream.
    Directly returns nothing.

    - **input_stream**: The stream of code with imports that need to be sorted.
    - **output_stream**: The stream where sorted imports should be written to.
    - **extension**: The file extension that contains imports. Defaults to filename extension or py.
    - **config**: The config object to use when sorting imports.
    - **file_path**: The disk location where the code string was pulled from.
    - **disregard_skip**: set to `True` if you want to ignore a skip set in config for this file.
    - ****config_kwargs**: Any config modifications.
    """
    config = _config(path=file_path, config=config, **config_kwargs)
    content_source = str(file_path or "Passed in content")
    if not disregard_skip:
        if file_path and config.is_skipped(file_path):
            raise FileSkipSetting(content_source)

    _internal_output = output_stream

    if config.atomic:
        try:
            file_content = input_stream.read()
            compile(file_content, content_source, "exec", 0, 1)
            input_stream = StringIO(file_content)
        except SyntaxError:
            raise ExistingSyntaxErrors(content_source)

        if not output_stream.readable():
            _internal_output = StringIO()

    try:
        changed = _sort_imports(
            input_stream,
            _internal_output,
            extension=extension or (file_path and file_path.suffix.lstrip(".")) or "py",
            config=config,
        )
    except FileSkipComment:
        raise FileSkipComment(content_source)

    if config.atomic:
        _internal_output.seek(0)
        try:
            compile(_internal_output.read(), content_source, "exec", 0, 1)
            _internal_output.seek(0)
            if _internal_output != output_stream:
                output_stream.write(_internal_output.read())
        except SyntaxError:  # pragma: no cover
            raise IntroducedSyntaxErrors(content_source)

    return changed


def check_stream(
    input_stream: TextIO,
    show_diff: bool = False,
    extension: Optional[str] = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Optional[Path] = None,
    disregard_skip: bool = False,
    **config_kwargs,
) -> bool:
    """Checks any imports within the provided code stream, returning `False` if any unsorted or
    incorrectly imports are found or `True` if no problems are identified.

    - **input_stream**: The stream of code with imports that need to be sorted.
    - **show_diff**: If `True` the changes that need to be done will be printed to stdout.
    - **extension**: The file extension that contains imports. Defaults to filename extension or py.
    - **config**: The config object to use when sorting imports.
    - **file_path**: The disk location where the code string was pulled from.
    - **disregard_skip**: set to `True` if you want to ignore a skip set in config for this file.
    - ****config_kwargs**: Any config modifications.
    """
    config = _config(path=file_path, config=config, **config_kwargs)

    changed: bool = sort_stream(
        input_stream=input_stream,
        output_stream=Empty,
        extension=extension,
        config=config,
        file_path=file_path,
        disregard_skip=disregard_skip,
    )

    if not changed:
        if config.verbose:
            print(f"SUCCESS: {file_path or ''} Everything Looks Good!")
        return True
    else:
        print(f"ERROR: {file_path or ''} Imports are incorrectly sorted and/or formatted.")
        if show_diff:
            output_stream = StringIO()
            input_stream.seek(0)
            file_contents = input_stream.read()
            sort_stream(
                input_stream=StringIO(file_contents),
                output_stream=output_stream,
                extension=extension,
                config=config,
                file_path=file_path,
                disregard_skip=disregard_skip,
            )
            output_stream.seek(0)

            show_unified_diff(
                file_input=file_contents, file_output=output_stream.read(), file_path=file_path
            )
        return False


def check_file(
    filename: Union[str, Path],
    show_diff: bool = False,
    config: Config = DEFAULT_CONFIG,
    file_path: Optional[Path] = None,
    disregard_skip: bool = True,
    extension: Optional[str] = None,
    **config_kwargs,
) -> bool:
    """Checks any imports within the provided file, returning `False` if any unsorted or
    incorrectly imports are found or `True` if no problems are identified.

    - **filename**: The name or Path of the file to check.
    - **show_diff**: If `True` the changes that need to be done will be printed to stdout.
    - **config**: The config object to use when sorting imports.
    - **file_path**: The disk location where the code string was pulled from.
    - **disregard_skip**: set to `True` if you want to ignore a skip set in config for this file.
    - **extension**: The file extension that contains imports. Defaults to filename extension or py.
    - ****config_kwargs**: Any config modifications.
    """
    with io.File.read(filename) as source_file:
        return check_stream(
            source_file.stream,
            show_diff=show_diff,
            extension=extension,
            config=config,
            file_path=file_path or source_file.path,
            disregard_skip=disregard_skip,
            **config_kwargs,
        )


def sort_file(
    filename: Union[str, Path],
    extension: Optional[str] = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Optional[Path] = None,
    disregard_skip: bool = True,
    ask_to_apply: bool = False,
    show_diff: bool = False,
    write_to_stdout: bool = False,
    **config_kwargs,
):
    """Sorts and formats any groups of imports imports within the provided file or Path.

    - **filename**: The name or Path of the file to format.
    - **extension**: The file extension that contains imports. Defaults to filename extension or py.
    - **config**: The config object to use when sorting imports.
    - **file_path**: The disk location where the code string was pulled from.
    - **disregard_skip**: set to `True` if you want to ignore a skip set in config for this file.
    - **ask_to_apply**: If `True`, prompt before applying any changes.
    - **show_diff**: If `True` the changes that need to be done will be printed to stdout.
    - **write_to_stdout**: If `True`, write to stdout instead of the input file.
    - ****config_kwargs**: Any config modifications.
    """
    with io.File.read(filename) as source_file:
        changed: bool = False
        try:
            if write_to_stdout:
                changed = sort_stream(
                    input_stream=source_file.stream,
                    output_stream=sys.stdout,
                    config=config,
                    file_path=file_path or source_file.path,
                    disregard_skip=disregard_skip,
                    extension=extension,
                    **config_kwargs,
                )
            else:
                tmp_file = source_file.path.with_suffix(source_file.path.suffix + ".isorted")
                try:
                    with tmp_file.open(
                        "w", encoding=source_file.encoding, newline=""
                    ) as output_stream:
                        shutil.copymode(filename, tmp_file)
                        changed = sort_stream(
                            input_stream=source_file.stream,
                            output_stream=output_stream,
                            config=config,
                            file_path=file_path or source_file.path,
                            disregard_skip=disregard_skip,
                            extension=extension,
                            **config_kwargs,
                        )
                    if changed:
                        if show_diff or ask_to_apply:
                            source_file.stream.seek(0)
                            show_unified_diff(
                                file_input=source_file.stream.read(),
                                file_output=tmp_file.read_text(encoding=source_file.encoding),
                                file_path=file_path or source_file.path,
                            )
                            if show_diff or (
                                ask_to_apply
                                and not ask_whether_to_apply_changes_to_file(str(source_file.path))
                            ):
                                return
                        source_file.stream.close()
                        tmp_file.replace(source_file.path)
                        if not config.quiet:
                            print(f"Fixing {source_file.path}")
                finally:
                    try:  # Python 3.8+: use `missing_ok=True` instead of try except.
                        tmp_file.unlink()
                    except FileNotFoundError:
                        pass
        except ExistingSyntaxErrors:
            warn("{file_path} unable to sort due to existing syntax errors")
        except IntroducedSyntaxErrors:  # pragma: no cover
            warn("{file_path} unable to sort as isort introduces new syntax errors")


def _config(
    path: Optional[Path] = None, config: Config = DEFAULT_CONFIG, **config_kwargs
) -> Config:
    if path:
        if (
            config is DEFAULT_CONFIG
            and "settings_path" not in config_kwargs
            and "settings_file" not in config_kwargs
        ):
            config_kwargs["settings_path"] = path

    if config_kwargs:
        if config is not DEFAULT_CONFIG:
            raise ValueError(
                "You can either specify custom configuration options using kwargs or "
                "passing in a Config object. Not Both!"
            )

        config = Config(**config_kwargs)

    return config


def _sort_imports(
    input_stream: TextIO,
    output_stream: TextIO,
    extension: str = "py",
    config: Config = DEFAULT_CONFIG,
) -> bool:
    """Parses stream identifying sections of contiguous imports and sorting them

    Code with unsorted imports is read from the provided `input_stream`, sorted and then
    outputted to the specified `output_stream`.

    - `input_stream`: Text stream with unsorted import sections.
    - `output_stream`: Text stream to output sorted inputs into.
    - `config`: Config settings to use when sorting imports. Defaults settings.
        - *Default*: `isort.settings.DEFAULT_CONFIG`.
    - `extension`: The file extension or file extension rules that should be used.
        - *Default*: `"py"`.
        - *Choices*: `["py", "pyi", "pyx"]`.

    Returns `True` if there were changes that needed to be made (errors present) from what
    was provided in the input_stream, otherwise `False`.
    """
    line_separator: str = config.line_ending
    add_imports: List[str] = [format_natural(addition) for addition in config.add_imports]
    import_section: str = ""
    next_import_section: str = ""
    next_cimports: bool = False
    in_quote: str = ""
    first_comment_index_start: int = -1
    first_comment_index_end: int = -1
    contains_imports: bool = False
    in_top_comment: bool = False
    first_import_section: bool = True
    section_comments = [f"# {heading}" for heading in config.import_headings.values()]
    indent: str = ""
    isort_off: bool = False
    cimports: bool = False
    made_changes: bool = False

    for index, line in enumerate(chain(input_stream, (None,))):
        if line is None:
            if index == 0 and not config.force_adds:
                return False

            not_imports = True
            line = ""
            if not line_separator:
                line_separator = "\n"
        else:
            stripped_line = line.strip()
            if stripped_line and not line_separator:
                line_separator = line[len(line.rstrip()) :]

            for file_skip_comment in FILE_SKIP_COMMENTS:
                if file_skip_comment in line:
                    raise FileSkipComment("Passed in content")

            if (
                (index == 0 or (index in (1, 2) and not contains_imports))
                and stripped_line.startswith("#")
                and stripped_line not in section_comments
            ):
                in_top_comment = True
            elif in_top_comment:
                if not line.startswith("#") or stripped_line in section_comments:
                    in_top_comment = False
                    first_comment_index_end = index - 1

            if (not stripped_line.startswith("#") or in_quote) and '"' in line or "'" in line:
                char_index = 0
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

            not_imports = bool(in_quote) or in_top_comment or isort_off
            if not (in_quote or in_top_comment):
                stripped_line = line.strip()
                if isort_off:
                    if stripped_line == "# isort: on":
                        isort_off = False
                elif stripped_line == "# isort: off":
                    not_imports = True
                    isort_off = True
                elif stripped_line == "# isort: split":
                    not_imports = True
                elif not (stripped_line or contains_imports):
                    if add_imports and not indent:
                        import_section += line_separator.join(add_imports) + line_separator
                        contains_imports = True
                        add_imports = []
                    else:
                        not_imports = True
                elif (
                    not stripped_line
                    or stripped_line.startswith("#")
                    and (not indent or indent + line.lstrip() == line)
                ):
                    import_section += line
                elif stripped_line.startswith(IMPORT_START_IDENTIFIERS):
                    contains_imports = True

                    new_indent = line[: -len(line.lstrip())]
                    import_statement = line
                    stripped_line = line.strip().split("#")[0]
                    while stripped_line.endswith("\\") or (
                        "(" in stripped_line and ")" not in stripped_line
                    ):
                        if stripped_line.endswith("\\"):
                            while stripped_line and stripped_line.endswith("\\"):
                                line = input_stream.readline()
                                stripped_line = line.strip().split("#")[0]
                                import_statement += line
                        else:
                            while ")" not in stripped_line:
                                line = input_stream.readline()
                                stripped_line = line.strip().split("#")[0]
                                import_statement += line

                    cimport_statement: bool = False
                    if (
                        import_statement.lstrip().startswith(CIMPORT_IDENTIFIERS)
                        or " cimport " in import_statement
                        or " cimport*" in import_statement
                        or " cimport(" in import_statement
                        or ".cimport" in import_statement
                    ):
                        cimport_statement = True

                    if cimport_statement != cimports or (new_indent != indent and import_section):
                        if import_section:
                            next_cimports = cimport_statement
                            next_import_section = import_statement
                            import_statement = ""
                            not_imports = True
                            line = ""
                        else:
                            cimports = cimport_statement

                    indent = new_indent
                    import_section += import_statement
                else:
                    not_imports = True

        if not_imports:
            raw_import_section: str = import_section
            if (
                add_imports
                and not in_top_comment
                and not in_quote
                and not import_section
                and not line.lstrip().startswith(COMMENT_INDICATORS)
            ):
                import_section = line_separator.join(add_imports) + line_separator
                contains_imports = True
                add_imports = []

            if next_import_section and not import_section:  # pragma: no cover
                raw_import_section = import_section = next_import_section
                next_import_section = ""

            if import_section:
                if add_imports and not indent:
                    import_section = (
                        line_separator.join(add_imports) + line_separator + import_section
                    )
                    contains_imports = True
                    add_imports = []

                if not indent:
                    import_section += line
                    raw_import_section += line
                if not contains_imports:
                    output_stream.write(import_section)
                else:
                    leading_whitespace = import_section[: -len(import_section.lstrip())]
                    trailing_whitespace = import_section[len(import_section.rstrip()) :]
                    if first_import_section and not import_section.lstrip(
                        line_separator
                    ).startswith(COMMENT_INDICATORS):
                        import_section = import_section.lstrip(line_separator)
                        raw_import_section = raw_import_section.lstrip(line_separator)
                        first_import_section = False

                    if indent:
                        import_section = line_separator.join(
                            line.lstrip() for line in import_section.split(line_separator)
                        )
                        out_config = Config(
                            config=config,
                            line_length=max(config.line_length - len(indent), 0),
                            lines_after_imports=1,
                        )
                    else:
                        out_config = config

                    sorted_import_section = output.sorted_imports(
                        parse.file_contents(import_section, config=config),
                        out_config,
                        extension,
                        import_type="cimport" if cimports else "import",
                    )
                    if not (import_section.strip() and not sorted_import_section):
                        if indent:
                            sorted_import_section = (
                                leading_whitespace
                                + textwrap.indent(sorted_import_section, indent).strip()
                                + trailing_whitespace
                            )

                        if not made_changes:
                            if config.ignore_whitespace:
                                compare_in = remove_whitespace(
                                    raw_import_section, line_separator=line_separator
                                ).strip()
                                compare_out = remove_whitespace(
                                    sorted_import_section, line_separator=line_separator
                                ).strip()
                            else:
                                compare_in = raw_import_section.strip()
                                compare_out = sorted_import_section.strip()

                            if compare_out != compare_in:
                                made_changes = True

                        output_stream.write(sorted_import_section)
                        if not line and not indent and next_import_section:
                            output_stream.write(line_separator)

                if indent:
                    output_stream.write(line)
                    if not next_import_section:
                        indent = ""

                if next_import_section:
                    cimports = next_cimports
                    contains_imports = True
                else:
                    contains_imports = False
                import_section = next_import_section
                next_import_section = ""
            else:
                output_stream.write(line)
                not_imports = False

    return made_changes
