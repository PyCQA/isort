#!/bin/bash
set -euxo pipefail

uv run cruft check
uv run mypy -p isort -p tests
uv run black --target-version py39 --check .
uv run isort --profile hug --check --diff isort/ tests/
uv run isort --profile hug --check --diff example_*/
uv run --with=Flake8-pyproject flake8 isort/ tests/
uv run ruff check
uv run bandit -r isort/ -x isort/_vendored
