#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running flake8"
docker exec -it infra_django_1 flake8
echo "flake8 OK :)"


