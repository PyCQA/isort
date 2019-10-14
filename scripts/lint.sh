#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy --ignore-missing-imports isort/
poetry run isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --use-parentheses --line-width=100 --recursive --check --diff --recursive isort/ tests/
poetry run black --check -l 100 isort/ tests/
poetry run flake8 isort/ tests/ --max-line 100 --ignore F403,F401,W503,E203
poetry run safety check
poetry run bandit -r isort/
