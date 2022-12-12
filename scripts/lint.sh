#!/bin/bash
set -euxo pipefail

# TODO: reneable cruft when it takes Python restriction
#poetry run cruft check
poetry run mypy -p isort -p tests
poetry run black --target-version py37 --check .
poetry run isort --profile hug --check --diff isort/ tests/
poetry run isort --profile hug --check --diff example_*/
poetry run flake8 isort/ tests/
poetry run safety check -i 47794 -i 51457
poetry run bandit -r isort/ -x isort/_vendored
