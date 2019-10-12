#!/bin/bash -xe

./scripts/lint.sh
poetry run pytest -s --cov={{cookiecutter.project_name}}/ --cov=tests --cov-report=term-missing ${@} --cov-report html
