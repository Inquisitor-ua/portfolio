#!/bin/sh
# Container startup: wait for the database, apply migrations, collect static
# files, optionally create a superuser, then run the given command (gunicorn).
set -e

if [ -z "$SECRET_KEY" ]; then
    echo "SECRET_KEY is not set. Refusing to start." >&2
    exit 1
fi

if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for the database..."
    python <<'PYEOF'
import os
import sys
import time

import dj_database_url
import psycopg

config = dj_database_url.parse(os.environ["DATABASE_URL"])

for attempt in range(30):
    try:
        psycopg.connect(
            dbname=config["NAME"],
            user=config["USER"],
            password=config["PASSWORD"],
            host=config["HOST"],
            port=config["PORT"],
        ).close()
        break
    except psycopg.OperationalError:
        time.sleep(1)
else:
    sys.exit("Database never became available")
PYEOF
fi

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Ensuring the configured superuser exists..."
    python manage.py createsuperuser --noinput || true
fi

exec "$@"
