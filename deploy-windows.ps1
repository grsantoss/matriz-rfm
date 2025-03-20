# RFM Insights - Windows Deployment Script

# Functions for colored output
function Write-Header {
    param([string]$text)
    Write-Host "`n===== $text =====" -ForegroundColor Green
}

function Write-Status {
    param([string]$text)
    Write-Host $text -ForegroundColor Yellow
}

function Write-Error {
    param([string]$text)
    Write-Host "ERROR: $text" -ForegroundColor Red
}

# Welcome message
Write-Header "RFM Insights - Deployment Script (Windows)"
Write-Host "This script will deploy the RFM Insights application with the following components:"
Write-Host "- PostgreSQL database"
Write-Host "- Python FastAPI backend"
Write-Host "- HTML/JS frontend"
Write-Host "- Nginx web server"
Write-Host ""
Write-Host "The application will be available at:"
Write-Host "- Frontend: http://localhost"
Write-Host "- API: http://localhost:8000"
Write-Host ""

# Confirm before proceeding
$continue = Read-Host "Do you want to continue? (y/n)"
if ($continue -ne "y") {
    Write-Host "Deployment canceled."
    exit
}

# Check for required tools
Write-Header "Checking requirements"

# Check for Docker
try {
    docker --version | Out-Null
    Write-Status "Docker is installed."
}
catch {
    Write-Error "Docker is not installed. Please install Docker Desktop for Windows first."
    exit
}

# Check for Docker Compose
try {
    docker-compose --version | Out-Null
    Write-Status "Docker Compose is installed."
}
catch {
    Write-Error "Docker Compose is not installed. Please install Docker Desktop for Windows first."
    exit
}

# Create required directories
Write-Header "Creating required directories"
New-Item -ItemType Directory -Force -Path nginx/ssl | Out-Null
New-Item -ItemType Directory -Force -Path logs | Out-Null
New-Item -ItemType Directory -Force -Path analysis_history | Out-Null
New-Item -ItemType Directory -Force -Path pdfs | Out-Null

# Create .env file if it doesn't exist
Write-Header "Setting up environment variables"
if (-not (Test-Path ".env")) {
    Write-Status "Creating .env file..."
    
    # Generate random password and JWT key
    $pgPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    $jwtKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    
    # Create .env file
    @"
# PostgreSQL Configuration
POSTGRES_USER=rfminsights
POSTGRES_PASSWORD=$pgPassword
POSTGRES_DB=rfminsights

# Application Configuration
DATABASE_URL=postgresql://rfminsights:$pgPassword@postgres:5432/rfminsights
JWT_SECRET_KEY=$jwtKey
PORT=8000

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# AWS Configuration (for email delivery)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
"@ | Out-File -FilePath ".env" -Encoding utf8
    
    Write-Status ".env file created with default values."
    Write-Host "Please update the following values in the .env file:"
    Write-Host "- OPENAI_API_KEY (for AI-powered insights)"
    Write-Host "- AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY (for email delivery)"
    
    $editEnv = Read-Host "Do you want to edit the .env file now? (y/n)"
    if ($editEnv -eq "y") {
        notepad .env
    }
}
else {
    Write-Status ".env file already exists."
}

# Update Nginx configuration for Windows (without SSL)
Write-Header "Updating Nginx configuration for Windows"
New-Item -ItemType Directory -Force -Path nginx | Out-Null

@"
server {
    listen 80;
    server_name localhost;
    
    # Serving static files
    root /usr/share/nginx/html;
    index index.html;
    
    # Main location
    location / {
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
    
    # Static assets - enable caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # Proxy API requests to the backend
    location /api/ {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://api:8000/health;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
"@ | Out-File -FilePath "nginx/nginx.conf" -Encoding utf8

# Update docker-compose.yml for Windows
Write-Header "Updating Docker Compose configuration for Windows"
@"
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    container_name: rfminsights-postgres
    restart: always
    environment:
      POSTGRES_USER: \${POSTGRES_USER:-rfminsights}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD:-rfminsights}
      POSTGRES_DB: \${POSTGRES_DB:-rfminsights}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"  # Mapped to a different port to avoid conflicts
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rfminsights"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: rfminsights-api
    restart: always
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://\${POSTGRES_USER:-rfminsights}:\${POSTGRES_PASSWORD:-rfminsights}@postgres:5432/\${POSTGRES_DB:-rfminsights}
      - JWT_SECRET_KEY=\${JWT_SECRET_KEY}
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
      - AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=\${AWS_REGION:-us-east-1}
      - PORT=8000
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./analysis_history:/app/analysis_history
      - ./pdfs:/app/pdfs

  # Nginx Frontend
  web:
    image: nginx:alpine
    container_name: rfminsights-web
    restart: always
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - api

volumes:
  postgres_data:
"@ | Out-File -FilePath "docker-compose-windows.yml" -Encoding utf8

# Build and start services
Write-Header "Starting services"
Write-Status "Building and starting containers..."
docker-compose -f docker-compose-windows.yml up -d postgres

# Wait for PostgreSQL to be ready
Write-Status "Waiting for PostgreSQL to be ready..."
Start-Sleep -Seconds 10

# Initialize the database and start the API
Write-Status "Initializing the database and starting the API..."
docker-compose -f docker-compose-windows.yml up -d api

# Wait for API to be ready
Write-Status "Waiting for API to be ready..."
Start-Sleep -Seconds 10

# Start web server
Write-Status "Starting web server..."
docker-compose -f docker-compose-windows.yml up -d web

# Success message
Write-Header "Deployment completed successfully"
Write-Host "The RFM Insights application is now available at:"
Write-Host "- Frontend: http://localhost"
Write-Host "- API: http://localhost:8000"
Write-Host ""
Write-Host "To view the logs, run:"
Write-Host "  docker-compose -f docker-compose-windows.yml logs -f"
Write-Host ""
Write-Host "To stop the services, run:"
Write-Host "  docker-compose -f docker-compose-windows.yml down"
Write-Host ""
Write-Host "If you encounter any issues, please check the logs in the logs/ directory." 