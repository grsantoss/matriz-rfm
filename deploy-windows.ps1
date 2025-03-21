# RFM Insights Deployment Script for Windows
# This script handles the deployment of RFM Insights application with error checking and automatic fixes

# Enable error handling
$ErrorActionPreference = "Stop"

# Function to write colored output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Test-Command($Command) {
    try {
        Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Initialize-Environment {
    Write-ColorOutput Green "Initializing deployment environment..."
    
    # Create necessary directories
    $directories = @(
        "logs",
        "uploads",
        "alembic/versions",
        "backend/utils"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force
            Write-ColorOutput Yellow "Created directory: $dir"
        }
    }

    # Check and create .env file from template
    if (-not (Test-Path ".env") -and (Test-Path ".env.template")) {
        Copy-Item ".env.template" ".env"
        Write-ColorOutput Yellow "Created .env file from template. Please update with your settings."
    }
}

function Install-Prerequisites {
    Write-ColorOutput Green "Checking and installing prerequisites..."

    # Check Python installation
    if (-not (Test-Command "python")) {
        Write-ColorOutput Red "Python not found. Please install Python 3.8 or higher."
        exit 1
    }

    # Check pip installation
    if (-not (Test-Command "pip")) {
        Write-ColorOutput Red "pip not found. Please install pip."
        exit 1
    }

    # Check Docker installation
    if (-not (Test-Command "docker")) {
        Write-ColorOutput Red "Docker not found. Please install Docker Desktop for Windows."
        exit 1
    }

    # Check Docker Compose installation
    if (-not (Test-Command "docker-compose")) {
        Write-ColorOutput Red "Docker Compose not found. Please install Docker Compose."
        exit 1
    }

    # Install Python dependencies
    Write-ColorOutput Green "Installing Python dependencies..."
    try {
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    }
    catch {
        Write-ColorOutput Red "Failed to install Python dependencies: $_"
        exit 1
    }
}

function Initialize-Database {
    Write-ColorOutput Green "Initializing database..."

    try {
        # Run database migrations
        Write-ColorOutput Yellow "Running database migrations..."
        alembic upgrade head

        # Verify database connection
        Write-ColorOutput Yellow "Verifying database connection..."
        python -c "from backend.database import check_db_connection; check_db_connection()"
    }
    catch {
        Write-ColorOutput Red "Database initialization failed: $_"
        exit 1
    }
}

function Start-Application {
    Write-ColorOutput Green "Starting the application..."

    try {
        # Stop any existing containers
        docker-compose -f docker-compose-windows.yml down

        # Build and start containers
        docker-compose -f docker-compose-windows.yml up --build -d

        # Wait for services to be ready
        Start-Sleep -Seconds 10

        # Verify services are running
        $containers = docker ps --format "{{.Names}}"
        if (-not ($containers -match "rfm_insights")) {
            throw "Containers not running properly"
        }
    }
    catch {
        Write-ColorOutput Red "Failed to start application: $_"
        exit 1
    }
}

function Test-Deployment {
    Write-ColorOutput Green "Testing deployment..."

    try {
        # Run the verification script
        python scripts/verify_prerequisites.py

        # Test API endpoints
        $apiHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        if ($apiHealth.status -ne "ok") {
            throw "API health check failed"
        }

        # Test frontend
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost" -Method Get
        if ($frontendResponse.StatusCode -ne 200) {
            throw "Frontend health check failed"
        }
    }
    catch {
        Write-ColorOutput Red "Deployment verification failed: $_"
        Write-ColorOutput Yellow "Please check the logs for more details"
        exit 1
    }
}

function Show-DeploymentInfo {
    Write-ColorOutput Green "`nDeployment completed successfully!"
    Write-ColorOutput White "`nApplication URLs:"
    Write-ColorOutput Cyan "Frontend: http://localhost"
    Write-ColorOutput Cyan "API: http://localhost:8000"
    Write-ColorOutput Cyan "API Documentation: http://localhost:8000/docs"
    
    Write-ColorOutput White "`nDefault Admin Credentials:"
    Write-ColorOutput Yellow "Email: admin@rfminsights.com"
    Write-ColorOutput Yellow "Password: Please check your .env file for the default admin password"
    
    Write-ColorOutput White "`nImportant Notes:"
    Write-ColorOutput Yellow "1. Make sure to change the default admin password"
    Write-ColorOutput Yellow "2. Configure your environment variables in the .env file"
    Write-ColorOutput Yellow "3. Check the logs directory for any issues"
    Write-ColorOutput Yellow "4. Backup your database regularly"
}

# Main deployment process
try {
    Write-ColorOutput Cyan "`n=== RFM Insights Deployment Script ===`n"
    
    # Run deployment steps
    Initialize-Environment
    Install-Prerequisites
    Initialize-Database
    Start-Application
    Test-Deployment
    Show-DeploymentInfo
}
catch {
    Write-ColorOutput Red "`nDeployment failed with error: $_"
    Write-ColorOutput Yellow "Please fix the errors and try again"
    exit 1
} 