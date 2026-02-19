#!/bin/sh

if [ ! -f "package.json" ]; then
    echo "🚀 Scaffolding Vite + React project..."
    mkdir -p /tmp/vite-temp
    cd /tmp/vite-temp
    create-vite . --template react
    cp -r . /app/
    cd /app
    npm install
fi

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "✅ Starting dev server..."
exec npm run dev -- --host