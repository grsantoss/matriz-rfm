#!/bin/bash

# Exit on error
set -e

echo "Starting RFM Insights installation..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run this script as root"
    exit 1
fi

# Create necessary directories
mkdir -p app/assets/{css,js} api/src/{routes,controllers,models} api/logs

# Install frontend
echo "Installing frontend..."
cd app
chmod +x install.sh
./install.sh
cd ..

# Install backend
echo "Installing backend..."
cd api
chmod +x install.sh
./install.sh
cd ..

# Create nginx configuration directory if it doesn't exist
mkdir -p nginx/conf.d

# Copy nginx configurations if they don't exist
if [ ! -f nginx/conf.d/frontend.conf ]; then
    cp app/nginx.conf nginx/conf.d/frontend.conf
fi

if [ ! -f nginx/conf.d/backend.conf ]; then
    cp api/nginx.conf nginx/conf.d/backend.conf
fi

# Set up SSL directory
mkdir -p nginx/ssl

# Create necessary directories for logs
mkdir -p logs/{frontend,backend}

# Set proper permissions
chmod -R 755 app/assets
chmod -R 755 api/src
chmod -R 755 logs
chmod 644 app/.env
chmod 644 api/.env

echo "RFM Insights installation completed successfully!"
echo "Please configure your environment variables in:"
echo "1. app/.env"
echo "2. api/.env"
echo ""
echo "Next steps:"
echo "1. Configure your SSL certificates in nginx/ssl/"
echo "2. Update your DNS records for app.rfminsights.com.br and api.rfminsights.com.br"
echo "3. Start the services using docker-compose up -d" 