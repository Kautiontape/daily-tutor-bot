#!/bin/bash
set -e

echo "========================================="
echo "Daily Tutor Bot - Automated Deployment"
echo "========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Working directory: $SCRIPT_DIR"
echo ""

# Pull latest changes
echo "📥 Pulling latest changes from main..."
git pull origin main
echo "✅ Git pull completed"
echo ""

# Stop containers
echo "🛑 Stopping existing containers..."
docker-compose down
echo "✅ Containers stopped"
echo ""

# Rebuild images
echo "🔨 Building new images..."
docker-compose build --no-cache
echo "✅ Build completed"
echo ""

# Start containers
echo "🚀 Starting containers..."
docker-compose up -d
echo "✅ Containers started"
echo ""

# Wait for healthcheck
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check container status
echo "📊 Container status:"
docker-compose ps
echo ""

# Show recent logs
echo "📋 Recent logs:"
docker-compose logs --tail=20
echo ""

echo "========================================="
echo "✅ Deployment completed successfully!"
echo "========================================="
