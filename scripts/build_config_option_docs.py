#! /bin/env python
import os
from typing import Any, Generator, Iterable, Type

from isort._future import dataclass, field
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
HEADER = """Configuration options for isort
========

As a code formatter isort has opinions. However, it also allows you to have your own. If your opinions disagree with those of isort,
isort will disagree but commit to your way of formatting. To enable this, isort exposes a plethora of options to specify
how you want your imports sorted, organized, and formatted.

"""
parser = _build_arg_parser()


@dataclass(frozen=True)
class ConfigOption:
    name: str
    type: Type = str
    default: Any = ""
    config_name: str = "**Not Supported**"
    cli_options: Iterable[str] = ("**Not Supported**",)
    description: str = "**No Description**"

    def __str__(self):
        if self.name in IGNORED:
            return ""

        cli_options = "\n - ".join(self.cli_options)
        return f"""
## {human(self.name)}
{self.description}

**Type:** {human(self.type.__name__)}{MD_NEWLINE}
**Default:** `{self.default}`{MD_NEWLINE}
**Python & Config File Name:** {self.config_name}{MD_NEWLINE}
**CLI Flags:**

 - {cli_options}
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

        yield ConfigOption(
            name=name, type=type(default), default=default, config_name=name, **extra_kwargs
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
            name=name, default=cli.default, cli_options=cli.option_strings, **extra_kwargs
        )


def document_text() -> str:
    return f"{HEADER}{''.join(str(config_option) for config_option in config_options())}"


def write_document():
    with open(OUTPUT_FILE, "w") as output_file:
        output_file.write(document_text())


if __name__ == "__main__":
    write_document()
