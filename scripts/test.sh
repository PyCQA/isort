#!/bin/bash -xe

./scripts/lint.sh
poetry run pytest -s --cov=isort/ --cov=test_isort.py --cov-report=term-missing ${@} --cov-report html
