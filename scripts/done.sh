#!/bin/bash
set -euxo pipefail

./scripts/clean.sh
./scripts/test.sh
