#!/bin/bash

echo "🚀 Price Monitor API - Quick Start"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Services are up and running!"
echo ""
echo "📚 Available URLs:"
echo "   - API:            http://localhost:8000"
echo "   - API Docs:       http://localhost:8000/docs"
echo "   - ReDoc:          http://localhost:8000/redoc"
echo "   - Flower (Tasks): http://localhost:5555"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs:      docker-compose logs -f"
echo "   - Stop services:  docker-compose down"
echo "   - Run tests:      docker-compose exec api pytest"
echo ""
echo "📖 Check README.md for detailed usage instructions"
