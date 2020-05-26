#! /bin/env python
import os
from typing import Generator

from isort.main import _build_arg_parser
from isort.settings import _DEFAULT_SETTINGS as config

OUTPUT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docs/configuration/options.md")
)
HUMAN_NAME = {"py_version": "Python Version", "vn": "Version Number"}
DESCRIPTIONS = {}
IGNORED = {"source", "help"}
COLUMNS = ["Name", "Type", "Default", "Python / Config file", "CLI", "Description"]
HEADER = f"""Configuration options for isort
========

As a code formatter isort has opinions. However, it also allows you to also have your own. If your opinions disagree with those of isort,
isort will disagree but commit to your way of formatting. To enable this, isort exposes a plethora of options to specify
how you want your imports sorted.

| {' | '.join(COLUMNS)} |
"""
parser = _build_arg_parser()


def human(name: str) -> str:
    if name in HUMAN_NAME:
        return HUMAN_NAME[name]

    return " ".join([part.capitalize() for part in name.replace("-", "_").split("_")])


def config_options() -> Generator[str, None, None]:
    cli_actions = {}
    for action in parser._actions:
        cli_actions[action.dest] = action

    for name, default in config.items():
        if name in IGNORED:
            continue

        description = DESCRIPTIONS.get(name, "")

        cli = cli_actions.pop(name, None)
        if cli:
            cli_options = ",".join(cli.option_strings)
            description = description or cli.help or ""
        else:
            cli_options = "**Not Supported**"
        description = description.replace("\n", " ")

        yield f"|{human(name)}|{human(type(default).__name__)}|{default}|{name}|{cli_options}|{description}|\n"

    for name, cli in cli_actions.items():
        if name in IGNORED:
            continue

        if cli.type:
            type_name = human(cli.type.__name__)
        elif cli.default is not None:
            type_name = human(type(cli.default).__name__)
        else:
            type_name = "*Not Typed*"

        description = (DESCRIPTIONS.get(name, cli.help) or "").replace("\n", " ")
        yield f"|{human(name)}|{type_name}|{cli.default}|**Not Supported**|{','.join(cli.option_strings)}|{description}|\n"


def document_text() -> str:
    return f"{HEADER}{''.join(config_options())}"


def write_document():
    with open(OUTPUT_FILE, "w") as output_file:
        output_file.write(document_text())


if __name__ == "__main__":
    write_document()
