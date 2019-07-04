#!/usr/bin/env bash
set -e
DIR=$(dirname "$0")
cd ${DIR}/..

echo "Running flake8"
docker-compose exec django flake8
echo "flake8 OK :)"


