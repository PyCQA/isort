#!/usr/bin/env bash
set -euxo pipefail

uv run isort --profile hug isort/ tests/ scripts/
uv run isort --profile hug example_*/
uv run black isort/ tests/ scripts/
uv run black example_*/
