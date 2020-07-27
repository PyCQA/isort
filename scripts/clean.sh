#!/bin/bash
set -euxo pipefail

poetry run isort --profile hug isort/ tests/ scripts/
poetry run isort --profile hug example_isort_formatting_plugin/
poetry run black isort/ tests/ scripts/
poetry run black example_isort_formatting_plugin/
