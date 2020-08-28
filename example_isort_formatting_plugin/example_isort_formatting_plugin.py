import black

import isort


def black_format_import_section(
    contents: str, extension: str, config: isort.settings.Config
) -> str:
    """Formats the given import section using black."""
    if extension.lower() not in ("pyi", "py"):
        return contents

    try:
        return black.format_file_contents(
            contents,
            fast=True,
            mode=black.FileMode(
                is_pyi=extension.lower() == "pyi",
                line_length=config.line_length,
            ),
        )
    except black.NothingChanged:
        return contents
