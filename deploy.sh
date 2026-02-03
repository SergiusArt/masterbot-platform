#!/bin/bash
set -e

cd /root/masterbot-platform

echo "=== Pulling latest code ==="
git pull origin main

echo "=== Building frontend ==="
cd miniapp_frontend
npm install --silent
npm run build
cd ..

echo "=== Rebuilding and restarting containers ==="
docker compose up -d --build

echo "=== Deploy complete ==="
