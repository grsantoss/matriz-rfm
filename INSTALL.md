# RFM Insights - Installation Guide

This guide provides step-by-step instructions for installing and setting up the RFM Insights project.

## Prerequisites

Before you begin, ensure you have the following installed:

- Docker (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- Git (version 2.30.0 or higher)
- A Unix-like operating system (Linux, macOS, or Windows with WSL2)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/rfm-insights.git
cd rfm-insights
```

### 2. Set Up Environment Variables

1. Copy the environment template file:
   ```bash
   cp .env.template .env
   ```

2. Edit the `.env` file with your configuration:
   ```bash
   # Database Configuration
   POSTGRES_USER=rfminsights
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_DB=rfminsights

   # JWT Configuration
   JWT_SECRET_KEY=your_jwt_secret_key

   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key

   # AWS Configuration (if using AWS services)
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_REGION=us-east-1
   ```

### 3. Create Required Directories

The deployment script will create these directories automatically, but you can create them manually if needed:

```bash
mkdir -p traefik logs analysis_history pdfs app/assets/js app/assets/css
```

### 4. Set Up SSL Certificates

1. Create the Traefik configuration directory:
   ```bash
   mkdir -p traefik
   ```

2. Create and set permissions for the ACME file:
   ```bash
   touch traefik/acme.json
   chmod 600 traefik/acme.json
   ```

### 5. Configure DNS

1. Point your domains to your server's IP address:
   - app.rfminsights.com.br
   - api.rfminsights.com.br
   - traefik.rfminsights.com.br

2. Wait for DNS propagation (can take up to 48 hours)

### 6. Run the Installation Script

```bash
chmod +x install.sh
./install.sh
```

The script will:
- Check for required dependencies
- Set up the environment
- Verify DNS configuration
- Start all services
- Verify the deployment

### 7. Verify Installation

After the installation is complete, verify that you can access:

- Frontend: https://app.rfminsights.com.br
- API: https://api.rfminsights.com.br
- Traefik Dashboard: https://traefik.rfminsights.com.br

## Development Setup

### Frontend Development

1. Navigate to the app directory:
   ```bash
   cd app
   ```

2. Install frontend dependencies (if using npm):
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Backend Development

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   alembic upgrade head
   ```

4. Start the development server:
   ```bash
   uvicorn backend.main:app --reload
   ```

## Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   sudo systemctl start docker
   ```

2. **Port conflicts**
   - Check if ports 80, 443, and 5433 are available
   - Stop any conflicting services

3. **SSL certificate issues**
   - Verify DNS configuration
   - Check Traefik logs: `docker compose logs traefik`
   - Ensure ports 80 and 443 are open on your firewall

4. **Database connection issues**
   - Verify PostgreSQL is running: `docker compose ps postgres`
   - Check database logs: `docker compose logs postgres`
   - Verify environment variables in `.env`

### Logs

View logs for specific services:

```bash
# All services
docker compose logs

# Specific service
docker compose logs api
docker compose logs web
docker compose logs postgres
docker compose logs traefik
```

## Maintenance

### Updating the Application

1. Pull the latest changes:
   ```bash
   git pull
   ```

2. Rebuild and restart services:
   ```bash
   docker compose up -d --build
   ```

### Backup

1. Database backup:
   ```bash
   docker compose exec postgres pg_dump -U rfminsights > backup.sql
   ```

2. Restore database:
   ```bash
   cat backup.sql | docker compose exec -T postgres psql -U rfminsights
   ```

## Security Considerations

1. Change default passwords in `.env`
2. Keep all dependencies updated
3. Regularly backup your data
4. Monitor logs for suspicious activity
5. Use strong passwords for all services

## Support

For support, please:
1. Check the documentation
2. Review the troubleshooting section
3. Open an issue on GitHub
4. Contact the development team

## License

This project is licensed under the MIT License - see the LICENSE file for details. 