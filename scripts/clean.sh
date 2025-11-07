#!/usr/bin/env bash
set -euxo pipefail

uv run isort --profile hug isort/ tests/ scripts/
uv run isort --profile hug example_*/
uv run ruff format isort/ tests/ scripts/
uv run ruff format example_*/
