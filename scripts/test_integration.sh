#!/usr/bin/env bash
set -euxo pipefail

uv run pytest tests/integration/ -s
