#!/bin/bash
set -euxo pipefail

poetry run coverage run --parallel -m pytest tests/unit/ --ignore=tests/unit/test_deprecated_finders.py
poetry run coverage html
