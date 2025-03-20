#!/bin/bash

# Exit on error
set -e

echo "Installing frontend dependencies..."

# Create necessary directories
mkdir -p assets/css assets/js

# Copy environment variables if they don't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template"
fi

# Install dependencies (if using npm)
if [ -f package.json ]; then
    npm install
fi

# Set proper permissions
chmod -R 755 assets
chmod 644 .env

echo "Frontend installation completed successfully!" 