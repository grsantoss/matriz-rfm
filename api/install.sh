#!/bin/bash

# Exit on error
set -e

echo "Installing backend dependencies..."

# Create necessary directories
mkdir -p src/routes src/controllers src/models logs

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created virtual environment"
fi

# Activate virtual environment
source venv/bin/activate

# Copy environment variables if they don't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template"
fi

# Install Python dependencies
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo "Installed Python dependencies"
fi

# Set proper permissions
chmod -R 755 src
chmod 644 .env
chmod -R 755 logs

# Create necessary files if they don't exist
touch logs/app.log
touch logs/error.log

# Set up logging
chmod 644 logs/app.log
chmod 644 logs/error.log

echo "Backend installation completed successfully!" 