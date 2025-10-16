#!/usr/bin/env bash
set -euxo pipefail

uv run coverage run --parallel -m pytest tests/unit/ -s --ignore=tests/unit/test_deprecated_finders.py
uv run coverage combine
uv run coverage report
uv run coverage xml
