#!/bin/sh

set -e

if [ ! -f "package.json" ]; then
    echo "ERROR: package.json not found in /app. Refusing to scaffold or mutate source."
    exit 1
fi

install_deps() {
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
}

deps_ok() {
    npm ls >/dev/null 2>&1
}

if [ ! -x "node_modules/.bin/vite" ]; then
    echo "📦 Installing dependencies..."
    install_deps
fi

if [ ! -x "node_modules/.bin/vite" ] || ! deps_ok; then
    echo "⚠️  Dependency state is inconsistent. Reinstalling from scratch..."
    # node_modules is a volume mount; remove its contents, not the mountpoint.
    if [ -d "node_modules" ]; then
        find node_modules -mindepth 1 -exec rm -rf {} +
    fi
    install_deps
fi

if [ ! -x "node_modules/.bin/vite" ] || ! deps_ok; then
    echo "ERROR: vite binary still missing after reinstall."
    exit 1
fi

echo "✅ Starting dev server..."
exec npm run dev -- --host
