#!/bin/bash

set -o errexit
set -o nounset

readonly cmd="$*"

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

exec $cmd