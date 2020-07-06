#! /bin/env python
import os
import textwrap
from typing import Any, Generator, Iterable, Type

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

========

As a code formatter isort has opinions. However, it also allows you to have your own. If your opinions disagree with those of isort,
isort will disagree but commit to your way of formatting. To enable this, isort exposes a plethora of options to specify
how you want your imports sorted, organized, and formatted.

Too busy to build your perfect isort configuration? For curated common configurations, see isort's [built-in profiles](https://timothycrosley.github.io/isort/docs/configuration/profiles/).
"""
parser = _build_arg_parser()


@dataclass
class ConfigOption:
    name: str
    type: Type = str
    default: Any = ""
    config_name: str = "**Not Supported**"
    cli_options: Iterable[str] = ("**Not Supported**",)
    description: str = "**No Description**"
    example_section: str = ""
    example_cfg: str = ""
    example_pyproject_toml: str = ""
    example_cli: str = ""

    def __post_init__(self):
        if self.example_cfg == "" and self.example_pyproject_toml == "" and self.example_cli == "":
            self.example_section = "**No Examples**"
        else:
            if self.example_cfg == "":
                self.example_cfg = "No example `.isort.cfg`"
            else:
                self.example_cfg = textwrap.dedent(
                    f"""
                    ### Example `.isort.cfg`

                    ```
                    {self.example_cfg}
                    ```
                    """
                )

            if self.example_pyproject_toml == "":
                self.example_pyproject_toml = "No example pyproject.toml"
            else:
                self.example_pyproject_toml = textwrap.dedent(
                    f"""
                    ### Example `pyproject.toml`

                    ```
                    {self.example_pyproject_toml}
                    ```
                    """
                )
                print(self.example_pyproject_toml)

            if self.example_cli == "":
                self.example_cli = "No example cli usage"
            else:
                self.example_cli = textwrap.dedent(
                    f"""
                    ### Example cli usage
                    `{self.example_cli}`
                    """
                )

            self.example_section = f"""**Examples:**

{self.example_cfg}
{self.example_pyproject_toml}
{self.example_cli}"""

    def __str__(self):
        if self.name in IGNORED:
            return ""

        cli_options = "\n- ".join(self.cli_options)
        return f"""
## {human(self.name)}

{self.description}

**Type:** {human(self.type.__name__)}{MD_NEWLINE}
**Default:** `{self.default}`{MD_NEWLINE}
**Python & Config File Name:** {self.config_name}{MD_NEWLINE}
**CLI Flags:**

- {cli_options}

{self.example_section}
"""


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
        if name != "known_other":
            yield ConfigOption(
                name=name,
                type=type(default),
                default=default_display,
                config_name=name,
                **extra_kwargs,
            )
        else:
            yield ConfigOption(
                name=name,
                type=type(default),
                default=default_display,
                config_name=name,
                example_pyproject_toml=textwrap.dedent(
                    """[tool.isort]
                    sections = ['FUTURE', 'STDLIB', 'THIRDPARTY', 'AIRFLOW', 'FIRSTPARTY', 'LOCALFOLDER']
                    known_airflow = ['airflow']"""
                ),
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
            name=name, default=cli.default, cli_options=cli.option_strings, **extra_kwargs,
        )


def document_text() -> str:
    return f"{HEADER}{''.join(str(config_option) for config_option in config_options())}"


def write_document():
    with open(OUTPUT_FILE, "w") as output_file:
        output_file.write(document_text())


if __name__ == "__main__":
    write_document()
