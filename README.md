# RFM Insights

RFM Insights is a web application for analyzing customer behavior using the RFM (Recency, Frequency, Monetary) model.

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher (for frontend development)
- Docker and Docker Compose (for production deployment)
- Nginx (for production deployment)
- PostgreSQL 14 or higher
- Domain names configured for app.rfminsights.com.br and api.rfminsights.com.br

## Pre-deployment Setup

### 1. Domain Configuration
1. Register your domains (if not already done)
2. Add DNS A records:
   ```
   app.rfminsights.com.br  → Your server IP
   api.rfminsights.com.br  → Your server IP
   ```
3. Wait for DNS propagation (can take up to 48 hours)

### 2. SSL Certificates
Option 1 - Using Let's Encrypt (Recommended):
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d app.rfminsights.com.br
sudo certbot certonly --standalone -d api.rfminsights.com.br

# Copy certificates
sudo cp /etc/letsencrypt/live/app.rfminsights.com.br/* nginx/ssl/
sudo cp /etc/letsencrypt/live/api.rfminsights.com.br/* nginx/ssl/
```

Option 2 - Using your own certificates:
- Place your .crt and .key files in the nginx/ssl/ directory
- Update paths in nginx configurations

### 3. Environment Setup

1. Frontend (.env):
```bash
# Required
REACT_APP_API_URL=https://api.rfminsights.com.br
REACT_APP_AUTH_DOMAIN=rfminsights.com.br
REACT_APP_AUTH_CLIENT_ID=your_auth_client_id

# Optional
REACT_APP_ENV=production
REACT_APP_API_TIMEOUT=30000
REACT_APP_ENABLE_ANALYTICS=true
```

2. Backend (.env):
```bash
# Required
DB_HOST=postgres
DB_PORT=5432
DB_NAME=rfm_db
DB_USER=rfm_user
DB_PASSWORD=strong_password
JWT_SECRET=your_secure_jwt_secret

# Optional
LOG_LEVEL=info
ENABLE_MONITORING=true
AWS_REGION=us-east-1
```

## Installation

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rfminsights.git
cd rfminsights
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Initialize the database:
```bash
cd api
source venv/bin/activate
python -c "from src.models.database import init_db; init_db()"
```

### Production Deployment

1. Prepare the server:
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create necessary directories
mkdir -p nginx/ssl logs/{frontend,backend}
```

2. Configure environment:
```bash
# Copy and edit environment files
cp app/.env.example app/.env
cp api/.env.example api/.env
nano app/.env
nano api/.env
```

3. Deploy using Docker:
```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

4. Verify deployment:
```bash
# Check frontend
curl -I https://app.rfminsights.com.br

# Check backend
curl -I https://api.rfminsights.com.br/health
```

## Troubleshooting

### Common Issues

1. Database Connection:
```bash
# Check database logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U rfm_user -d rfm_db
```

2. Nginx Configuration:
```bash
# Test nginx configuration
docker-compose exec web nginx -t

# Check nginx logs
docker-compose logs web
```

3. SSL Certificate Issues:
```bash
# Verify certificates
openssl x509 -in nginx/ssl/app.rfminsights.com.br.crt -text
openssl x509 -in nginx/ssl/api.rfminsights.com.br.crt -text
```

4. Permission Issues:
```bash
# Fix log permissions
sudo chown -R 1000:1000 logs/
sudo chmod -R 755 logs/
```

## Monitoring

### Log Locations
- Frontend: `logs/frontend/access.log` and `logs/frontend/error.log`
- Backend: `logs/backend/app.log` and `logs/backend/error.log`
- Nginx: `logs/nginx/access.log` and `logs/nginx/error.log`
- Database: View using `docker-compose logs postgres`

### Health Checks
- Frontend: https://app.rfminsights.com.br/health.html
- Backend: https://api.rfminsights.com.br/health
- Database: `docker-compose exec postgres pg_isready`

## Backup and Restore

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U rfm_user rfm_db > backup.sql

# Restore from backup
cat backup.sql | docker-compose exec -T postgres psql -U rfm_user -d rfm_db
```

### File Backup
```bash
# Backup uploaded files
tar -czf uploads_backup.tar.gz uploads/

# Backup logs
tar -czf logs_backup.tar.gz logs/
```

## Security

- All sensitive data must be stored in environment variables
- SSL certificates are required for production
- API endpoints are protected with JWT authentication
- CORS is configured to allow only specific origins
- Regular security updates:
  ```bash
  # Update containers
  docker-compose pull
  docker-compose up -d
  
  # Update system packages
  sudo apt update && sudo apt upgrade
  ```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 