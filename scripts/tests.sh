#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running py.test"
docker-compose exec django env PYTHONDONTWRITEBYTECODE=1 DJANGO_SETTINGS_MODULE=conf.settings.testing py.test -v -p no:cacheprovider $@
echo "py.test OK :)"


