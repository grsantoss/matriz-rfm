#!/bin/bash
# RFM Insights - Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colorful headers
print_header() {
    echo -e "${BLUE}===== $1 =====${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if dependencies are installed
check_dependencies() {
    print_header "Checking Dependencies"
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    else
        print_success "Docker is installed."
    fi
    
    # Check if docker compose is installed
    if ! command -v docker compose &> /dev/null; then
        if ! command -v docker-compose &> /dev/null; then
            print_error "Docker Compose is not installed. Please install Docker Compose first."
            exit 1
        else
            print_warning "Using deprecated docker-compose. Consider upgrading to Docker Compose V2."
            # Create alias for backward compatibility
            alias "docker compose"="docker-compose"
        fi
    else
        print_success "Docker Compose is installed."
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker service."
        exit 1
    else
        print_success "Docker daemon is running."
    fi
}

# Function to create required directories and files
setup_environment() {
    print_header "Setting Up Environment"
    
    # Create traefik directory if it doesn't exist
    if [ ! -d "./traefik" ]; then
        mkdir -p ./traefik
        print_success "Created traefik directory."
    fi
    
    # Create other required directories
    mkdir -p logs analysis_history pdfs frontend nginx
    print_success "Created application directories."
    
    # Create traefik.yml if it doesn't exist
    if [ ! -f "./traefik/traefik.yml" ]; then
        print_warning "traefik.yml file not found. This should have been created already."
    fi
    
    # Create and set permissions for acme.json
    if [ ! -f "./traefik/acme.json" ]; then
        touch ./traefik/acme.json
        chmod 600 ./traefik/acme.json
        print_success "Created acme.json with proper permissions."
    else
        # Ensure acme.json has the correct permissions
        chmod 600 ./traefik/acme.json
        print_success "Updated acme.json permissions."
    fi
    
    # Check if nginx.conf exists
    if [ ! -d "./nginx" ]; then
        mkdir -p ./nginx
    fi
    
    if [ ! -f "./nginx/nginx.conf" ]; then
        print_warning "nginx.conf file not found. This should have been created already."
    fi
    
    # Check if .env file exists, create it from template if not
    if [ ! -f ".env" ] && [ -f ".env.template" ]; then
        cp .env.template .env
        print_warning "Created .env file from template. Please update it with your configuration."
        print_warning "Press Enter to continue after updating .env, or Ctrl+C to abort..."
        read
    elif [ ! -f ".env" ]; then
        print_warning "No .env file or template found. Creating a basic .env file."
        cat > .env <<EOL
# Database Configuration
POSTGRES_USER=rfminsights
POSTGRES_PASSWORD=changeme
POSTGRES_DB=rfminsights

# API Configuration
JWT_SECRET_KEY=change_this_to_a_secure_random_string
OPENAI_API_KEY=your_openai_api_key

# AWS Configuration (if needed)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
EOL
        print_warning "Created basic .env file. Please update it with your configuration."
        print_warning "Press Enter to continue after updating .env, or Ctrl+C to abort..."
        read
    else
        print_success "Found existing .env file."
    fi
}

# Function to check DNS settings
check_dns() {
    print_header "Checking DNS Configuration"
    
    # Get server's public IP
    SERVER_IP=$(curl -s https://ipinfo.io/ip || curl -s https://api.ipify.org)
    
    if [ -z "$SERVER_IP" ]; then
        print_warning "Could not determine server IP address. DNS check will be skipped."
        return
    fi
    
    print_success "Server IP address: $SERVER_IP"
    
    # Check DNS for app domain
    echo "Checking app.rfminsights.com.br DNS..."
    APP_IP=$(dig +short app.rfminsights.com.br A || host -t A app.rfminsights.com.br | grep "has address" | cut -d' ' -f4)
    
    if [ -z "$APP_IP" ]; then
        print_warning "Could not resolve app.rfminsights.com.br. Make sure DNS is configured correctly."
    elif [ "$APP_IP" != "$SERVER_IP" ]; then
        print_warning "app.rfminsights.com.br points to $APP_IP, but your server IP is $SERVER_IP"
        print_warning "SSL certificate generation might fail if DNS is not properly configured."
    else
        print_success "app.rfminsights.com.br correctly points to $SERVER_IP"
    fi
    
    # Check DNS for API domain
    echo "Checking api.rfminsights.com.br DNS..."
    API_IP=$(dig +short api.rfminsights.com.br A || host -t A api.rfminsights.com.br | grep "has address" | cut -d' ' -f4)
    
    if [ -z "$API_IP" ]; then
        print_warning "Could not resolve api.rfminsights.com.br. Make sure DNS is configured correctly."
    elif [ "$API_IP" != "$SERVER_IP" ]; then
        print_warning "api.rfminsights.com.br points to $API_IP, but your server IP is $SERVER_IP"
        print_warning "SSL certificate generation might fail if DNS is not properly configured."
    else
        print_success "api.rfminsights.com.br correctly points to $SERVER_IP"
    fi
}

# Function to start services
start_services() {
    print_header "Starting Services"
    
    # Pull the latest images
    docker compose pull
    print_success "Pulled the latest Docker images."
    
    # Start all services
    docker compose up -d
    print_success "Started all services."
    
    # Wait for services to be ready
    echo "Waiting for services to initialize..."
    sleep 10
    
    # Check if containers are running
    if [ "$(docker compose ps -q | wc -l)" -lt 3 ]; then
        print_error "Not all containers are running. Check logs with 'docker compose logs'."
    else
        print_success "All containers are running."
    fi
}

# Function to verify services and SSL
verify_deployment() {
    print_header "Verifying Deployment"
    
    # Wait for Traefik to obtain certificates
    echo "Waiting for SSL certificates to be obtained..."
    sleep 30
    
    # Check if Traefik is running
    if ! docker compose ps traefik | grep -q "Up"; then
        print_error "Traefik is not running. Check logs with 'docker compose logs traefik'."
        return 1
    else
        print_success "Traefik is running."
    fi
    
    # Check if web service is running
    if ! docker compose ps web | grep -q "Up"; then
        print_error "Web service is not running. Check logs with 'docker compose logs web'."
        return 1
    else
        print_success "Web service is running."
    fi
    
    # Check if API service is running
    if ! docker compose ps api | grep -q "Up"; then
        print_error "API service is not running. Check logs with 'docker compose logs api'."
        return 1
    else
        print_success "API service is running."
    fi
    
    # Check if HTTPS is working for app domain
    echo "Checking HTTPS for app.rfminsights.com.br..."
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://app.rfminsights.com.br/ | grep -q "200\|301\|302"; then
        print_success "HTTPS is working for app.rfminsights.com.br"
    else
        print_warning "Could not connect to https://app.rfminsights.com.br"
        print_warning "SSL certificate might not be ready yet, or there might be network issues."
    fi
    
    # Check if HTTPS is working for API domain
    echo "Checking HTTPS for api.rfminsights.com.br..."
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://api.rfminsights.com.br/ | grep -q "200\|301\|302\|404"; then
        print_success "HTTPS is working for api.rfminsights.com.br"
    else
        print_warning "Could not connect to https://api.rfminsights.com.br"
        print_warning "SSL certificate might not be ready yet, or there might be network issues."
    fi
    
    # Check acme.json for certificates
    if grep -q "Certificate" ./traefik/acme.json; then
        print_success "SSL certificates have been issued."
    else
        print_warning "SSL certificates might not be issued yet. Check 'docker compose logs traefik' for details."
    fi
    
    return 0
}

# Function to display deployment summary
deployment_summary() {
    print_header "Deployment Summary"
    
    echo -e "${BLUE}RFM Insights application is now deployed with Traefik!${NC}"
    echo ""
    echo -e "${GREEN}Frontend:${NC} https://app.rfminsights.com.br"
    echo -e "${GREEN}API:${NC} https://api.rfminsights.com.br"
    echo -e "${GREEN}Traefik Dashboard:${NC} https://traefik.rfminsights.com.br (protected with Basic Auth)"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo "  - View logs: docker compose logs"
    echo "  - Service-specific logs: docker compose logs [service]"
    echo "  - Restart all services: docker compose restart"
    echo "  - Stop all services: docker compose down"
    echo "  - Update and redeploy: ./deploy.sh"
    echo ""
    echo -e "${YELLOW}Note:${NC} If you encounter any issues, check the logs and ensure your DNS is correctly configured."
}

# Main deployment process
main() {
    print_header "RFM Insights Deployment"
    
    # Execute deployment steps
    check_dependencies
    setup_environment
    check_dns
    start_services
    
    # Verify deployment
    if verify_deployment; then
        deployment_summary
        print_success "Deployment completed successfully!"
        exit 0
    else
        print_error "Deployment failed. Please check the logs for errors."
        exit 1
    fi
}

# Execute main function
main 