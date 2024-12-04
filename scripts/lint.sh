#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy -p isort -p tests
poetry run black --target-version py38 .
poetry run isort --profile hug --check --diff isort/ tests/
poetry run isort --profile hug --check --diff example_*/
poetry run flake8 isort/ tests/
 # 51457: https://github.com/tiangolo/typer/discussions/674
 # 72715: https://github.com/timothycrosley/portray/issues/95
poetry run safety check -i 72715 -i 51457 -i 59587
poetry run bandit -r isort/ -x isort/_vendored
