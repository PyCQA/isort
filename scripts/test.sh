#!/usr/bin/env bash
set -euxo pipefail

uv run coverage run --parallel -m pytest tests/unit/ -s
uv run coverage combine
uv run coverage report
uv run coverage xml
