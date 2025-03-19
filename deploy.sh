#!/bin/bash
# RFM Insights - Deployment Script

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print section header
print_header() {
    echo -e "\n${GREEN}==== $1 ====${NC}\n"
}

# Print status message
print_status() {
    echo -e "${YELLOW}$1${NC}"
}

# Print error message
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (or with sudo)"
    exit 1
fi

# Welcome message
print_header "RFM Insights - Deployment Script"
echo "This script will deploy the RFM Insights application with the following components:"
echo "- PostgreSQL database"
echo "- Python FastAPI backend"
echo "- HTML/JS frontend"
echo "- Nginx web server with SSL"
echo ""
echo "The application will be available at:"
echo "- Frontend: https://app.rfminsights.com.br"
echo "- API: https://api.rfminsights.com.br"
echo ""

# Confirm before proceeding
read -p "Do you want to continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment canceled."
    exit 0
fi

# Check for required tools
print_header "Checking requirements"

# Check for Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_status "Docker is installed."

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_status "Docker Compose is installed."

# Check DNS records
print_header "Checking DNS records"
print_status "Checking if app.rfminsights.com.br resolves to this server..."
SERVER_IP=$(curl -s http://ifconfig.me)
APP_DNS=$(dig +short app.rfminsights.com.br A)

if [ -z "$APP_DNS" ]; then
    print_error "The domain app.rfminsights.com.br does not have an A record."
    echo "Please add an A record pointing to $SERVER_IP and try again."
    exit 1
elif [ "$APP_DNS" != "$SERVER_IP" ]; then
    echo "Warning: app.rfminsights.com.br resolves to $APP_DNS, but this server's IP is $SERVER_IP"
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment canceled."
        exit 0
    fi
else
    print_status "DNS record for app.rfminsights.com.br is correctly set to $SERVER_IP"
fi

print_status "Checking if api.rfminsights.com.br resolves to this server..."
API_DNS=$(dig +short api.rfminsights.com.br A)

if [ -z "$API_DNS" ]; then
    print_error "The domain api.rfminsights.com.br does not have an A record."
    echo "Please add an A record pointing to $SERVER_IP and try again."
    exit 1
elif [ "$API_DNS" != "$SERVER_IP" ]; then
    echo "Warning: api.rfminsights.com.br resolves to $API_DNS, but this server's IP is $SERVER_IP"
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment canceled."
        exit 0
    fi
else
    print_status "DNS record for api.rfminsights.com.br is correctly set to $SERVER_IP"
fi

# Create required directories
print_header "Creating required directories"
mkdir -p nginx/ssl
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p logs
mkdir -p analysis_history
mkdir -p pdfs

# Create .env file if it doesn't exist
print_header "Setting up environment variables"
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# PostgreSQL Configuration
POSTGRES_USER=rfminsights
POSTGRES_PASSWORD=$(openssl rand -base64 12)
POSTGRES_DB=rfminsights

# Application Configuration
DATABASE_URL=postgresql://rfminsights:${POSTGRES_PASSWORD}@postgres:5432/rfminsights
JWT_SECRET_KEY=$(openssl rand -base64 32)
PORT=8000

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# AWS Configuration (for email delivery)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
EOF
    print_status ".env file created with default values."
    echo "Please update the following values in the .env file:"
    echo "- OPENAI_API_KEY (for AI-powered insights)"
    echo "- AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY (for email delivery)"
    
    read -p "Do you want to edit the .env file now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    print_status ".env file already exists."
fi

# Load environment variables
set -a
source .env
set +a

# Start the services
print_header "Starting services"
print_status "Building and starting containers..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
sleep 10

# Initialize the database
print_status "Initializing the database..."
docker-compose up -d api

# Wait for API to be ready
print_status "Waiting for API to be ready..."
sleep 10

# Start web server
print_status "Starting web server..."
docker-compose up -d web

# Initialize SSL certificates with Let's Encrypt
print_header "Setting up SSL certificates"
print_status "Obtaining SSL certificates from Let's Encrypt..."
docker-compose up certbot

# Success message
print_header "Deployment completed successfully"
echo "The RFM Insights application is now available at:"
echo "- Frontend: https://app.rfminsights.com.br"
echo "- API: https://api.rfminsights.com.br"
echo ""
echo "To view the logs, run:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the services, run:"
echo "  docker-compose down"
echo ""
echo "If you encounter any issues, please check the logs in the logs/ directory." 