#!/bin/sh
set -e

if [ ! -f "manage.py" ]; then
    echo "ERROR: manage.py not found in /app. Refusing to scaffold or mutate source."
    exit 1
fi

echo "📦 Applying migrations..."
i=1
until python manage.py migrate --noinput; do
    if [ "$i" -ge 30 ]; then
        echo "ERROR: migrations failed after ${i} attempts."
        exit 1
    fi
    echo "Database not ready yet, retrying migrations in 2s (attempt ${i}/30)..."
    i=$((i + 1))
    sleep 2
done

if [ "$#" -gt 0 ]; then
    echo "🚀 Starting backend with custom command: $*"
    exec "$@"
fi

echo "🚀 Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
