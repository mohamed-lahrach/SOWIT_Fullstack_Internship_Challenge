#!/bin/sh
set -e

# 1. CHECK FOR SOURCE CODE
if [ ! -f "manage.py" ]; then
    echo " "
    echo "🛑 CRITICAL ERROR: 'manage.py' not found in /app"
    echo "----------------------------------------------------------------"
    echo "   The container has started in IDLE MODE to allow scaffolding."
    echo " "
    echo "   TO INITIALIZE A NEW PROJECT:"
    echo "   Run: make scaffold-project"
    echo " "
    echo "----------------------------------------------------------------"
    
    # Keep the container alive but do nothing (tail /dev/null)
    # This allows 'docker compose exec' to work.
    tail -f /dev/null
fi

# 2. WAIT FOR DATABASE
echo "🔌 Waiting for Database..."
# Simple connection check loop (requires netcat or python check, usually python is safer in slim images)
until python -c "import socket; s = socket.socket(); s.connect(('db', 5432))" 2>/dev/null; do
    echo "   ... DB not ready. Sleeping 2s."
    sleep 2
done
echo "✅ Database is up."

# 3. RUNTIME COMMANDS
echo "📦 Applying migrations..."
python manage.py migrate --noinput

echo "🚀 Starting Django Server..."
exec python manage.py runserver 0.0.0.0:8000