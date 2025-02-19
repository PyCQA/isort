#!/bin/bash
set -euxo pipefail

uv run cruft check
uv run mypy -p isort -p tests
uv run black --target-version py39 --check .
uv run isort --profile hug --check --diff isort/ tests/
uv run isort --profile hug --check --diff example_*/
uv run --with=Flake8-pyproject flake8 isort/ tests/
uv run ruff check
 # 51457: https://github.com/tiangolo/typer/discussions/674
 # 72715: https://github.com/timothycrosley/portray/issues/95
uv run safety check -i 72715 -i 51457 -i 59587
uv run bandit -r isort/ -x isort/_vendored
