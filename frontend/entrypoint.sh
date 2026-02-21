#!/bin/sh
set -e

# 1. CHECK FOR SOURCE CODE
if [ ! -f "package.json" ]; then
    echo " "
    echo "🛑 CRITICAL ERROR: 'package.json' not found in /app"
    echo "----------------------------------------------------------------"
    echo "   The container has started in IDLE MODE to allow scaffolding."
    echo " "
    echo "   TO INITIALIZE A NEW FRONTEND:"
    echo "   Run: make scaffold-frontend"
    echo " "
    echo "----------------------------------------------------------------"
    
    # Keep container alive for 'exec' commands
    tail -f /dev/null
fi

# 2. INSTALL DEPENDENCIES
# We run this on every startup to ensure the container matches package.json
echo "📦 Checking dependencies..."
if [ ! -d "node_modules" ] || [ ! -x "node_modules/.bin/vite" ]; then
    echo "   Installing modules (or repairing incomplete install)..."
    npm install
else
    echo "   Node modules found. (Run 'npm ci' manually if strictly needed)"
fi

# 3. START SERVER
echo "🚀 Starting Vite Dev Server..."
exec npm run dev -- --host
