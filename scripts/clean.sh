#!/bin/bash
set -euxo pipefail

poetry run isort --profile hug isort/ tests/ scripts/
poetry run isort --profile hug example_*/
poetry run black isort/ tests/ scripts/
poetry run black example_*/
