#!/bin/bash
set -euxo pipefail


poetry run cruft check
poetry run mypy --ignore-missing-imports isort/
poetry run black --check -l 100 isort/ tests/
poetry run isort --profile hug --check --diff isort/ tests/
poetry run flake8 isort/ tests/ --max-line 100 --ignore F403,F401,W503,E203
poetry run safety check
poetry run bandit -r isort/
