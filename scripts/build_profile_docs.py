#! /bin/env python
import os
from typing import Any, Dict, Generator, Iterable, Type

from isort.profiles import profiles

OUTPUT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docs/configuration/profiles.md")
)

HEADER = """Built-in Profile for isort
========

The following profiles are built into isort to allow easy interoperability with
common projects and code styles.

To use any of the listed profiles, use `isort --profile PROFILE_NAME` from the command line, or `profile=PROFILE_NAME` in your configuration file.

"""


def format_profile(profile_name: str, profile: Dict[str, Any]) -> str:
    options = "\n".join(f" - **{name}**: `{repr(value)}`" for name, value in profile.items())
    return f"""
#{profile_name}

{profile.get('description', '')}
{options}
"""


def document_text() -> str:
    return f"{HEADER}{''.join(format_profile(profile_name,  profile) for profile_name, profile in profiles.items())}"


def write_document():
    with open(OUTPUT_FILE, "w") as output_file:
        output_file.write(document_text())


if __name__ == "__main__":
    write_document()
