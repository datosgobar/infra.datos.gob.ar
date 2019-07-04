#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running pylint"
docker exec -it infra_django_1 pylint --load-plugins pylint_django infra/
echo "pylint OK :)"


