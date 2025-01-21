#! /bin/env python
import dataclasses
import os
from textwrap import dedent
from typing import Any, Dict, Generator, Iterable, Optional, Type

from isort.main import _build_arg_parser
from isort.settings import _DEFAULT_SETTINGS as config

OUTPUT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docs/configuration/options.md")
)
MD_NEWLINE = "  "
HUMAN_NAME = {
    "py_version": "Python Version",
    "vn": "Version Number",
    "str": "String",
    "frozenset": "List of Strings",
    "tuple": "List of Strings",
}
CONFIG_DEFAULTS = {"False": "false", "True": "true", "None": ""}
DESCRIPTIONS = {}
IGNORED = {"source", "help", "sources", "directory"}
COLUMNS = ["Name", "Type", "Default", "Python / Config file", "CLI", "Description"]
HEADER = """# Configuration options for isort

As a code formatter isort has opinions. However, it also allows you to have your own. If your opinions disagree with those of isort,
isort will disagree but commit to your way of formatting. To enable this, isort exposes a plethora of options to specify
how you want your imports sorted, organized, and formatted.

Too busy to build your perfect isort configuration? For curated common configurations, see isort's [built-in
profiles](https://pycqa.github.io/isort/docs/configuration/profiles.html).
"""
parser = _build_arg_parser()


@dataclasses.dataclass
class Example:
    section_complete: str = ""
    cfg: str = ""
    pyproject_toml: str = ""
    cli: str = ""

    def __post_init__(self):
        if self.cfg or self.pyproject_toml or self.cli:
            if self.cfg:
                cfg = dedent(self.cfg).lstrip()
                self.cfg = (
                    dedent(
                        """
                    ### Example `.isort.cfg`

                    ```
                    [settings]
                    {cfg}
                    ```
                    """
                    )
                    .format(cfg=cfg)
                    .lstrip()
                )

            if self.pyproject_toml:
                pyproject_toml = dedent(self.pyproject_toml).lstrip()
                self.pyproject_toml = (
                    dedent(
                        """
                    ### Example `pyproject.toml`

                    ```
                    [tool.isort]
                    {pyproject_toml}
                    ```
                    """
                    )
                    .format(pyproject_toml=pyproject_toml)
                    .lstrip()
                )

            if self.cli:
                cli = dedent(self.cli).lstrip()
                self.cli = (
                    dedent(
                        """
                    ### Example cli usage

                    `{cli}`
                    """
                    )
                    .format(cli=cli)
                    .lstrip()
                )

            sections = [s for s in [self.cfg, self.pyproject_toml, self.cli] if s]
            sections_str = "\n".join(sections)
            self.section_complete = f"""**Examples:**

{sections_str}"""

        else:
            self.section_complete = ""

    def __str__(self):
        return self.section_complete


description_mapping: Dict[str, str]
description_mapping = {
    "length_sort_sections": "Sort the given sections by length",
    "forced_separate": "Force certain sub modules to show separately",
    "sections": "What sections isort should display imports for and in what order",
    "known_other": "known_OTHER is how imports of custom sections are defined. "
    "OTHER is a placeholder for the custom section name.",
    "comment_prefix": "Allows customizing how isort prefixes comments that it adds or modifies on import lines"
    "Generally `  #` (two spaces before a pound symbol) is use, though one space is also common.",
    "lines_before_imports": "The number of blank lines to place before imports. -1 for automatic determination",
    "lines_after_imports": "The number of blank lines to place after imports. -1 for automatic determination",
    "lines_between_sections": "The number of lines to place between sections",
    "lines_between_types": "The number of lines to place between direct and from imports",
    "lexicographical": "Lexicographical order is strictly alphabetical order. "
    "For example by default isort will sort `1, 10, 2` into `1, 2, 10` - but with "
    "lexicographical sorting enabled it will remain `1, 10, 2`.",
    "ignore_comments": "If enabled, isort will strip comments that exist within import lines.",
    "constants": "An override list of tokens to always recognize as a CONSTANT for order_by_type regardless of casing.",
    "classes": "An override list of tokens to always recognize as a Class for order_by_type regardless of casing.",
    "variables": "An override list of tokens to always recognize as a var for order_by_type regardless of casing.",
    "auto_identify_namespace_packages": "Automatically determine local namespace packages, generally by lack of any src files before a src containing directory.",
    "namespace_packages": "Manually specify one or more namespace packages.",
    "follow_links": "If `True` isort will follow symbolic links when doing recursive sorting.",
    "git_ignore": "If `True` isort will honor ignores within locally defined .git_ignore files.",
    "formatting_function": "The fully qualified Python path of a function to apply to format code sorted by isort.",
    "group_by_package": "If `True` isort will automatically create section groups by the top-level package they come from.",
    "indented_import_headings": "If `True` isort will apply import headings to indented imports the same way it does unindented ones.",
    "import_headings": "A mapping of import sections to import heading comments that should show above them.",
    "import_footers": "A mapping of import sections to import footer comments that should show below them.",
}

example_mapping: Dict[str, Example]
example_mapping = {
    "skip": Example(
        cfg="""
skip=.gitignore,.dockerignore""",
        pyproject_toml="""
skip = [".gitignore", ".dockerignore"]
""",
    ),
    "extend_skip": Example(
        cfg="""
extend_skip=.md,.json""",
        pyproject_toml="""
extend_skip = [".md", ".json"]
""",
    ),
    "skip_glob": Example(
        cfg="""
skip_glob=docs/*
""",
        pyproject_toml="""
skip_glob = ["docs/*"]
""",
    ),
    "extend_skip_glob": Example(
        cfg="""
extend_skip_glob=my_*_module.py,test/*
""",
        pyproject_toml="""
extend_skip_glob = ["my_*_module.py", "test/*"]
""",
    ),
    "known_third_party": Example(
        cfg="""
known_third_party=my_module1,my_module2
""",
        pyproject_toml="""
known_third_party = ["my_module1", "my_module2"]
""",
    ),
    "known_first_party": Example(
        cfg="""
known_first_party=my_module1,my_module2
""",
        pyproject_toml="""
known_first_party = ["my_module1", "my_module2"]
""",
    ),
    "known_local_folder": Example(
        cfg="""
known_local_folder=my_module1,my_module2
""",
        pyproject_toml="""
known_local_folder = ["my_module1", "my_module2"]
""",
    ),
    "known_standard_library": Example(
        cfg="""
known_standard_library=my_module1,my_module2
""",
        pyproject_toml="""
known_standard_library = ["my_module1", "my_module2"]
""",
    ),
    "extra_standard_library": Example(
        cfg="""
extra_standard_library=my_module1,my_module2
""",
        pyproject_toml="""
extra_standard_library = ["my_module1", "my_module2"]
""",
    ),
    "forced_separate": Example(
        cfg="""
forced_separate=glob_exp1,glob_exp2
""",
        pyproject_toml="""
forced_separate = ["glob_exp1", "glob_exp2"]
""",
    ),
    "length_sort_sections": Example(
        cfg="""
length_sort_sections=future,stdlib
""",
        pyproject_toml="""
length_sort_sections = ["future", "stdlib"]
""",
    ),
    "add_imports": Example(
        cfg="""
add_imports=import os,import json
""",
        pyproject_toml="""
add_imports = ["import os", "import json"]
""",
    ),
    "remove_imports": Example(
        cfg="""
remove_imports=os,json
""",
        pyproject_toml="""
remove_imports = ["os", "json"]
""",
    ),
    "single_line_exclusions": Example(
        cfg="""
single_line_exclusions=os,json
""",
        pyproject_toml="""
single_line_exclusions = ["os", "json"]
""",
    ),
    "no_lines_before": Example(
        cfg="""
no_lines_before=future,stdlib
""",
        pyproject_toml="""
no_lines_before = ["future", "stdlib"]
""",
    ),
    "src_paths": Example(
        cfg="""
src_paths = src,tests
""",
        pyproject_toml="""
src_paths = ["src", "tests"]
""",
    ),
    "treat_comments_as_code": Example(
        cfg="""
treat_comments_as_code = # my comment 1, # my other comment
""",
        pyproject_toml="""
treat_comments_as_code = ["# my comment 1", "# my other comment"]
""",
    ),
    "supported_extensions": Example(
        cfg="""
supported_extensions=pyw,ext
""",
        pyproject_toml="""
supported_extensions = ["pyw", "ext"]
""",
    ),
    "blocked_extensions": Example(
        cfg="""
blocked_extensions=pyw,pyc
""",
        pyproject_toml="""
blocked_extensions = ["pyw", "pyc"]
""",
    ),
    "known_other": Example(
        cfg="""
        sections=FUTURE,STDLIB,THIRDPARTY,AIRFLOW,FIRSTPARTY,LOCALFOLDER
        known_airflow=airflow""",
        pyproject_toml="""
            sections = ['FUTURE', 'STDLIB', 'THIRDPARTY', 'AIRFLOW', 'FIRSTPARTY', 'LOCALFOLDER']
            known_airflow = ['airflow']""",
    ),
    "multi_line_output": Example(cfg="multi_line_output=3", pyproject_toml="multi_line_output = 3"),
    "show_version": Example(cli="isort --version"),
    "py_version": Example(
        cli="isort --py 39",
        pyproject_toml="""
py_version=39
""",
        cfg="""
py_version=39
""",
    ),
}


@dataclasses.dataclass
class ConfigOption:
    name: str
    type: Type = str
    default: Any = ""
    config_name: str = "**Not Supported**"
    cli_options: Iterable[str] = (" **Not Supported**",)
    description: str = "**No Description**"
    example: Optional[Example] = None

    def __str__(self):
        if self.name in IGNORED:
            return ""

        if self.cli_options == (" **Not Supported**",):
            cli_options = self.cli_options[0]
        else:
            cli_options = "\n\n- " + "\n- ".join(self.cli_options)

        # new line if example otherwise nothing
        example = f"\n{self.example}" if self.example else ""
        return f"""
## {human(self.name)}

{self.description}

**Type:** {human(self.type.__name__)}{MD_NEWLINE}
**Default:** `{str(self.default) or " "}`{MD_NEWLINE}
**Config default:** `{config_default(self.default) or " "}`{MD_NEWLINE}
**Python & Config File Name:** {self.config_name}{MD_NEWLINE}
**CLI Flags:**{cli_options}
{example}"""


def config_default(default: Any) -> str:
    if isinstance(default, (frozenset, tuple)):
        default = list(default)
    default_str = str(default)
    if default_str in CONFIG_DEFAULTS:
        return CONFIG_DEFAULTS[default_str]

    if default_str.startswith("py"):
        return default_str[2:]
    return default_str


def human(name: str) -> str:
    if name in HUMAN_NAME:
        return HUMAN_NAME[name]

    return " ".join(
        part if part in ("of",) else part.capitalize() for part in name.replace("-", "_").split("_")
    )


def config_options() -> Generator[ConfigOption, None, None]:
    cli_actions = {action.dest: action for action in parser._actions}
    for name, default in config.items():
        extra_kwargs = {}
        description: Optional[str] = description_mapping.get(name, None)

        cli = cli_actions.pop(name, None)
        if cli:
            extra_kwargs["cli_options"] = cli.option_strings
            if cli.help and not description:
                description = cli.help

        default_display = default
        if isinstance(default, (set, frozenset)) and len(default) > 0:
            default_display = tuple(sorted(default))

        # todo: refactor place for example params
        # needs to integrate with isort/settings/_Config
        # needs to integrate with isort/main/_build_arg_parser
        yield ConfigOption(
            name=name,
            type=type(default),
            default=default_display,
            config_name=name,
            description=description or "**No Description**",
            example=example_mapping.get(name, None),
            **extra_kwargs,
        )

    for name, cli in cli_actions.items():
        extra_kwargs = {}
        description: Optional[str] = description_mapping.get(name, None)
        if cli.type:
            extra_kwargs["type"] = cli.type
        elif cli.default is not None:
            extra_kwargs["type"] = type(cli.default)

        if cli.help and not description:
            description = cli.help

        yield ConfigOption(
            name=name,
            default=cli.default,
            cli_options=cli.option_strings,
            example=example_mapping.get(name, None),
            description=description or "**No Description**",
            **extra_kwargs,
        )


def document_text() -> str:
    return f"{HEADER}{''.join(str(config_option) for config_option in config_options())}"


def write_document():
    with open(OUTPUT_FILE, "w") as output_file:
        output_file.write(document_text())


if __name__ == "__main__":
    write_document()
