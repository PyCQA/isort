#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy -p isort -p tests
poetry run black --target-version py38 --check .
poetry run isort --profile hug --check --diff isort/ tests/
poetry run isort --profile hug --check --diff example_*/
poetry run flake8 isort/ tests/
poetry run safety check -i 51457 -i 59587 -i 64484 # https://github.com/tiangolo/typer/discussions/674
poetry run bandit -r isort/ -x isort/_vendored
