#!/bin/bash
set -euxo pipefail

./scripts/lint.sh
poetry run pytest tests/unit/ -s --cov=isort/ --cov-report=term-missing ${@-} --ignore=tests/unit/test_deprecated_finders.py
poetry run coverage html
