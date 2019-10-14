#!/bin/bash
set -euxo pipefail

version=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')
parsedVersion=$(echo "${version//./}")

if [[ "$parsedVersion" -lt "360" ]]
then
    echo "WARNING: Some linters have been skipped. Run against 3.6+ for full set of linters to run against the project!"
else
    poetry run cruft check
    poetry run mypy --ignore-missing-imports isort/
    poetry run black --check -l 100 isort/ tests/
fi

poetry run isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --use-parentheses --line-width=100 --recursive --check --diff --recursive isort/ tests/
poetry run flake8 isort/ tests/ --max-line 100 --ignore F403,F401,W503,E203
poetry run safety check
poetry run bandit -r isort/
