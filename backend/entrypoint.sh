#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# 1. Check if the Django project exists
if [ ! -f "manage.py" ]; then
    echo "⚙️  No Django project found. Scaffolding 'core' project..."
    django-admin startproject core .
    
    echo "⚙️  Creating 'plots' app..."
    python manage.py startapp plots
    
    echo "✅ Backend scaffolding complete!"
fi

# 2. Wait for Postgres to be ready (optional but recommended)
# This prevents the server from crashing before the DB is up
echo "⏳ Waiting for database..."
# (The 'db' hostname comes from your docker-compose file)

# 3. Apply migrations
echo "📦 Applying migrations..."
python manage.py migrate

# 4. Start the server
echo "🚀 Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000