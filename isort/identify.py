"""Fast stream based import identification.
Eventually this will likely replace parse.py
"""

from collections.abc import Iterator
from functools import partial
from pathlib import Path
from typing import NamedTuple, TextIO

from ._parse_utils import (
    collect_import_continuation,
    import_type,
    normalize_from_import_string,
    normalize_line,
    skip_line,
    strip_syntax,
)
from .comments import parse as parse_comments
from .settings import DEFAULT_CONFIG, Config

STATEMENT_DECLARATIONS: tuple[str, ...] = ("def ", "cdef ", "cpdef ", "class ", "@", "async def")


class Import(NamedTuple):
    line_number: int
    indented: bool
    module: str
    attribute: str | None = None
    alias: str | None = None
    cimport: bool = False
    file_path: Path | None = None

    def statement(self) -> str:
        import_cmd = "cimport" if self.cimport else "import"
        if self.attribute:
            import_string = f"from {self.module} {import_cmd} {self.attribute}"
        else:
            import_string = f"{import_cmd} {self.module}"
        if self.alias:
            import_string += f" as {self.alias}"
        return import_string

    def __str__(self) -> str:
        return (
            f"{self.file_path or ''}:{self.line_number} "
            f"{'indented ' if self.indented else ''}{self.statement()}"
        )


# Ignore DeepSource cyclomatic complexity check for this function.
# skipcq: PY-R1000
def imports(
    input_stream: TextIO,
    config: Config = DEFAULT_CONFIG,
    file_path: Path | None = None,
    top_only: bool = False,
) -> Iterator[Import]:
    """Parses a python file taking out and categorizing imports."""
    in_quote = ""

    indexed_input = enumerate(input_stream)
    for index, raw_line in indexed_input:
        (skipping_line, in_quote) = skip_line(raw_line, in_quote=in_quote)

        if top_only and not in_quote and raw_line.startswith(STATEMENT_DECLARATIONS):
            break
        if skipping_line:
            continue

        stripped_line = raw_line.strip().split("#")[0]
        if stripped_line.startswith(("raise", "yield")):
            if stripped_line == "yield":
                while not stripped_line or stripped_line == "yield":
                    try:
                        index, next_line = next(indexed_input)
                    except StopIteration:
                        break

                    stripped_line = next_line.strip().split("#")[0]
            while stripped_line.endswith("\\"):
                try:
                    index, next_line = next(indexed_input)
                except StopIteration:
                    break

                stripped_line = next_line.strip().split("#")[0]
            continue  # pragma: no cover

        line, *end_of_line_comment = raw_line.split("#", 1)
        statements = [line.strip() for line in line.split(";")]
        if end_of_line_comment:
            statements[-1] = f"{statements[-1]}#{end_of_line_comment[0]}"

        for statement in statements:
            line, _raw_line = normalize_line(statement)
            type_of_import = import_type(line, config)
            if type_of_import is None:
                continue  # pragma: no cover

            import_string, _ = parse_comments(line)

            identified_import = partial(
                Import,
                index + 1,  # line numbers use 1 based indexing
                raw_line.startswith((" ", "\t")),
                file_path=file_path,
            )

            _, import_string, _ = collect_import_continuation(
                line,
                import_string,
                # We can disregard `index` here because it is no longer accessed after this line.
                lambda: parse_comments(next(indexed_input)[1]),
            )

            if type_of_import == "from":
                import_string = normalize_from_import_string(import_string)

            cimports: bool = " cimport " in import_string or import_string.startswith("cimport")

            identified_import = partial(identified_import, cimport=cimports)

            just_imports = [
                item.replace("{|", "{ ").replace("|}", " }")
                for item in strip_syntax(import_string).split()
            ]

            direct_imports = just_imports[1:]
            top_level_module = ""
            if "as" in just_imports and (just_imports.index("as") + 1) < len(just_imports):
                while "as" in just_imports:
                    attribute = None
                    as_index = just_imports.index("as")
                    if type_of_import == "from":
                        attribute = just_imports[as_index - 1]
                        top_level_module = just_imports[0]
                        module = top_level_module + "." + attribute
                        alias = just_imports[as_index + 1]
                        direct_imports.remove(attribute)
                        direct_imports.remove(alias)
                        direct_imports.remove("as")
                        just_imports[1:] = direct_imports
                        if attribute == alias and config.remove_redundant_aliases:
                            yield identified_import(top_level_module, attribute)
                        else:
                            yield identified_import(top_level_module, attribute, alias=alias)

                    else:
                        module = just_imports[as_index - 1]
                        alias = just_imports[as_index + 1]
                        just_imports.remove(alias)
                        just_imports.remove("as")
                        just_imports.remove(module)
                        if module == alias and config.remove_redundant_aliases:
                            yield identified_import(module)
                        else:
                            yield identified_import(module, alias=alias)

            if just_imports:
                if type_of_import == "from":
                    module = just_imports.pop(0)
                    for attribute in just_imports:
                        yield identified_import(module, attribute)
                else:
                    for module in just_imports:
                        yield identified_import(module)
