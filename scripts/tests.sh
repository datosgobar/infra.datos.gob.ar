#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running py.test"
env PYTHONDONTWRITEBYTECODE=1 py.test -v $@
echo "py.test OK :)"


