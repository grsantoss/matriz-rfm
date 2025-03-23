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
    exit 1
}

# Function to check if dependencies are installed
check_dependencies() {
    print_header "Checking Dependencies"
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
    else
        print_success "Docker is installed."
    fi
    
    # Check if docker compose is installed
    if ! command -v docker compose &> /dev/null; then
        if ! command -v docker-compose &> /dev/null; then
            print_error "Docker Compose is not installed. Please install Docker Compose first."
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
    else
        print_success "Docker daemon is running."
    fi
}

# Function to create required directories and files
setup_environment() {
    print_header "Setting Up Environment"
    
    # Create required directories
    local dirs=("traefik" "logs" "analysis_history" "pdfs" "app/assets/js" "app/assets/css")
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
    
    # Create traefik.yml if it doesn't exist
    if [ ! -f "./traefik/traefik.yml" ]; then
        cat > ./traefik/traefik.yml << 'EOL'
# Traefik Global Configuration
api:
  dashboard: true

# Docker Provider Configuration
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: rfm_network
  file:
    directory: "/etc/traefik/dynamic"
    watch: true

# Entrypoints Configuration
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true
  websecure:
    address: ":443"

# Certificate Resolvers Configuration
certificatesResolvers:
  letsencrypt:
    acme:
      email: "admin@rfminsights.com.br"
      storage: "/acme.json"
      httpChallenge:
        entryPoint: web

# Log Configuration
log:
  level: INFO

# Access Logs Configuration
accessLog:
  filePath: "/var/log/traefik/access.log"
  format: json
  bufferingSize: 100
EOL
        print_success "Created traefik.yml"
    fi
    
    # Create and set permissions for acme.json
    if [ ! -f "./traefik/acme.json" ]; then
        touch ./traefik/acme.json
        chmod 600 ./traefik/acme.json
        print_success "Created acme.json with proper permissions"
    fi
    
    # Create nginx.conf if it doesn't exist
    if [ ! -f "./nginx/nginx.conf" ]; then
        cat > ./nginx/nginx.conf << 'EOL'
server {
    listen 80;
    server_name localhost;
    server_tokens off;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval';" always;

    # Route all requests to frontend files
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Cache settings for static content
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|eot)$ {
        root /usr/share/nginx/html;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        access_log off;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 'healthy\n';
    }

    # Deny access to .htaccess files
    location ~ /\.ht {
        deny all;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}
EOL
        print_success "Created nginx.conf"
    fi
    
    # Check if .env file exists, create it from template if not
    if [ ! -f ".env" ] && [ -f ".env.template" ]; then
        cp .env.template .env
        print_warning "Created .env file from template. Please update it with your configuration."
        print_warning "Press Enter to continue after updating .env, or Ctrl+C to abort..."
        read
    elif [ ! -f ".env" ]; then
        print_error "No .env file or template found. Please create one with required configuration."
    else
        print_success "Found existing .env file"
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
    print_success "Pulled the latest Docker images"
    
    # Start all services
    docker compose up -d
    print_success "Started all services"
    
    # Wait for services to be ready
    echo "Waiting for services to initialize..."
    sleep 10
    
    # Check if containers are running
    if [ "$(docker compose ps -q | wc -l)" -lt 4 ]; then
        print_error "Not all containers are running. Check logs with 'docker compose logs'"
    else
        print_success "All containers are running"
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
        print_error "Traefik is not running. Check logs with 'docker compose logs traefik'"
    else
        print_success "Traefik is running"
    fi
    
    # Check if web service is running
    if ! docker compose ps web | grep -q "Up"; then
        print_error "Web service is not running. Check logs with 'docker compose logs web'"
    else
        print_success "Web service is running"
    fi
    
    # Check if API service is running
    if ! docker compose ps api | grep -q "Up"; then
        print_error "API service is not running. Check logs with 'docker compose logs api'"
    else
        print_success "API service is running"
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
}

# Main deployment process
main() {
    print_header "Starting RFM Insights Deployment"
    
    # Check dependencies
    check_dependencies
    
    # Setup environment
    setup_environment
    
    # Check DNS configuration
    check_dns
    
    # Start services
    start_services
    
    # Verify deployment
    verify_deployment
    
    print_header "Deployment Complete"
    print_success "RFM Insights has been deployed successfully!"
    print_success "Frontend: https://app.rfminsights.com.br"
    print_success "API: https://api.rfminsights.com.br"
    print_success "Traefik Dashboard: https://traefik.rfminsights.com.br"
}

# Run main function
main 