#!/bin/bash
set -euxo pipefail

cd example_isort_formatting_plugin && poetry install
cd ..
poetry run pytest tests/unit/ -s --cov=isort/ --cov-report=term-missing ${@-} --ignore=tests/unit/test_deprecated_finders.py
poetry run coverage html
