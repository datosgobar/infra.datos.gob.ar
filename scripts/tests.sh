#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running py.test"
env DJANGO_SETTINGS_MODULE=conf.settings.testing py.test -v $@
echo "py.test OK :)"


