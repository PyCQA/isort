#!/bin/bash
set -euxo pipefail

poetry run pytest tests/integration/ -s
