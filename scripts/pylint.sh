#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running pylint"
docker-compose exec django pylint --load-plugins pylint_django infra/
echo "pylint OK :)"


