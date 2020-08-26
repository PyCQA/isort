#! /bin/env python
import os
from textwrap import dedent
from typing import Any, Dict, Generator, Iterable, Optional, Type

from isort._future import dataclass
from isort.main import _build_arg_parser
from isort.settings import _DEFAULT_SETTINGS as config

OUTPUT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docs/configuration/options.md")
)
MD_NEWLINE = "  "
HUMAN_NAME = {"py_version": "Python Version", "vn": "Version Number", "str": "String"}
DESCRIPTIONS = {}
IGNORED = {"source", "help"}
COLUMNS = ["Name", "Type", "Default", "Python / Config file", "CLI", "Description"]
HEADER = """# Configuration options for isort

As a code formatter isort has opinions. However, it also allows you to have your own. If your opinions disagree with those of isort,
isort will disagree but commit to your way of formatting. To enable this, isort exposes a plethora of options to specify
how you want your imports sorted, organized, and formatted.

Too busy to build your perfect isort configuration? For curated common configurations, see isort's [built-in
profiles](https://pycqa.github.io/isort/docs/configuration/profiles/).
"""
parser = _build_arg_parser()


@dataclass
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


example_mapping: Dict[str, Example]
example_mapping = {
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
}


@dataclass
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
**Default:** `{self.default}`{MD_NEWLINE}
**Python & Config File Name:** {self.config_name}{MD_NEWLINE}
**CLI Flags:**{cli_options}
{example}"""


def human(name: str) -> str:
    if name in HUMAN_NAME:
        return HUMAN_NAME[name]

    return " ".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def config_options() -> Generator[ConfigOption, None, None]:
    cli_actions = {}
    for action in parser._actions:
        cli_actions[action.dest] = action

    for name, default in config.items():
        extra_kwargs = {}

        cli = cli_actions.pop(name, None)
        if cli:
            extra_kwargs["cli_options"] = cli.option_strings
            if cli.help:
                extra_kwargs["description"] = cli.help

        default_display = default
        if isinstance(default, (set, frozenset)) and len(default) > 0:
            default_display = tuple(i for i in sorted(default))

        # todo: refactor place for example params
        # needs to integrate with isort/settings/_Config
        # needs to integrate with isort/main/_build_arg_parser
        yield ConfigOption(
            name=name,
            type=type(default),
            default=default_display,
            config_name=name,
            example=example_mapping.get(name, None),
            **extra_kwargs,
        )

    for name, cli in cli_actions.items():
        extra_kwargs = {}
        if cli.type:
            extra_kwargs["type"] = cli.type
        elif cli.default is not None:
            extra_kwargs["type"] = type(cli.default)

        if cli.help:
            extra_kwargs["description"] = cli.help

        yield ConfigOption(
            name=name,
            default=cli.default,
            cli_options=cli.option_strings,
            example=example_mapping.get(name, None),
            **extra_kwargs,
        )


def document_text() -> str:
    return f"{HEADER}{''.join(str(config_option) for config_option in config_options())}"


def write_document():
    with open(OUTPUT_FILE, "w") as output_file:
        output_file.write(document_text())


if __name__ == "__main__":
    write_document()
