# isort

[![isort - isort your imports, so you don't have to.](https://raw.githubusercontent.com/pycqa/isort/main/art/logo_large.png)](https://pycqa.github.io/isort/)

[![PyPI version](https://badge.fury.io/py/isort.svg)](https://badge.fury.io/py/isort)
[![Python Version](https://img.shields.io/pypi/pyversions/isort)](https://pypi.org/project/isort/)
[![Code coverage Status](https://codecov.io/gh/pycqa/isort/branch/main/graph/badge.svg)](https://codecov.io/gh/pycqa/isort)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.org/project/isort/)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

isort your imports, so you don't have to.

isort is a Python utility / library to sort imports alphabetically and automatically separate into sections and by type. It provides a command line utility, Python library and [plugins for various editors](https://github.com/pycqa/isort/wiki/isort-Plugins) to quickly sort all your imports. It requires Python 3.10+ to run but supports formatting Python 2 code too.

- [Try isort now from your browser!](quick_start/0.-try.md)
- [Using black? See the isort and black compatibility guide.](configuration/black_compatibility.md)
- [isort has official support for pre-commit!](configuration/pre-commit.md)

![Example Usage](https://raw.github.com/pycqa/isort/main/example.gif)

## Quick Start

```bash
pip install isort
isort .
```

## Features

- Sorts imports alphabetically within sections
- Automatically separates imports into sections (stdlib, third-party, first-party)
- Supports many editors and CI tools via plugins
- Compatible with [black](configuration/black_compatibility.md) and [pre-commit](configuration/pre-commit.md)
- Highly configurable via [configuration options](configuration/options.md)
