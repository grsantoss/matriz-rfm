# RFM Insights - Deployment Verification Script

# Functions for colored output
function Write-Header {
    param([string]$text)
    Write-Host "`n===== $text =====" -ForegroundColor Green
}

function Write-Status {
    param([string]$text)
    Write-Host $text -ForegroundColor Yellow
}

function Write-Success {
    param([string]$text)
    Write-Host $text -ForegroundColor Green
}

function Write-Error {
    param([string]$text)
    Write-Host "ERROR: $text" -ForegroundColor Red
}

# Check if a container is running
function Test-Container {
    param([string]$containerName)
    
    $container = docker ps --format "{{.Names}}" | Where-Object { $_ -eq $containerName }
    return ($null -ne $container)
}

# Check if a port is open
function Test-Port {
    param(
        [string]$hostname,
        [int]$port
    )
    
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $connection = $tcp.BeginConnect($hostname, $port, $null, $null)
        $wait = $connection.AsyncWaitHandle.WaitOne(1000, $false)
        
        if ($wait) {
            $tcp.EndConnect($connection)
            $tcp.Close()
            return $true
        } else {
            $tcp.Close()
            return $false
        }
    } catch {
        return $false
    }
}

# Main verification process
Write-Header "RFM Insights - Deployment Verification"

# Check Docker and Docker Compose
Write-Header "Checking Docker"
try {
    $dockerVersion = docker --version
    Write-Success "Docker is installed: $dockerVersion"
} catch {
    Write-Error "Docker is not installed or not running."
    exit
}

# Check running containers
Write-Header "Checking Containers"

if (Test-Container "rfminsights-postgres") {
    Write-Success "PostgreSQL container is running"
} else {
    Write-Error "PostgreSQL container is not running"
}

if (Test-Container "rfminsights-api") {
    Write-Success "API container is running"
} else {
    Write-Error "API container is not running"
}

if (Test-Container "rfminsights-web") {
    Write-Success "Web container is running"
} else {
    Write-Error "Web container is not running"
}

# Check container logs for errors
Write-Header "Checking Container Logs"

Write-Status "Checking PostgreSQL logs..."
$pgLogs = docker logs rfminsights-postgres --tail 10 2>&1
if ($pgLogs -match "error|fatal|exception") {
    Write-Error "PostgreSQL container has errors:"
    Write-Host $pgLogs
} else {
    Write-Success "PostgreSQL logs look good"
}

Write-Status "Checking API logs..."
$apiLogs = docker logs rfminsights-api --tail 10 2>&1
if ($apiLogs -match "error|exception|fail") {
    Write-Error "API container has errors:"
    Write-Host $apiLogs
} else {
    Write-Success "API logs look good"
}

# Check ports
Write-Header "Checking Network Ports"

if (Test-Port "localhost" 80) {
    Write-Success "Web server is accessible on port 80"
} else {
    Write-Error "Web server is not accessible on port 80"
}

if (Test-Port "localhost" 8000) {
    Write-Success "API is accessible on port 8000"
} else {
    Write-Error "API is not accessible on port 8000"
}

if (Test-Port "localhost" 5433) {
    Write-Success "PostgreSQL is accessible on port 5433"
} else {
    Write-Error "PostgreSQL is not accessible on port 5433"
}

# Check API health endpoint
Write-Header "Checking API Health"
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Success "API health check successful: $($response.Content)"
    } else {
        Write-Error "API health check failed with status code: $($response.StatusCode)"
    }
} catch {
    Write-Error "API health check failed: $_"
}

# Final summary
Write-Header "Verification Summary"
Write-Host "The RFM Insights application should be accessible at:"
Write-Host "- Frontend: http://localhost"
Write-Host "- API: http://localhost:8000"
Write-Host ""
Write-Host "If you're still experiencing issues, check the detailed logs with:"
Write-Host "  docker-compose -f docker-compose-windows.yml logs"
Write-Host ""
Write-Host "To restart the services, run:"
Write-Host "  docker-compose -f docker-compose-windows.yml restart" 