#!/bin/bash
set -euxo pipefail

poetry run isort --profile hug isort/ tests/ scripts/
poetry run black isort/ tests/ scripts/ -l 100
