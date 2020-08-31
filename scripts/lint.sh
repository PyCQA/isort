#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy --ignore-missing-imports isort/
poetry run black --check isort/ tests/
poetry run black --check example_isort_formatting_plugin/
poetry run isort --profile hug --check --diff isort/ tests/
poetry run isort --profile hug --check --diff example_isort_formatting_plugin/
poetry run flake8 isort/ tests/
poetry run safety check
poetry run bandit -r isort/
