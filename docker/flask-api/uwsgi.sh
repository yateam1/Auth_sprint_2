#!/usr/bin/env sh

set -o errexit
set -o nounset

export FLASK_ENV

flask db upgrade -d /app/migrations/


/usr/local/bin/uwsgi --master \
  --single-interpreter \
  --workers 4 \
  --gevent 100 \
  --protocol http \
  --socket 0.0.0.0:5000 \
  --module app.patched:application
