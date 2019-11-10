#!/bin/bash
set -euxo pipefail

poetry run isort --profile hug isort/ tests/
poetry run black isort/ tests/ -l 100
