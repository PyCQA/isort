#!/bin/bash
set -euxo pipefail

poetry run coverage run --parallel -m pytest tests/unit/ -s --ignore=tests/unit/test_deprecated_finders.py
poetry run coverage combine
poetry run coverage report
poetry run coverage xml
