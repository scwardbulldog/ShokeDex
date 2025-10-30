#!/bin/bash
# Post-create script for ShokeDex development environment
# This script runs after the container is created to set up the development environment

set -e

echo "🚀 Setting up ShokeDex development environment..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install black pylint flake8 mypy pytest

# Install system dependencies needed for pygame (if not already in image)
echo "📦 Installing system dependencies for pygame..."
sudo apt-get update
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev python3-setuptools python3-dev

# Create data directory if it doesn't exist
echo "📁 Creating data directory..."
mkdir -p data

# Initialize the database
echo "🗄️  Initializing database schema..."
python src/data/manage_db.py init || echo "⚠️  Database initialization failed or already completed"

# Show database stats
echo "📊 Database statistics:"
python src/data/manage_db.py stats || echo "⚠️  Could not retrieve database stats - check if database was initialized successfully"

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
python -m unittest discover tests -v || echo "⚠️  Some tests failed - check output above for details or run tests individually"

echo ""
echo "✅ ShokeDex development environment setup complete!"
echo ""
echo "📚 Quick Start Commands:"
echo "  - Initialize database: python src/data/manage_db.py init"
echo "  - Seed database (Gen 1-3): python src/data/manage_db.py seed --gen 1-3"
echo "  - Query Pokémon: python src/data/manage_db.py query --id 25"
echo "  - Run tests: python -m unittest discover tests -v"
echo "  - View database stats: python src/data/manage_db.py stats"
echo ""
echo "📖 Documentation:"
echo "  - README.md - Project overview and setup instructions"
echo "  - docs/database_schema.md - Database schema documentation"
echo "  - docs/data_loading_guide.md - Data loading instructions"
echo "  - docs/IMPLEMENTATION_SUMMARY.md - Implementation details"
echo ""
echo "Happy coding! 🎮✨"
